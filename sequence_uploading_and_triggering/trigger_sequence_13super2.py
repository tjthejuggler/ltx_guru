import socket
import random
import time
import sys
from datetime import datetime

# --- Configuration ---
BALL_IP = "192.168.40.133"  # VERIFY THIS IS STILL THE BALL'S CURRENT IP
PC_IP = ""
BROADCAST_ADDR = "255.255.255.255"
UDP_PORT = 41412

KNOWN_PLAY_NONCES = {
    # Fill with known good OpID: (Nonce1, Nonce2) pairs if you have them
    # 0x14: (0xAB, 0xCD),
}
# --- End Configuration ---

def log_print(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    print(f"[{timestamp}] {message}")
    sys.stdout.flush()

def sniff_ball_udp_status():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind((PC_IP, UDP_PORT))
    except OSError as e:
        log_print(f"Error binding sniff socket: {e}.")
        return None, None, None, None
    
    sock.settimeout(7)
    log_print(f"Sniffing for ball's UDP broadcast (from {BALL_IP} on port {UDP_PORT})... ")
    try:
        while True: 
            data, addr = sock.recvfrom(1024)
            if addr[0] == BALL_IP:
                packet_len = len(data)
                hex_data = data.hex()
                
                ball_status_from_packet = None
                sniffed_cmd_byte2_val = None # This will be logged but NOT used for sending
                ts_b3, ts_b4 = None, None

                if packet_len >= 17: # Basic check for minimum expected length
                    # Universal timestamp location for both 47 and 62 byte packets observed so far
                    ts_b3 = data[15] 
                    ts_b4 = data[16]

                    if packet_len == 47:
                        # Beacon: DevID(4) + zeros(8) + status(1) + TS_part1(2) + ts_b3(1) + ts_b4(1)
                        # Indices: [0:3]    [4:11]      [12]        [13:14]       [15]      [16]
                        ball_status_from_packet = data[12] 
                        sniffed_cmd_byte2_val = data[10] # Should be 0x00 from zero block
                        log_print(f"OK (47-byte beacon). Sniffed Status: {ball_status_from_packet:02x}, "
                                  f"SniffedCmdByte2Val: {sniffed_cmd_byte2_val:02x}, "
                                  f"Sniffed_TS_B3,4: {ts_b3:02x}{ts_b4:02x}. Payload: {hex_data}")
                    elif packet_len == 62:
                        # Active Status Packet (assuming the structure from PC app interaction)
                        # Original: MAC(4) + unknown(5) + field9(1) + cmd_byte2_src(1) + status_counter(1) + status(1) + timestamp(4)
                        # Indices: [0:3]    [4:8]         [9]         [10]                [11]              [12]        [13:16]
                        ball_status_from_packet = data[12]
                        sniffed_cmd_byte2_val = data[10] 
                        # ts_b3, ts_b4 already parsed from data[15], data[16]
                        log_print(f"OK (62-byte status). Sniffed Status: {ball_status_from_packet:02x}, "
                                  f"SniffedCmdByte2Val: {sniffed_cmd_byte2_val:02x}, "
                                  f"Sniffed_TS_B3,4: {ts_b3:02x}{ts_b4:02x}. Payload: {hex_data}")
                    else:
                        log_print(f"INFO: Received packet of unexpected length {packet_len} from {addr}. Data: {hex_data}. Assuming TS at [15][16] might be okay if >17 bytes.")
                        # Fallback if length is weird but >=17, still try to get a timestamp
                        ball_status_from_packet = data[12] if packet_len > 12 else 0xEE # Error status
                        sniffed_cmd_byte2_val = data[10] if packet_len > 10 else 0xEE   # Error val
                    
                    return ball_status_from_packet, sniffed_cmd_byte2_val, ts_b3, ts_b4
    except socket.timeout:
        log_print("FAIL. Sniffing timed out.")
        return None, None, None, None
    except Exception as e:
        log_print(f"Error during sniffing: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None, None
    finally:
        sock.close()

def trigger_play_sequence(play_op_id_byte, pc_nonce_byte1, pc_nonce_byte2):
    log_print(f"Attempting to trigger PLAY (OpID {play_op_id_byte:02x})")
    _, _, ts_b3, ts_b4 = sniff_ball_udp_status() 
    
    if ts_b3 is None or ts_b4 is None:
        log_print("Sniff failed to get timestamp for PLAY. Aborting.")
        return False
    
    command_group = 0x61
    command_byte2_to_use = 0x01  # <<<< KEY CHANGE: ALWAYS USE 0x01 FOR SENDING
    
    payload = bytes([
        command_group, play_op_id_byte, command_byte2_to_use, 0x00, 0x00,
        pc_nonce_byte1, pc_nonce_byte2, ts_b3, ts_b4
    ])
    log_print(f"Sending Play Command (OpID {play_op_id_byte:02x}, SentCmdByte2 {command_byte2_to_use:02x}, Echoed_TS {ts_b3:02x}{ts_b4:02x}). Payload: {payload.hex()}")
    
    send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    send_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    try:
        send_sock.sendto(payload, (BROADCAST_ADDR, UDP_PORT))
        log_print("Play command sent.")
        return True
    except Exception as e:
        log_print(f"Error sending Play command: {e}")
        return False
    finally:
        send_sock.close()

def stop_play_sequence(stop_op_id_byte):
    log_print(f"Attempting to trigger STOP (OpID {stop_op_id_byte:02x})")
    # Sniff primarily for timestamp for potential future use, or if stop needs it
    # but current v13.1 stop command does not echo TS.
    ball_status_ignored, sniffed_cmd_byte2_ignored, ts_b3_ignored, ts_b4_ignored = sniff_ball_udp_status()
    
    if ball_status_ignored is None: # If sniff failed completely
         log_print("Sniff failed before STOP. Aborting stop command (or could try sending blind).")
         return False # Or, you could choose to try sending without a fresh sniff

    command_group = 0x61
    command_byte2_to_use = 0x01  # <<<< KEY CHANGE: ALWAYS USE 0x01 FOR SENDING

    payload = bytes([
        command_group, stop_op_id_byte, command_byte2_to_use, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00 # v13.1 stop payload (no TS echo)
    ])
    log_print(f"Sending Stop Command (OpID {stop_op_id_byte:02x}, SentCmdByte2 {command_byte2_to_use:02x}). Payload: {payload.hex()}")
    
    send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    send_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    try:
        send_sock.sendto(payload, (BROADCAST_ADDR, UDP_PORT))
        log_print("Stop command sent.")
        return True
    except Exception as e:
        log_print(f"Error sending Stop command: {e}")
        return False
    finally:
        send_sock.close()

if __name__ == "__main__":
    script_version = "v15.0_HardcodedCmdByte2_FeedbackTS"
    log_print(f"LED Juggling Ball Interactive Control ({script_version})")
    log_print("--------------------------------------------------------------------------------")
    log_print(f"Target Ball IP: {BALL_IP}, UDP Port: {UDP_PORT}")
    log_print(f"PC IP for sniffing: '{PC_IP}' (blank means all available).")
    log_print("Press 'p' to play, 's' to stop, 'q' to quit.")

    op_id_for_next_play = 0x14 
    op_id_of_playing_sequence = 0x00 
    is_playing_assumed = False
    feedback_log = []

    try:
        while True:
            action_input_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            action_prompt_msg = f"[{action_input_time}] Enter command (p/s/q) [Next PlayOp: {op_id_for_next_play:02x}]: "
            action = input(f"\n{action_prompt_msg}").lower()

            if action == 'p':
                # ... (play logic from previous script, calling trigger_play_sequence)
                if is_playing_assumed:
                    log_print("Script assumes ball is already playing. Send 's' to stop first.")
                    continue
                
                play_op_to_send = op_id_for_next_play
                p1, p2 = KNOWN_PLAY_NONCES.get(play_op_to_send, 
                                               (random.randint(1, 254), random.randint(1, 254)))
                if play_op_to_send not in KNOWN_PLAY_NONCES:
                    log_print(f"Using RANDOM nonce P1=0x{p1:02x}, P2=0x{p2:02x} for Op ID {play_op_to_send:02x}.")
                else:
                    log_print(f"Using KNOWN nonce P1=0x{p1:02x}, P2=0x{p2:02x} for Op ID {play_op_to_send:02x}.")

                play_successful_send = trigger_play_sequence(play_op_to_send, p1, p2)
                
                if play_successful_send:
                    op_id_of_playing_sequence = play_op_to_send 
                    is_playing_assumed = True # Assume it will play for now
                    log_print("OBSERVE BALL: Did it play or show red LED?")
                    feedback = input("    Did play work (y/n/r=red_led)? ").lower()
                    feedback_log.append(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}] PLAY OpID {play_op_to_send:02x} Feedback: {feedback}")
                    if feedback == 'n' or feedback == 'r':
                        is_playing_assumed = False 
                else:
                    log_print("Play command send FAILED or aborted. Ball state unknown.")
                    feedback_log.append(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}] PLAY OpID {play_op_to_send:02x} Feedback: send_aborted")


            elif action == 's':
                # ... (stop logic from previous script, calling stop_play_sequence)
                if not is_playing_assumed: # if we think it's already stopped
                    # Ask if user wants to send a stop anyway, as the ball might be in a desynced state
                    force_stop = input("    Script thinks ball is stopped. Force send stop (y/n)? ").lower()
                    if force_stop != 'y':
                        continue
                    # If forcing, we don't have an op_id_of_playing_sequence.
                    # We could try sending a generic stop (e.g., with current next_play_op + 0A, or a common one like 0x1E)
                    # For now, let's just use the last known op_id_of_playing_sequence + 0A, even if it's old.
                    # Or perhaps a fixed "emergency stop" OpID if we discover one.
                    log_print(f"Attempting to force stop. Last known playing OpID was {op_id_of_playing_sequence:02x}.")
                
                current_stop_op_id = (op_id_of_playing_sequence + 0x0A) & 0xFF 
                
                stop_successful_send = stop_play_sequence(current_stop_op_id)
                
                if stop_successful_send:
                    is_playing_assumed_after_send = False # Temporarily assume stop worked
                    log_print(f"OBSERVE BALL: Did it stop? Next Play Op ID will be 0x{op_id_for_next_play:02x}")
                    feedback = input("    Did stop work (y/n)? ").lower()
                    feedback_log.append(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}] STOP OpID {current_stop_op_id:02x} Feedback: {feedback}")
                    if feedback == 'n':
                        is_playing_assumed_after_send = True # It didn't actually stop
                    
                    is_playing_assumed = is_playing_assumed_after_send
                    if not is_playing_assumed: # if stop actually worked
                        op_id_for_next_play = (op_id_of_playing_sequence + 0x14) & 0xFF
                        if op_id_for_next_play == 0x00: 
                            op_id_for_next_play = 0x14
                        log_print(f"Stop confirmed. Next Play Op ID updated to 0x{op_id_for_next_play:02x}")
                else:
                    log_print("Stop command send FAILED or aborted. Ball state unknown.")
                    feedback_log.append(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}] STOP OpID {current_stop_op_id:02x} Feedback: send_aborted")

            elif action == 'q':
                log_print("Exiting.")
                break
            else:
                log_print("Invalid command. Use 'p', 's', or 'q'.")
    
    except KeyboardInterrupt:
        log_print("\nExiting due to Ctrl-C.")
    except Exception as e:
        log_print(f"\nAn unexpected error occurred in the main loop: {e}")
        import traceback
        traceback.print_exc()
    finally:
        log_print("--- Feedback Log ---")
        for entry in feedback_log:
            print(entry) 
        log_print("--- Control Script Finished ---")