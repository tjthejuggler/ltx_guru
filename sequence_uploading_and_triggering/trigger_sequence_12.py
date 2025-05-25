import socket
import random
import time
import sys

BALL_IP = "192.168.40.133"  # Or your current ball IP
PC_IP = "" 
BROADCAST_ADDR = "255.255.255.255"
UDP_PORT = 41412

KNOWN_PLAY_NONCES = {
    0x14: (0x99, 0x6f),
    0x28: (0x3e, 0x94)
}

# --- Helper to sniff one UDP packet from the ball ---
def sniff_ball_udp_payload():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind(("", UDP_PORT))
    except OSError as e:
        print(f"Error binding sniff socket: {e}.")
        return None
    
    sock.settimeout(7) 

    print(f"Sniffing for ball's UDP broadcast (from {BALL_IP} on port {UDP_PORT})... ", end="")
    sys.stdout.flush()
    try:
        while True: 
            data, addr = sock.recvfrom(1024)
            if addr[0] == BALL_IP:
                if len(data) >= 17: 
                    print(f"OK. Ball UDP: {data.hex()}") # Log full payload
                    return data 
                else:
                    print(f"Short packet from {addr}. Ignoring.")
    except socket.timeout:
        print("FAIL. Sniffing timed out.")
        return None
    finally:
        sock.close()

# --- Trigger Play ---
def trigger_sequence_interactive(play_op_id_byte, pc_nonce_byte1, pc_nonce_byte2):
    print(f"Attempting to get ball's timestamp for Play Op ID {play_op_id_byte:02x}...")
    ball_udp_payload = sniff_ball_udp_payload()
    if not ball_udp_payload:
        print("Could not get ball's UDP payload. Aborting play command.")
        return False

    ball_ts_byte3 = ball_udp_payload[15] 
    ball_ts_byte4 = ball_udp_payload[16]
    print(f"Using Ball TS bytes (payload[15],payload[16]): {ball_ts_byte3:02x} {ball_ts_byte4:02x}")

    command_group = 0x61
    
    payload = bytes([
        command_group, play_op_id_byte, 0x00, 0x00, 0x00,
        pc_nonce_byte1, pc_nonce_byte2, ball_ts_byte3, ball_ts_byte4
    ])

    print(f"Sending Play Command (Op ID: {play_op_id_byte:02x}). Full payload: {payload.hex()}")
    
    send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    send_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    send_sock.sendto(payload, (BROADCAST_ADDR, UDP_PORT))
    send_sock.close()
    print("Play command sent to network.")
    return True


# --- Stop Play ---
def stop_sequence_interactive(stop_op_id_byte):
    command_group = 0x61
    payload = bytes([
        command_group, stop_op_id_byte, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00
    ])

    print(f"Sending Stop Command (Op ID: {stop_op_id_byte:02x}). Full payload: {payload.hex()}")
    
    send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    send_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    send_sock.sendto(payload, (BROADCAST_ADDR, UDP_PORT))
    send_sock.close()
    print("Stop command sent to network.")
    return True

# --- Main Interactive Loop ---
if __name__ == "__main__":
    print("LED Juggling Ball Interactive Control")
    print("------------------------------------")
    print("1. Power cycle the ball.")
    print("2. Run your `upload_sequence_works.py` script.")
    print("3. THEN run this script.")
    print("Press 'p' to play, 's' to stop, 'q' to quit.")

    current_play_op_id_base = 0x14
    is_playing_assumed = False 
    
    try:
        while True:
            action = input("\nEnter command (p/s/q): ").lower()

            if action == 'p':
                if is_playing_assumed:
                    print("Script assumes ball is already playing. Send 's' to stop first (or 'q' to reset script).")
                    continue
                
                p1, p2 = KNOWN_PLAY_NONCES.get(current_play_op_id_base, (random.randint(1,254), random.randint(1,254))) # Avoid 00 or FF for random for now
                if current_play_op_id_base not in KNOWN_PLAY_NONCES:
                    print(f"Note: Play Op ID {current_play_op_id_base:02x} not in KNOWN_PLAY_NONCES, using random P1=0x{p1:02x}, P2=0x{p2:02x}.")
                else:
                    print(f"Using KNOWN nonce P1=0x{p1:02x}, P2=0x{p2:02x} for Op ID {current_play_op_id_base:02x}.")

                if trigger_sequence_interactive(current_play_op_id_base, p1, p2):
                    is_playing_assumed = True # Assume play was successful for script logic
                    print("OBSERVE BALL: Did it play or show red LED?")
                else:
                    print("Play command FAILED (could not get ball timestamp). Ball state unknown.")

            elif action == 's':
                if not is_playing_assumed:
                    print("Script assumes ball is already stopped. Send 'p' to play first (or 'q' to reset script).")
                    continue
                
                current_stop_op_id = current_play_op_id_base + 0x0A
                if stop_sequence_interactive(current_stop_op_id):
                    is_playing_assumed = False
                    current_play_op_id_base = (current_play_op_id_base + 0x14) & 0xFF # Cycle and wrap at 255
                    if current_play_op_id_base == 0x00: # Avoid 0x00 as a base op ID if it wraps
                        current_play_op_id_base = 0x14
                    print(f"OBSERVE BALL: Did it stop? Next Play Op ID will be 0x{current_play_op_id_base:02x}")
                else:
                    print("Stop command FAILED. Ball state unknown.")

            elif action == 'q':
                print("Exiting.")
                break
            else:
                print("Invalid command. Use 'p', 's', or 'q'.")
    except KeyboardInterrupt:
        print("\nExiting due to Ctrl-C.")