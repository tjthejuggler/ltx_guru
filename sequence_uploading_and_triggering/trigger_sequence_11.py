import socket
import random
import time
import sys # For sys.stdout.flush()

BALL_IP = "192.168.40.205"  # Replace with actual ball IP if it changes
PC_IP = "" # Your PC's IP on the relevant network interface, e.g., "192.168.40.40"
           # Leave "" to bind to all available interfaces for sniffing.
BROADCAST_ADDR = "255.255.255.255" # Or your subnet broadcast e.g., "192.168.40.255"
UDP_PORT = 41412

# Known successful P1, P2 nonces from app captures for specific play operation IDs
# (Play_Op_ID, P1, P2)
# The app sent two play commands per trigger, we'll use the first one from each cycle.
# From official app capture:
# Cycle 1 (Op ID 0x14): Suffix 99 6f 03 00 (P1=0x99, P2=0x6f). Ball TS B3,B4 was 03 00
# Cycle 2 (Op ID 0x28): Suffix 3e 94 03 00 (P1=0x3e, P2=0x94). Ball TS B3,B4 was 03 00
# We will use these P1,P2 for the corresponding Play Op IDs.
# If we go beyond these, we'll use random P1,P2.
KNOWN_PLAY_NONCES = {
    0x14: (0x99, 0x6f), # For the first play cycle
    0x28: (0x3e, 0x94)  # For the second play cycle
}

# --- Helper to sniff one UDP packet from the ball ---
def sniff_ball_udp_payload():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        # Bind to allow receiving broadcasts. Empty string for IP means listen on all interfaces.
        sock.bind(("", UDP_PORT))
    except OSError as e:
        print(f"Error binding sniff socket: {e}. Ensure port {UDP_PORT} is not in use (e.g. by another script or Wireshark without promiscuous mode).")
        print("If on Linux, 'sudo netstat -lunp | grep 41412' can show if port is in use.")
        return None
    
    sock.settimeout(7) # Wait up to 7 seconds for a packet

    print(f"Sniffing for ball's UDP broadcast (from {BALL_IP} on port {UDP_PORT})... ", end="")
    sys.stdout.flush()
    try:
        while True: 
            data, addr = sock.recvfrom(1024)
            if addr[0] == BALL_IP:
                if len(data) >= 17: 
                    print(f"OK. (TS Bytes 15,16: {data[15]:02x}{data[16]:02x})")
                    return data 
                else:
                    print(f"Short packet from {addr}. Ignoring.")
            # else: # For debugging noisy networks
            #     print(f"Ignoring packet from {addr}") 
    except socket.timeout:
        print("FAIL. Sniffing timed out. No suitable packet from ball.")
        return None
    finally:
        sock.close()

# --- Trigger Play ---
def trigger_sequence_interactive(play_op_id_byte, pc_nonce_byte1, pc_nonce_byte2):
    print("Attempting to get ball's timestamp for Play command...")
    ball_udp_payload = sniff_ball_udp_payload()
    if not ball_udp_payload:
        print("Could not get ball's UDP payload. Aborting play command.")
        return False

    ball_ts_byte3 = ball_udp_payload[15] 
    ball_ts_byte4 = ball_udp_payload[16]

    command_group = 0x61
    
    payload = bytes([
        command_group, play_op_id_byte, 0x00, 0x00, 0x00,
        pc_nonce_byte1, pc_nonce_byte2, ball_ts_byte3, ball_ts_byte4
    ])

    print(f"Sending Play Command (Op ID: {play_op_id_byte:02x}) with P1,P2: {pc_nonce_byte1:02x},{pc_nonce_byte2:02x} and TS Suffix: {payload[7:].hex()}")
    
    send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    send_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    send_sock.sendto(payload, (BROADCAST_ADDR, UDP_PORT))
    # The app sent a second, slightly different play command. We'll try one for now.
    # If issues, could add the second send here.
    send_sock.close()
    print("Play command sent.")
    return True


# --- Stop Play ---
def stop_sequence_interactive(stop_op_id_byte):
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
    return True

# --- Main Interactive Loop ---
if __name__ == "__main__":
    print("LED Juggling Ball Interactive Control")
    print("------------------------------------")
    print("Ensure the ball is powered on and a sequence has been uploaded.")
    print("Press 'p' to play, 's' to stop, 'q' to quit.")

    current_play_op_id_base = 0x14 # Start with the first play operation ID
    is_playing = False # Assume stopped initially
    play_cycle_index = 0 # To cycle through known nonces or generate random

    while True:
        action = input("\nEnter command (p/s/q): ").lower()

        if action == 'p':
            if is_playing:
                print("Ball is already considered playing. Send 's' to stop first.")
                continue
            
            p1, p2 = KNOWN_PLAY_NONCES.get(current_play_op_id_base, (random.randint(0,255), random.randint(0,255)))
            if current_play_op_id_base not in KNOWN_PLAY_NONCES:
                print(f"Note: Play Op ID {current_play_op_id_base:02x} not in known nonces, using random P1,P2.")
            
            if trigger_sequence_interactive(current_play_op_id_base, p1, p2):
                is_playing = True
            else:
                print("Play command failed to send (could not get ball timestamp).")

        elif action == 's':
            if not is_playing:
                print("Ball is already considered stopped. Send 'p' to play first.")
                continue
            
            current_stop_op_id = current_play_op_id_base + 0x0A
            if stop_sequence_interactive(current_stop_op_id):
                is_playing = False
                # Increment for the *next* play cycle
                current_play_op_id_base += 0x14 
                if current_play_op_id_base > 0xFF: # Basic wrap-around, though unlikely to be hit often
                    current_play_op_id_base = 0x14 
                play_cycle_index += 1
            else:
                print("Stop command failed.")

        elif action == 'q':
            print("Exiting.")
            break
        else:
            print("Invalid command. Use 'p', 's', or 'q'.")