import socket
import time
import threading

# --- Configuration ---
BALL_IP = "192.168.40.133"
BROADCAST_IP = "255.255.255.255"
UDP_PORT = 41412
APP_IP = "192.168.40.40"

# This is the specific PLAY command payload observed when the app triggered play
# (Packet 261 in your capture, when ball was sending 47-byte statuses)
PAYLOAD_APP_SPECIFIC_PLAY_HEX = "61fa0000008b219000"
PAYLOAD_APP_SPECIFIC_PLAY_BYTES = bytes.fromhex(PAYLOAD_APP_SPECIFIC_PLAY_HEX)

# This is an observed IDLE/STOP payload from the app
PAYLOAD_IDLE_HEX = "611e00000000000000" # Make sure this is a common one
PAYLOAD_IDLE_BYTES = bytes.fromhex(PAYLOAD_IDLE_HEX)

command_sender_socket = None

def setup_sender_socket():
    global command_sender_socket
    if command_sender_socket:
        try: command_sender_socket.close()
        except: pass
    command_sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    command_sender_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

def send_udp_broadcast(payload_bytes):
    global command_sender_socket
    if not command_sender_socket: setup_sender_socket()
    try:
        command_sender_socket.sendto(payload_bytes, (BROADCAST_IP, UDP_PORT))
        print(f"Sent: {payload_bytes.hex()}")
    except Exception as e:
        print(f"Send UDP Error: {e}")
        setup_sender_socket()

if __name__ == "__main__":
    setup_sender_socket()
    print(f"Using BALL_IP: {BALL_IP}")
    print(f"Idle/Stop payload set to: {PAYLOAD_IDLE_HEX}")
    print(f"Specific Play payload to test: {PAYLOAD_APP_SPECIFIC_PLAY_HEX}")
    print("\nEnsure sequence uploaded.")
    
    try:
        while True:
            action = input("Enter 'p' to play (sends specific observed cmd), 's' to stop, 'q' to quit: ").strip().lower()
            if action == 'p':
                print(f"Sending SPECIFIC PLAY command: {PAYLOAD_APP_SPECIFIC_PLAY_BYTES.hex()}")
                send_udp_broadcast(PAYLOAD_APP_SPECIFIC_PLAY_BYTES)
                # The app then starts sending the modified "611e..." packets.
                # For now, we just send the initial trigger.
            elif action == 's':
                print(f"Sending STOP command: {PAYLOAD_IDLE_BYTES.hex()}")
                send_udp_broadcast(PAYLOAD_IDLE_BYTES)
            elif action == 'q':
                break
            else:
                print("Invalid.")
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        if command_sender_socket:
            command_sender_socket.close()
        print("Script finished.")