import socket
import random
import time
import sys
from datetime import datetime # For timestamped logs

# --- Configuration ---
# IMPORTANT: Verify BALL_IP. Last seen as 192.168.40.205 in your logs.
BALL_IP = "192.168.40.205"
PC_IP = ""  # Leave blank to bind to all interfaces for sniffing
BROADCAST_ADDR = "255.255.255.255"
UDP_PORT = 41412

# Nonces observed from official PC app. Your script will cycle through op_ids.
# If an op_id isn't here, it will use random nonces.
KNOWN_PLAY_NONCES = {
    0x58: (0x6f, 0xcc),
    0x80: (0x86, 0xd2),
    0x94: (0x7a, 0xd5),
    0xbc: (0xef, 0xda),
    0xe4: (0x6c, 0xe0),
    # Add more if you observe them.
    # Example for the very first play OpID 0x14 (if PC app starts with it)
    # 0x14: (0x??, 0x??), # You'd need to capture this from the PC app
}
# --- End Configuration ---

def log_print(message):
    """Prints a message with a timestamp."""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}] {message}")
    sys.stdout.flush()

# --- Helper to sniff one UDP packet from the ball ---
def sniff_ball_udp_status():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind((PC_IP, UDP_PORT))
    except OSError as e:
        log_print(f"Error binding sniff socket: {e}. Make sure no other script/app is bound to this port.")
        if "Address already in use" in str(e):
            log_print("Hint: Another program (maybe a previous run or Wireshark/Official App) is using port 41412.")
        return None, None, None, None # Return 4 None values
    
    sock.settimeout(7) # Increased timeout slightly

    log_print(f"Sniffing for ball's UDP broadcast (from {BALL_IP} on port {UDP_PORT})... ")
    try:
        while True: 
            data, addr = sock.recvfrom(1024)
            if addr[0] == BALL_IP:
                packet_len = len(data)
                hex_data = data.hex()
                
                # Default values in case parsing fails for unexpected packet
                ball_status_byte = None
                ball_command_byte2_source = None
                ts_b3, ts_b4 = None, None

                if packet_len == 62:
                    # Assuming standard 62-byte active status packet
                    # Structure: MAC(4?) + unknown(5) + field9(1) + cmd_byte2_src(1) + status(1) + timestamp(4) ...
                    # Indices:   [0:3]     [4:8]        [9]         [10]                [11] -> was status_counter
                    #            [12] -> was status                  [13:16]
                    # The structure seen after PC command (F1121) was slightly different than PC App's own active status
                    # Let's use the common structure your script originally assumed for 62-byte:
                    if packet_len >= 17: # Basic check
                        ball_status_byte = data[12]
                        ball_command_byte2_source = data[10] 
                        ts_b3 = data[15] 
                        ts_b4 = data[16]
                        log_print(f"OK (62-byte). Ball Status: {ball_status_byte:02x}, "
                                  f"SniffedCmdByte2: {ball_command_byte2_source:02x}, "
                                  f"TS_B3,4: {ts_b3:02x}{ts_b4:02x}. Payload: {hex_data}")
                        return ball_status_byte, ball_command_byte2_source, ts_b3, ts_b4
                elif packet_len == 47:
                    # 47-byte beacon packet
                    # Structure: DevID(4) + zeros(9) + status(1) + TS_part1(2) + ts_b3(1) + ts_b4(1) ...
                    # Indices:   [0:3]    [4:12]      [12]        [13:14]       [15]      [16]
                    if packet_len >= 17: # Basic check
                        ball_status_byte = data[12] # Should be 0x00 for idle
                        ball_command_byte2_source = data[10] # Should be 0x00 from the zero block
                        ts_b3 = data[15]
                        ts_b4 = data[16]
                        log_print(f"OK (47-byte beacon). Ball Status: {ball_status_byte:02x}, "
                                  f"SniffedCmdByte2: {ball_command_byte2_source:02x}, "
                                  f"TS_B3,4: {ts_b3:02x}{ts_b4:02x}. Payload: {hex_data}")
                        return ball_status_byte, ball_command_byte2_source, ts_b3, ts_b4
                else:
                    log_print(f"INFO: Received packet of unexpected length {packet_len} from {addr}. Data: {hex_data}. Ignoring for command.")
            
    except socket.timeout:
        log_print("FAIL. Sniffing timed out. Is the ball powered on and connected?")
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
    
    # Sniffing is primarily for the timestamp echo.
    # The ball_status and sniffed_cmd_byte2 from sniff can be used for logging/context.
    ball_status_ignored, sniffed_cmd_byte2_ignored, ts_b3, ts_b4 = sniff_ball_udp_status() 
    
    if ts_b3 is None or ts_b4 is None: # Check if we got a timestamp
        log_print("Could not get ball's UDP status for TS. Aborting play command.")
        # Optionally, could try sending with 00 for TS, but better to abort if sniff fails.
        # ts_b3, ts_b4 = 0x00, 0x00 # Fallback if you want to try anyway
        return False, 0x00 # Indicate failure and the CmdByte2 we would have tried

    command_group = 0x61
    command_byte2_to_use = 0x01  # HARDCODED to 0x01 - THIS IS THE KEY CHANGE FOR SENDING
    
    payload = bytes([
        command_group, play_op_id_byte, command_byte2_to_use, 0x00, 0x00,
        pc_nonce_byte1, pc_nonce_byte2, ts_b3, ts_b4
    ])

    log_print(f"Sending Play Command (OpID {play_op_id_byte:02x}, SentCmdByte2 {command_byte2_to_use:02x}, TS_echo {ts_b3:02x}{ts_b4:02x}). Payload: {payload.hex()}")
    
    send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    send_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    try:
        send_sock.sendto(payload, (BROADCAST_ADDR, UDP_PORT))
        log_print("Play command sent.")
        # We don't know if it was successful until we observe or sniff an ACK/status change.
        # For now, assume it was sent and the ball will react.
        return True, command_byte2_to_use 
    except Exception as e:
        log_print(f"Error sending Play command: {e}")
        return False, command_byte2_to_use 
    finally:
        send_sock.close()

