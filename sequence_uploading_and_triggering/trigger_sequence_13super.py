import socket
import random
import time
import sys
from datetime import datetime # For timestamped logs

# --- Configuration ---
# IMPORTANT: Verify BALL_IP. Last seen as 192.168.40.205.
BALL_IP = "192.168.40.205"
PC_IP = ""  # Leave blank to bind to all interfaces for sniffing
BROADCAST_ADDR = "255.255.255.255"
UDP_PORT = 41412

KNOWN_PLAY_NONCES = {
    # 0x58: (0x6f, 0xcc), # Example from PC app log
    # 0x80: (0x86, 0xd2), # Example from PC app log
}
# --- End Configuration ---

def log_print(message):
    """Prints a message with a timestamp."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    print(f"[{timestamp}] {message}")
    sys.stdout.flush() # Ensure immediate output

# --- Helper to sniff one UDP packet from the ball ---
def sniff_ball_udp_status():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind((PC_IP, UDP_PORT))
    except OSError as e:
        log_print(f"Error binding sniff socket: {e}. Make sure no other script is bound to this port.")
        if "Address already in use" in str(e):
            log_print("Hint: Another program (maybe a previous run or Wireshark/Official App) is using port 41412.")
        return None, None, None, None # Return 4 None values
    
    sock.settimeout(7)

    log_print(f"Sniffing for ball's UDP broadcast (from {BALL_IP} on port {UDP_PORT})... ")
    try:
        while True: 
            data, addr = sock.recvfrom(1024)
            if addr[0] == BALL_IP:
                packet_len = len(data)
                hex_data = data.hex()
                
                ball_status_byte = None
                ball_command_byte2_source = None
                ts_b3, ts_b4 = None, None

                # This script (v13.1) originally expected >= 17, implying it could handle 47 or 62 byte packets
                # for its specific parsing needs if those indices were valid.
                if packet_len >= 17:
                    # Original parsing logic from v13.1
                    ball_status_byte = data[12]
                    ball_command_byte2_source = data[10] 
                    ts_b3 = data[15] 
                    ts_b4 = data[16]
                    
                    log_print(f"OK (len {packet_len}). Sniffed Status: {ball_status_byte:02x}, "
                              f"SniffedCmdByte2: {ball_command_byte2_source:02x}, "
                              f"Sniffed_TS_B3,4: {ts_b3:02x}{ts_b4:02x}. Payload: {hex_data}")
                    return ball_status_byte, ball_command_byte2_source, ts_b3, ts_b4
                else:
                    log_print(f"INFO: Received short packet from {addr} (len {packet_len}). Data: {hex_data}. Ignoring for command.")
    except socket.timeout:
        log_print("FAIL. Sniffing timed out. Is the ball powered on and connected to the network?")
        return None, None, None, None
    except Exception as e:
        log_print(f"Error during sniffing: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None, None
    finally:
        sock.close()

# --- Trigger Play ---
def trigger_play_sequence(play_op_id_byte, pc_nonce_byte1, pc_nonce_byte2):
    log_print(f"Attempting to trigger PLAY (OpID {play_op_id_byte:02x})")
    ball_status, sniffed_cmd_byte2, ts_b3, ts_b4 = sniff_ball_udp_status() 
    
    if ball_status is None: # Check if sniff failed to get essential data
        log_print("Could not get ball's UDP status for TS. Aborting play command.")
        return False, 0x00 

    command_group = 0x61
    command_byte2_to_use = sniffed_cmd_byte2 # Using the sniffed value as per v13.1
    
    payload = bytes([
        command_group, play_op_id_byte, command_byte2_to_use, 0x00, 0x00,
        pc_nonce_byte1, pc_nonce_byte2, ts_b3, ts_b4
    ])

    log_print(f"Sending Play Command (OpID {play_op_id_byte:02x}, UsedCmdByte2 {command_byte2_to_use:02x}, Echoed_TS {ts_b3:02x}{ts_b4:02x}). Payload: {payload.hex()}")
    
    send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    send_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    try:
        send_sock.sendto(payload, (BROADCAST_ADDR, UDP_PORT))
        log_print("Play command sent.")
        return True, command_byte2_to_use
    except Exception as e:
        log_print(f"Error sending Play command: {e}")
        return False, command_byte2_to_use 
    finally:
        send_sock.close()

# --- Stop Play ---
def stop_play_sequence(stop_op_id_byte):
    log_print(f"Attempting to trigger STOP (OpID {stop_op_id_byte:02x})")
    ball_status, sniffed_cmd_byte2, ts_b3_ignored, ts_b4_ignored = sniff_ball_udp_status() # Original doesn't use TS for stop
    
    if ball_status is None:
        log_print("Could not get ball's UDP status. Aborting stop command.")
        return False

    command_group = 0x61
    command_byte2_to_use = sniffed_cmd_byte2 # Using the sniffed value as per v13.1

    payload = bytes([
        command_group, stop_op_id_byte, command_byte2_to_use, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00 # Original v13.1 logic for stop payload
    ])

    log_print(f"Sending Stop Command (OpID {stop_op_id_byte:02x}, UsedCmdByte2 {command_byte2_to_use:02x}). Payload: {payload.hex()}")
    
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

# --- Main Interactive Loop ---
if __name__ == "__main__":
    script_version = "v13.1_feedback_timestamps"
    log_print(f"LED Juggling Ball Interactive Control ({script_version})")
    log_print("--------------------------------------------------------------------------------")
    log_print(f"Target Ball IP: {BALL_IP}, UDP Port: {UDP_PORT}")
    log_print(f"PC IP for sniffing: '{PC_IP}' (blank means all available).")
    log_print("Ensure sequence is uploaded first.")
    log_print("Press 'p' to play, 's' to stop, 'q' to quit.")

    op_id_for_next_play = 0x14 
    op_id_of_playing_sequence = 0x00 
    
    is_playing_assumed = False # This script assumes the ball's state by observation.
    
    # Store feedback
    feedback_log = []

    try:
        while True:
            action_input_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            action_prompt_msg = f"[{action_input_time}] Enter command (p/s/q) [Next PlayOp: {op_id_for_next_play:02x}]: "
            action = input(f"\n{action_prompt_msg}").lower()

            if action == 'p':
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

                play_successful_send, used_cmd_byte2 = trigger_play_sequence(play_op_to_send, p1, p2)
                
                if play_successful_send:
                    op_id_of_playing_sequence = play_op_to_send 
                    is_playing_assumed = True
                    log_print("OBSERVE BALL: Did it play or show red LED?")
                    feedback = input("    Did play work (y/n/r=red_led)? ").lower()
                    feedback_log.append(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}] PLAY OpID {play_op_to_send:02x} Feedback: {feedback}")
                    if feedback == 'n' or feedback == 'r':
                        is_playing_assumed = False # Correct assumption if it didn't work
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
                    is_playing_assumed = False
                    
                    op_id_for_next_play = (op_id_of_playing_sequence + 0x14) & 0xFF
                    if op_id_for_next_play == 0x00: 
                        op_id_for_next_play = 0x14 
                    
                    log_print(f"OBSERVE BALL: Did it stop? Next Play Op ID will be 0x{op_id_for_next_play:02x}")
                    feedback = input("    Did stop work (y/n)? ").lower()
                    feedback_log.append(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}] STOP OpID {current_stop_op_id:02x} Feedback: {feedback}")
                    if feedback == 'n':
                        is_playing_assumed = True # Correct assumption if it didn't stop
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
            print(entry) # Print without the log_print prefix for cleaner final output
        log_print("--- Control Script Finished ---")