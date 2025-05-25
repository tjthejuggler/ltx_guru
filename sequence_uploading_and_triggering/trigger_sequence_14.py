import socket
import random
import time
import sys

# --- Configuration ---
BALL_IP = "192.168.40.133"  # <<<< YOUR BALL IP
PC_IP = ""
BROADCAST_ADDR = "255.255.255.255"
UDP_PORT = 41412

KNOWN_PLAY_NONCES = {
    # 0x14: (0x99, 0x6f), # Example, adjust if needed based on app's first OpID
    # 0x28: (0x3e, 0x94)
}
# --- End Configuration ---

# --- Helper to sniff one UDP packet from the ball ---
def sniff_ball_udp_status():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind((PC_IP, UDP_PORT))
    except OSError as e:
        print(f"Error binding sniff socket: {e}. Make sure no other script is bound to this port.")
        if "Address already in use" in str(e):
            print("Hint: Another program (maybe a previous run of this script or Wireshark) is using port 41412.")
        return None, None, None, None # Return 4 None values
    
    sock.settimeout(7)

    print(f"Sniffing for ball's UDP broadcast (from {BALL_IP} on port {UDP_PORT})... ", end="")
    sys.stdout.flush()
    try:
        while True: 
            data, addr = sock.recvfrom(1024)
            if addr[0] == BALL_IP:
                if len(data) >= 17: # mac(4?) + unknown(5) + status_field1(1) + status_field2(1) + status_counter(1) + status(1) + timestamp(4)
                    
                    ball_status_byte = data[12]
                    ball_command_byte2_source = data[10] 
                    ball_ts_byte3 = data[15] 
                    ball_ts_byte4 = data[16]
                    
                    print(f"OK. Ball Status: {ball_status_byte:02x}, "
                          f"Source for CmdByte2: {ball_command_byte2_source:02x}, "
                          f"TS_B3,4: {ball_ts_byte3:02x}{ball_ts_byte4:02x}")
                    return ball_status_byte, ball_command_byte2_source, ball_ts_byte3, ball_ts_byte4
                else:
                    print(f"INFO: Received short packet from {addr} (len {len(data)}). Ignoring.")
    except socket.timeout:
        print("FAIL. Sniffing timed out. Is the ball powered on and connected to the network?")
        return None, None, None, None # Return 4 None values
    except Exception as e:
        print(f"Error during sniffing: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None, None # Return 4 None values
    finally:
        sock.close()

# --- Trigger Play ---
def trigger_play_sequence(play_op_id_byte, pc_nonce_byte1, pc_nonce_byte2):
    ball_status, sniffed_cmd_byte2, ts_b3, ts_b4 = sniff_ball_udp_status() 
    
    if ball_status is None:
        print("Could not get ball's UDP status. Aborting play command.")
        return False, 0x00 

    command_group = 0x61
    command_byte2_to_use = sniffed_cmd_byte2
    
    payload = bytes([
        command_group, play_op_id_byte, command_byte2_to_use, 0x00, 0x00,
        pc_nonce_byte1, pc_nonce_byte2, ts_b3, ts_b4
    ])

    print(f"Sending Play Command (OpID {play_op_id_byte:02x}, CmdByte2 {command_byte2_to_use:02x}). Payload: {payload.hex()}")
    
    send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    send_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    try:
        send_sock.sendto(payload, (BROADCAST_ADDR, UDP_PORT))
        print("Play command sent.")
        return True, command_byte2_to_use
    except Exception as e:
        print(f"Error sending Play command: {e}")
        return False, command_byte2_to_use 
    finally:
        send_sock.close()




# --- Stop Play ---
def stop_play_sequence(stop_op_id_byte):
    ball_status, sniffed_cmd_byte2, ts_b3, ts_b4 = sniff_ball_udp_status() # Sniff TS
    
    if ball_status is None:
        print("Could not get ball's UDP status. Aborting stop command.")
        return False

    command_group = 0x61
    command_byte2_to_use = sniffed_cmd_byte2 # This is consistently 0x01 from logs

    # Ensure ts_b3 and ts_b4 are not None if sniff_ball_udp_status might return them as None
    # (though it shouldn't if ball_status is not None)
    if ts_b3 is None or ts_b4 is None:
        print("Warning: Timestamp bytes for STOP are None. Defaulting to 0x00. This might be an issue.")
        ts_b3, ts_b4 = 0x00, 0x00

    payload = bytes([
        command_group, stop_op_id_byte, command_byte2_to_use, 0x00, 0x00,
        0x00, 0x00, ts_b3, ts_b4  # MODIFIED: Echo sniffed timestamp bytes
    ])

    print(f"Sending Stop Command (Op ID: {stop_op_id_byte:02x}, CmdByte2 {command_byte2_to_use:02x}, TS_echo {ts_b3:02x}{ts_b4:02x}). Payload: {payload.hex()}")
    
    send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    send_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    try:
        send_sock.sendto(payload, (BROADCAST_ADDR, UDP_PORT))
        print("Stop command sent.")
        return True
    except Exception as e:
        print(f"Error sending Stop command: {e}")
        return False
    finally:
        send_sock.close()

# --- Main Interactive Loop ---
if __name__ == "__main__":
    print("LED Juggling Ball Interactive Control (v13.1 - Dynamic Byte2, Error Handling Fix)")
    print("--------------------------------------------------------------------------------")
    print(f"Target Ball IP: {BALL_IP}, UDP Port: {UDP_PORT}")
    print("Ensure sequence is uploaded first.")
    print("Press 'p' to play, 's' to stop, 'q' to quit.")

    op_id_for_next_play = 0x14 
    op_id_of_playing_sequence = 0x00 
    
    is_playing_assumed = False
    
    try:
        while True:
            action = input(f"\nEnter command (p/s/q) [Next PlayOp: {op_id_for_next_play:02x}]: ").lower()

            if action == 'p':
                if is_playing_assumed:
                    print("Script assumes ball is already playing. Send 's' to stop first.")
                    continue
                
                play_op_to_send = op_id_for_next_play

                p1, p2 = KNOWN_PLAY_NONCES.get(play_op_to_send, 
                                               (random.randint(1, 254), random.randint(1, 254)))
                if play_op_to_send not in KNOWN_PLAY_NONCES:
                    print(f"Using random P1=0x{p1:02x}, P2=0x{p2:02x} for Op ID {play_op_to_send:02x}.")
                else:
                    print(f"Using KNOWN nonce P1=0x{p1:02x}, P2=0x{p2:02x} for Op ID {play_op_to_send:02x}.")

                play_successful, _ = trigger_play_sequence(play_op_to_send, p1, p2) # Byte2 used is handled internally
                
                if play_successful:
                    op_id_of_playing_sequence = play_op_to_send # Store the OpID that started this play
                    is_playing_assumed = True
                    print("OBSERVE BALL: Did it play or show red LED?")
                else:
                    print("Play command FAILED. Ball state unknown.")

            elif action == 's':
                if not is_playing_assumed:
                    print("Script assumes ball is already stopped. Send 'p' to play first.")
                    continue
                
                current_stop_op_id = (op_id_of_playing_sequence + 0x0A) & 0xFF
                
                if stop_play_sequence(current_stop_op_id): # Byte2 used is handled internally
                    is_playing_assumed = False
                    
                    # Prepare for the next play cycle
                    op_id_for_next_play = (op_id_of_playing_sequence + 0x14) & 0xFF
                    if op_id_for_next_play == 0x00:
                        op_id_for_next_play = 0x14
                    
                    print(f"OBSERVE BALL: Did it stop? Next Play Op ID will be 0x{op_id_for_next_play:02x}")
                else:
                    print("Stop command FAILED. Ball state unknown.")

            elif action == 'q':
                print("Exiting.")
                break
            else:
                print("Invalid command. Use 'p', 's', or 'q'.")
    
    except KeyboardInterrupt:
        print("\nExiting due to Ctrl-C.")
    except Exception as e:
        print(f"\nAn unexpected error occurred in the main loop: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("--- Control Script Finished ---")














