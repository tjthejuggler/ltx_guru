import socket
import time
import threading

# --- Configuration ---
BALL_IP = "192.168.40.205"  # UPDATE THIS if your ball's IP changes
BROADCAST_IP = "255.255.255.255"
UDP_PORT = 41412

# This is the "idle" or "stop" payload sent by the app.
# Update this with the most common/current 9-byte idle payload you observe from the official app.
# Example from one of your later screenshots: "611e00000000000000"
PAYLOAD_IDLE_HEX = "611e00000000000000" 
PAYLOAD_IDLE_BYTES = bytes.fromhex(PAYLOAD_IDLE_HEX)

# Global to store the last known status from the ball (as bytes)
last_ball_status_payload = None
listener_thread_stop_event = threading.Event() # Event to signal the listener thread to stop

# Global socket for sending commands (to avoid creating/closing it repeatedly)
command_sender_socket = None

def setup_sender_socket():
    """Initializes or re-initializes the global command sender socket."""
    global command_sender_socket
    if command_sender_socket:
        try:
            command_sender_socket.close() # Close if already open, to be safe
        except:
            pass
    command_sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    command_sender_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

def send_udp_broadcast(payload_bytes):
    """Sends a UDP broadcast packet using the global sender socket."""
    global command_sender_socket
    if not command_sender_socket:
        setup_sender_socket() # Ensure socket is ready
    
    try:
        command_sender_socket.sendto(payload_bytes, (BROADCAST_IP, UDP_PORT))
        # print(f"Sent: {payload_bytes.hex()} to {BROADCAST_IP}:{UDP_PORT}") # Uncomment for debugging
    except Exception as e:
        print(f"Error sending UDP: {e}")
        # Attempt to re-initialize socket on error, in case it got closed/invalidated
        setup_sender_socket()


def ball_status_listener():
    global last_ball_status_payload, listener_thread_stop_event
    
    print(f"Listener: Attempting to bind to 0.0.0.0:{UDP_PORT}...")
    listen_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        listen_sock.bind(("0.0.0.0", UDP_PORT))
        print(f"Listener: Successfully bound to 0.0.0.0:{UDP_PORT}")
    except OSError as e:
        print(f"Listener: CRITICAL ERROR binding socket: {e}.")
        listener_thread_stop_event.set() 
        return
        
    listen_sock.settimeout(1.0) 
    packet_count = 0

    while not listener_thread_stop_event.is_set():
        try:
            data, addr = listen_sock.recvfrom(1024) # Increased buffer just in case
            packet_count += 1
            received_from_ip = addr[0]
            received_from_port = addr[1]
            
            print(f"Listener: PKT #{packet_count} RECVD from {received_from_ip}:{received_from_port}, len={len(data)}, data_hex_start={data[:12].hex()}...")

            if received_from_ip == BALL_IP and received_from_port == UDP_PORT and len(data) == 71:
                print(f"Listener: --- Ball Status MATCHED (71 bytes from {BALL_IP}) ---")
                last_ball_status_payload = data
            # Optional: Check for app's 9-byte packets if you want to see them too
            # elif received_from_ip == "192.168.40.40" and len(data) == 9:
            #     print(f"Listener: --- App Command DETECTED (9 bytes) ---")

        except socket.timeout:
            continue 
        except Exception as e:
            print(f"Listener: Error during recvfrom: {e}")
            time.sleep(0.1) 
            
    listen_sock.close()
    print("Listener: Stopped.")

def construct_and_send_play_command():
    """
    Constructs and sends the 9-byte PLAY command.
    It attempts to derive parameters from the last ball status.
    """
    global last_ball_status_payload
    
    play_payload_base_hex = "61fa000000" # First 5 bytes of the play command
    derived_params_hex = "00000000"      # Default/fallback for the last 4 bytes

    if last_ball_status_payload is None:
        print("Play CMD: No ball status received yet. Sending generic initial play command.")
        # This was App Pkt 496, might be a "play last loaded" or "initiate play mode"
        # derived_params_hex remains "00000000"
    elif len(last_ball_status_payload) == 71:
        # We have a ball status, let's try to derive the play command params
        # S1 (Ball Pkt 501) had byte 16 (0-indexed) = 0x5e -> App derived ff330000
        # S2 (Ball Pkt 515) had byte 16 (0-indexed) = 0xbb -> App derived 01040100
        s_byte16 = last_ball_status_payload[16] # Get the byte at offset 16
        
        print(f"Play CMD: Using last ball status. Byte[16] of ball status = 0x{s_byte16:02x}")

        if s_byte16 == 0x5e:
            derived_params_hex = "ff330000"
            print("Play CMD: Matched s_byte16=0x5e, using derived_params=ff330000")
        elif s_byte16 == 0xbb:
            derived_params_hex = "01040100"
            print("Play CMD: Matched s_byte16=0xbb, using derived_params=01040100")
        # TODO: Add more elif conditions here if we find other S_byte16 -> P_derived mappings
        # from more Wireshark analysis.
        else:
            print(f"Play CMD: Unknown S_byte16 value 0x{s_byte16:02x}. Sending generic (fallback) play.")
            # Fallback to generic play's derived part (all zeros) or a common one.
            derived_params_hex = "00000000" 
    else:
        print(f"Play CMD: Last ball status is not 71 bytes (is {len(last_ball_status_payload)}B). Sending generic play.")
        derived_params_hex = "00000000"

    final_play_payload_hex = play_payload_base_hex + derived_params_hex
    play_payload_bytes = bytes.fromhex(final_play_payload_hex)
    
    print(f"Play CMD: Sending {play_payload_bytes.hex()}")
    send_udp_broadcast(play_payload_bytes)


def stop_sequence_play():
    """Sends the STOP command (which is an IDLE state packet)."""
    print(f"Sending STOP command (using idle: {PAYLOAD_IDLE_BYTES.hex()})...")
    send_udp_broadcast(PAYLOAD_IDLE_BYTES)


if __name__ == "__main__":
    # Initialize the sender socket once
    setup_sender_socket()

    # Start the listener thread
    listener_thread = threading.Thread(target=ball_status_listener, daemon=True)
    listener_thread.start()
    print("Ball status listener started in background.")
    print(f"Will listen for ball status from {BALL_IP} and send commands via broadcast.")
    print(f"Make sure your 'PAYLOAD_IDLE_HEX' is set to a currently observed idle packet from the app (e.g., {PAYLOAD_IDLE_HEX}).")
    time.sleep(1.5) # Give listener a moment to start up and potentially get an initial status

    print("\nEnsure a sequence has been uploaded to the ball (e.g., via official app or TCP script).")
    
    try:
        while True:
            action = input("Enter 'p' to play, 's' to stop, 'q' to quit: ").strip().lower()
            if action == 'p':
                construct_and_send_play_command()
                # The app sends play state continuously. For now, we send once.
                # If needed, add a loop here to resend for a duration.
            elif action == 's':
                stop_sequence_play()
            elif action == 'q':
                break
            else:
                print("Invalid action. Please enter 'p', 's', or 'q'.")
    except KeyboardInterrupt:
        print("\nExiting by user request (Ctrl+C).")
    finally:
        print("Stopping listener thread...")
        listener_thread_stop_event.set() # Signal listener thread to stop
        if listener_thread.is_alive():
            listener_thread.join(timeout=2.5) # Wait for listener to finish
        
        if command_sender_socket: # Clean up the sender socket
            command_sender_socket.close()
            
        print("Script finished.")