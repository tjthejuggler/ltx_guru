import socket
import random
import time

BALL_IP = "192.168.40.205"  # Replace with actual ball IP if it changes
PC_IP = "192.168.40.40"    # Replace with your Python PC's IP if different
BROADCAST_ADDR = "255.255.255.255" # Or your subnet broadcast e.g., "192.168.40.255"
UDP_PORT = 41412

# --- Helper to sniff one UDP packet from the ball ---
def sniff_ball_udp_payload():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind(("", UDP_PORT)) # Listen on all interfaces for the ball's broadcast
    except OSError as e:
        print(f"Error binding sniff socket: {e}. Ensure port {UDP_PORT} is not in use.")
        return None
    
    sock.settimeout(10) # Increased timeout to 10 seconds

    print(f"Sniffing for ball's UDP broadcast (from {BALL_IP} on port {UDP_PORT})...")
    try:
        while True: # Loop to ignore other packets until one from the ball is found
            data, addr = sock.recvfrom(1024)
            if addr[0] == BALL_IP:
                if len(data) >= 17: # Ensure packet is long enough for timestamp
                    print(f"Received packet from {addr}: {data.hex()}")
                    return data # Return the UDP payload
                else:
                    print(f"Received short packet from {addr}: {data.hex()}. Ignoring.")
            # else:
            #     print(f"Ignoring packet from {addr}") # Optional: for debugging other traffic
    except socket.timeout:
        print("Sniffing timed out. No suitable packet from ball.")
        return None
    finally:
        sock.close()

# --- Trigger Play ---
def trigger_sequence_play_test(play_op_id_byte=0x14):
    print("Attempting to get ball's timestamp...")
    ball_udp_payload = sniff_ball_udp_payload()
    if not ball_udp_payload: # sniff_ball_udp_payload now returns None on error/timeout
        print("Could not get ball's UDP payload. Aborting play command.")
        return

    # Ball's timestamp is bytes 13-16 (0-indexed) of its UDP payload.
    # We need the 3rd and 4th byte of this LE timestamp (bytes 15 and 16 of payload)
    ball_ts_byte3 = ball_udp_payload[15] 
    ball_ts_byte4 = ball_udp_payload[16]

    # --- TEST: Hardcode P1, P2 from successful app trigger ---
    pc_byte1 = 0x99 
    pc_byte2 = 0x6f 
    print(f"Using TEST P1=0x{pc_byte1:02x}, P2=0x{pc_byte2:02x}")
    # --- END TEST ---

    # Original random generation (commented out for this test)
    # pc_byte1 = random.randint(0, 255)
    # pc_byte2 = random.randint(0, 255)

    command_group = 0x61
    
    payload = bytes([
        command_group, play_op_id_byte, 0x00, 0x00, 0x00,
        pc_byte1, pc_byte2, ball_ts_byte3, ball_ts_byte4
    ])

    print(f"Sending Play Command (Op ID: {play_op_id_byte:02x}) with suffix: {payload[5:].hex()}")
    
    send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    send_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    # Ensure PC_IP is correctly set for your environment if binding source is needed
    # try:
    #     send_sock.bind((PC_IP, 0)) # Bind to PC_IP and an ephemeral port
    # except OSError as e:
    #     print(f"Warning: Could not bind sending socket to {PC_IP}: {e}")
    #     # Proceeding with default OS-assigned source IP/port
        
    send_sock.sendto(payload, (BROADCAST_ADDR, UDP_PORT))
    send_sock.close()
    print("Play command sent.")

# --- Stop Play (using 0x1e for first stop cycle) ---
def stop_sequence_play_test(stop_op_id_byte=0x1e):
    command_group = 0x61
    payload = bytes([
        command_group, stop_op_id_byte, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00  # Static suffix for stop
    ])
    print(f"Sending Stop Command (Op ID: {stop_op_id_byte:02x})")
    send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    send_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    send_sock.sendto(payload, (BROADCAST_ADDR, UDP_PORT))
    send_sock.close()
    print("Stop command sent.")

# --- Example Usage ---
if __name__ == "__main__":
    # !! IMPORTANT !!
    # 1. Power cycle the ball.
    # 2. Run your `upload_sequence_works.py` script to upload a sequence.
    # 3. ONLY THEN run this script.

    print("\nAttempting first play with test parameters...")
    trigger_sequence_play_test(play_op_id_byte=0x14) # Uses 0x14 for the first play
    
    # print("\nWaiting 10 seconds before attempting stop...")
    # time.sleep(10) 
    
    # print("\nAttempting first stop with test parameters...")
    # stop_sequence_play_test(stop_op_id_byte=0x1e) # Uses 0x1e for the first stop