# --- Stop Play ---
def stop_play_sequence(stop_op_id_byte):
    log_print(f"Attempting to trigger STOP (OpID {stop_op_id_byte:02x})")
    
    ball_status_ignored, sniffed_cmd_byte2_ignored, ts_b3, ts_b4 = sniff_ball_udp_status()
    
    if ts_b3 is None or ts_b4 is None: # Check if we got a timestamp
        log_print("Could not get ball's UDP status for TS. Aborting stop command.")
        # ts_b3, ts_b4 = 0x00, 0x00 # Fallback
        return False

    command_group = 0x61
    command_byte2_to_use = 0x01  # HARDCODED to 0x01 - THIS IS THE KEY CHANGE FOR SENDING

    payload = bytes([
        command_group, stop_op_id_byte, command_byte2_to_use, 0x00, 0x00,
        0x00, 0x00, ts_b3, ts_b4 # Echoing TS for stop. If this fails, try 0x00,0x00
    ])

    log_print(f"Sending Stop Command (OpID {stop_op_id_byte:02x}, SentCmdByte2 {command_byte2_to_use:02x}, TS_echo {ts_b3:02x}{ts_b4:02x}). Payload: {payload.hex()}")
    
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
    script_version = "v14.0 - Hardcoded CmdByte2=0x01, TS Echo for Stop, Timestamps, KNOWN_NONCES"
    log_print(f"LED Juggling Ball Interactive Control ({script_version})")
    log_print("--------------------------------------------------------------------------------")
    log_print(f"Target Ball IP: {BALL_IP}, UDP Port: {UDP_PORT}")
    log_print(f"PC IP for sniffing: '{PC_IP}' (blank means all available).")
    log_print("Ensure sequence is uploaded first.")
    log_print("Press 'p' to play, 's' to stop, 'q' to quit.")

    op_id_for_next_play = 0x14 
    op_id_of_playing_sequence = 0x00 
    
    is_playing_assumed = False # This script assumes the ball's state by observation.
    
    try:
        while True:
            action = input(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}] Enter command (p/s/q) [Next PlayOp: {op_id_for_next_play:02x}]: ").lower()

            if action == 'p':
                if is_playing_assumed:
                    log_print("Script assumes ball is already playing. Send 's' to stop first.")
                    continue
                
                play_op_to_send = op_id_for_next_play

                # Get nonce: from known list or random
                p1, p2 = KNOWN_PLAY_NONCES.get(play_op_to_send, 
                                               (random.randint(1, 254), random.randint(1, 254)))
                if play_op_to_send not in KNOWN_PLAY_NONCES:
                    log_print(f"Using RANDOM nonce P1=0x{p1:02x}, P2=0x{p2:02x} for Op ID {play_op_to_send:02x}.")
                else:
                    log_print(f"Using KNOWN nonce P1=0x{p1:02x}, P2=0x{p2:02x} for Op ID {play_op_to_send:02x}.")

                # The second return value (used_cmd_byte2) is now mostly for logging if needed,
                # as the sending function uses a hardcoded 0x01.
                play_successful, _ = trigger_play_sequence(play_op_to_send, p1, p2)
                
                if play_successful:
                    op_id_of_playing_sequence = play_op_to_send 
                    is_playing_assumed = True
                    log_print("OBSERVE BALL: Did it play or show red LED?")
                else:
                    log_print("Play command send FAILED or aborted due to sniff failure. Ball state unknown.")

            elif action == 's':
                if not is_playing_assumed:
                    log_print("Script assumes ball is already stopped. Send 'p' to play first.")
                    continue
                
                # Stop OpID is based on the OpID that *started* the current play
                current_stop_op_id = (op_id_of_playing_sequence + 0x0A) & 0xFF 
                
                if stop_play_sequence(current_stop_op_id):
                    is_playing_assumed = False
                    
                    # Prepare for the next play cycle
                    # The next PLAY OpID is based on the OpID that was *just playing*.
                    op_id_for_next_play = (op_id_of_playing_sequence + 0x14) & 0xFF
                    if op_id_for_next_play == 0x00: # Avoid OpID 0x00 for play
                        op_id_for_next_play = 0x14 
                    
                    log_print(f"OBSERVE BALL: Did it stop? Next Play Op ID will be 0x{op_id_for_next_play:02x}")
                else:
                    log_print("Stop command send FAILED or aborted. Ball state unknown.")

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
        log_print("--- Control Script Finished ---")