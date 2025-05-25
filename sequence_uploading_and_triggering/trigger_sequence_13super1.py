import socket
import random
import time
import sys
from datetime import datetime # For timestamped logs

# --- Configuration ---
BALL_IP = "192.168.40.205"
PC_IP = ""  # Leave blank to bind to all interfaces for sniffing
BROADCAST_ADDR = "255.255.255.255"
UDP_PORT = 41412

# --- Constants for Command Construction ---
COMMAND_BYTE2_FOR_CONTROL = 0x01 # Using 0x01 for the third command byte

# --- End Configuration ---

def log_print(message):
    """Prints a message with a timestamp."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    print(f"[{timestamp}] {message}")
    sys.stdout.flush()

def sniff_ball_udp_data_for_playstop():
    # Returns: ball_status_d12, ts_b3, ts_b4, sniffed_d10, packet_len_sniffed
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind((PC_IP, UDP_PORT))
    except OSError as e:
        log_print(f"Error binding sniff socket: {e}. Make sure no other script is bound to this port.")
        return None, None, None, None, 0 # 0 for packet_len_sniffed indicates total failure
    
    sock.settimeout(7) 

    log_print(f"Sniffing for ball's UDP broadcast (from {BALL_IP} on port {UDP_PORT})... ")
    try:
        while True: 
            data, addr = sock.recvfrom(1024)
            if addr[0] == BALL_IP:
                packet_len = len(data)
                hex_data = data.hex()
                
                if packet_len >= 17: 
                    ball_status_d12 = data[12]
                    sniffed_d10 = data[10] 
                    ts_b3 = data[15] 
                    ts_b4 = data[16]
                    
                    log_print(f"OK (len {packet_len}). Sniffed_d10: {sniffed_d10:02x}, "
                              f"Sniffed_d12_status: {ball_status_d12:02x}, "
                              f"Sniffed_TS_d15_16: {ts_b3:02x}{ts_b4:02x}. Payload: {hex_data}")
                    return ball_status_d12, ts_b3, ts_b4, sniffed_d10, packet_len
                elif packet_len == 9: 
                    log_print(f"INFO: Received ECHO packet from {addr} (len {packet_len}). Data: {hex_data}. Sniffing again...")
                    # Continue sniffing for a status packet
                else:
                    log_print(f"INFO: Received short/unknown packet from {addr} (len {packet_len}). Data: {hex_data}. Sniffing again...")
                    # Continue sniffing
    except socket.timeout:
        log_print("FAIL. Sniffing timed out. Is the ball powered on and connected to the network?")
        return None, None, None, None, 0
    except Exception as e:
        log_print(f"Error during sniffing: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None, None, 0
    finally:
        sock.close()

def trigger_play_sequence(play_op_id_byte):
    log_print(f"Attempting to trigger PLAY (OpID {play_op_id_byte:02x})")
    _, ts_b3, ts_b4, sniffed_d10_val, packet_len_sniffed = sniff_ball_udp_data_for_playstop() 
    
    if packet_len_sniffed == 0 or ts_b3 is None: # Check for complete sniff failure or parse issue
        log_print("Could not get valid ball's UDP status for TS. Aborting play command.")
        return False

    command_group = 0x61
    command_byte2_to_use = COMMAND_BYTE2_FOR_CONTROL 
    
    pc_nonce_byte1 = random.randint(1, 254)
    pc_nonce_byte2 = random.randint(1, 254)
    
    payload = bytes([
        command_group, play_op_id_byte, command_byte2_to_use, 0x00, 0x00,
        pc_nonce_byte1, pc_nonce_byte2, ts_b3, ts_b4
    ])

    sniffed_d10_display = f"{sniffed_d10_val:02x}" if sniffed_d10_val is not None else "N/A (no status packet?)"
    log_print(f"Sending Play Command (OpID {play_op_id_byte:02x}, UsedCmdByte2 {command_byte2_to_use:02x}, "
              f"Nonce {pc_nonce_byte1:02x}{pc_nonce_byte2:02x}, Echoed_TS {ts_b3:02x}{ts_b4:02x}, "
              f"Sniffed_d10_was {sniffed_d10_display} from {packet_len_sniffed}b packet). Payload: {payload.hex()}")
    
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
    # Sniff to check ball's responsiveness and log its state, though ts/nonce from it won't be used in payload for STOP
    ball_status_d12, _, _, sniffed_d10_val, packet_len_sniffed = sniff_ball_udp_data_for_playstop()
    
    if packet_len_sniffed == 0: # Indicates a total sniff failure
        log_print("Could not get ball's UDP status (sniff failed completely). Aborting stop command.")
        return False

    command_group = 0x61
    command_byte2_to_use = COMMAND_BYTE2_FOR_CONTROL # Still using 0x01 for consistency with PLAY for now

    # Reverted to v13.1 style for last 4 bytes of STOP command
    payload = bytes([
        command_group, stop_op_id_byte, command_byte2_to_use, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00 
    ])

    sniffed_d10_display = f"{sniffed_d10_val:02x}" if sniffed_d10_val is not None else "N/A (no status packet?)"
    log_print(f"Sending Stop Command (OpID {stop_op_id_byte:02x}, UsedCmdByte2 {command_byte2_to_use:02x}, "
              f"Nonce/TS: 00000000, " # Explicitly stating what we're sending for these bytes
              f"Sniffed_d10_was {sniffed_d10_display} from {packet_len_sniffed}b packet). Payload: {payload.hex()}")
    
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
    script_version = "v14.1_stop_payload_like_v13.1"
    log_print(f"LED Juggling Ball Interactive Control ({script_version})")
    log_print("--------------------------------------------------------------------------------")
    log_print(f"Target Ball IP: {BALL_IP}, UDP Port: {UDP_PORT}")
    log_print(f"PC IP for sniffing: '{PC_IP}' (blank means all available).")
    log_print(f"COMMAND_BYTE2_FOR_CONTROL (for 3rd byte of cmd) is hardcoded to: 0x{COMMAND_BYTE2_FOR_CONTROL:02x}")
    log_print("STOP commands will use 00000000 for nonce/timestamp bytes.")
    log_print("Ensure sequence is uploaded first.")
    log_print("Press 'p' to play, 's' to stop, 'q' to quit.")

    op_id_for_next_play = 0x14 
    op_id_of_playing_sequence = 0x00 
    
    is_playing_assumed = False 
    feedback_log = []

    try:
        while True:
            action_input_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            current_assumed_state_msg = "Playing" if is_playing_assumed else "Stopped"
            action_prompt_msg = (f"[{action_input_time}] Enter command (p/s/q) "
                                 f"[Next PlayOp: {op_id_for_next_play:02x}, AssumedState: {current_assumed_state_msg}]: ")
            action = input(f"\n{action_prompt_msg}").lower()

            if action == 'p':
                if is_playing_assumed:
                    log_print("Script assumes ball is already playing. Send 's' to stop first.")
                    continue
                
                play_op_to_send = op_id_for_next_play
                play_successful_send = trigger_play_sequence(play_op_to_send)
                
                if play_successful_send:
                    log_print("OBSERVE BALL: Did it play or show red LED?")
                    feedback = input("    Did play work (y/n/r=red_led)? ").lower()
                    feedback_log.append(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}] PLAY OpID {play_op_to_send:02x} Feedback: {feedback}")
                    if feedback == 'y':
                        op_id_of_playing_sequence = play_op_to_send 
                        is_playing_assumed = True
                    else: 
                        is_playing_assumed = False 
                else:
                    log_print("Play command send FAILED or aborted due to sniff failure. Ball state unknown.")
                    feedback_log.append(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}] PLAY OpID {play_op_to_send:02x} Feedback: send_aborted")

            elif action == 's':
                if not is_playing_assumed:
                    log_print("Script assumes ball is already stopped. Send 'p' to play first.")
                    continue
                
                current_stop_op_id = (op_id_of_playing_sequence + 0x0A) & 0xFF 
                stop_successful_send = stop_play_sequence(current_stop_op_id)
                
                if stop_successful_send:
                    next_play_op_candidate = (op_id_of_playing_sequence + 0x14) & 0xFF
                    if next_play_op_candidate == 0x00: 
                        next_play_op_candidate = 0x14 
                    
                    log_print(f"OBSERVE BALL: Did it stop? Next Play Op ID will be 0x{next_play_op_candidate:02x}")
                    feedback = input("    Did stop work (y/n)? ").lower()
                    feedback_log.append(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}] STOP OpID {current_stop_op_id:02x} Feedback: {feedback}")
                    if feedback == 'y':
                        is_playing_assumed = False
                        op_id_for_next_play = next_play_op_candidate
                    else: 
                        is_playing_assumed = True 
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