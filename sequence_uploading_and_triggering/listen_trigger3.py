import socket
import time
import threading

# --- Configuration ---
BALL_IP = "192.168.40.205"  # UPDATE THIS if your ball's IP changes
BROADCAST_IP = "255.255.255.255"
UDP_PORT = 41412
BALL_TCP_CONTROL_PORT = 22067 # The port for the initial TCP "presence" handshake

# This is the "idle" or "stop" payload sent by the app.
# Update this with the most common/current 9-byte idle payload you observe from the official app.
# Example from one of your later screenshots: "611e00000000000000"
PAYLOAD_IDLE_HEX = "611e00000000000000" 
PAYLOAD_IDLE_BYTES = bytes.fromhex(PAYLOAD_IDLE_HEX)

# Globals
last_ball_status_payload = None # Stores the latest 71-byte status (as bytes)
listener_thread_stop_event = threading.Event()
tcp_control_socket = None # For the TCP connection to port 22067
tcp_thread_stop_event = threading.Event()
command_sender_socket = None # For sending UDP broadcasts

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
    except Exception as e:
        print(f"Send UDP Error: {e}")
        setup_sender_socket()

def ball_tcp_controller():
    """Establishes and maintains the TCP connection to the ball's control port."""
    global tcp_control_socket, tcp_thread_stop_event
    
    while not tcp_thread_stop_event.is_set():
        if tcp_control_socket is None: # Try to connect if not already connected
            try:
                print(f"TCP Controller: Attempting to connect to {BALL_IP}:{BALL_TCP_CONTROL_PORT}...")
                temp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                temp_sock.settimeout(5.0) # Connection timeout
                temp_sock.connect((BALL_IP, BALL_TCP_CONTROL_PORT))
                tcp_control_socket = temp_sock # Assign to global on success
                print(f"TCP Controller: Successfully connected to {BALL_IP}:{BALL_TCP_CONTROL_PORT}.")
                # We don't expect to send/receive app data here, just maintain connection
            except socket.timeout:
                print(f"TCP Controller: Connection to {BALL_IP}:{BALL_TCP_CONTROL_PORT} timed out.")
                tcp_control_socket = None # Ensure it's None on failure
                time.sleep(5) # Wait before retrying
                continue
            except ConnectionRefusedError:
                print(f"TCP Controller: Connection to {BALL_IP}:{BALL_TCP_CONTROL_PORT} refused.")
                tcp_control_socket = None
                time.sleep(5) 
                continue
            except Exception as e:
                print(f"TCP Controller: Error connecting - {e}")
                tcp_control_socket = None
                time.sleep(5)
                continue
        
        # If connected, we could periodically check if the socket is still alive
        # For now, we'll just rely on exceptions during send/recv if it dies,
        # or simply keep it open. The OS handles TCP keep-alives.
        # If the app sends TCP keep-alives, we might need to add that here.
        # For now, assume just being connected is enough.
        
        # Check if socket is still valid (a simple way, not foolproof for all disconnects)
        if tcp_control_socket:
            try:
                # Sending 0 bytes can sometimes check connection status without sending actual data
                # However, this might not be universally reliable or might be seen as an error by server
                # A better way might be to try a non-blocking receive or check socket options
                # For simplicity, we'll assume it stays open or errors out on next actual use (if any)
                pass # Just keep it open
            except socket.error:
                print("TCP Controller: TCP connection appears to be broken. Reconnecting...")
                tcp_control_socket.close()
                tcp_control_socket = None
                # Loop will retry connection

        time.sleep(10) # Check/maintain connection periodically or just sleep

    if tcp_control_socket:
        print("TCP Controller: Closing TCP connection.")
        tcp_control_socket.close()
        tcp_control_socket = None
    print("TCP Controller: Stopped.")


def ball_status_listener():
    global last_ball_status_payload, listener_thread_stop_event
    # ... (this function remains largely the same as your last version, 
    #      listening for UDP on port 41412 and updating last_ball_status_payload.
    #      It should now hopefully see 71-byte packets if the TCP connection is up)
    print(f"UDP Listener: Starting for ball status from {BALL_IP} on port {UDP_PORT}...")
    listen_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        listen_sock.bind(("0.0.0.0", UDP_PORT))
        print(f"UDP Listener: Successfully bound.")
    except OSError as e:
        print(f"UDP Listener: CRITICAL BIND ERROR: {e}.")
        listener_thread_stop_event.set()
        return
    listen_sock.settimeout(1.0)
    pk_count = 0

    while not listener_thread_stop_event.is_set():
        try:
            data, addr = listen_sock.recvfrom(1024)
            pk_count += 1
            ip_src, port_src = addr
            len_data = len(data)
            # print(f"UDP Listener PKT#{pk_count}: From {ip_src}:{port_src}, Len={len_data}, Hex={data[:16].hex()}...")

            if ip_src == BALL_IP and port_src == UDP_PORT: # Ball sends from 41412
                if len_data == 71:
                    # print(f"UDP Listener: --- Ball Status (71B) DETECTED ---")
                    last_ball_status_payload = data 
                elif len_data == 47: # Still handle this just in case
                    # print(f"UDP Listener: --- Ball Status (47B) DETECTED ---")
                    if last_ball_status_payload is None or len(last_ball_status_payload) != 71:
                        last_ball_status_payload = data 
                # We don't really care about the ball echoing our commands in this listener
        except socket.timeout:
            continue
        except Exception as e:
            print(f"UDP Listener Recv Error: {e}")
            time.sleep(0.1)
    listen_sock.close()
    print("UDP Listener: Stopped.")


def construct_and_send_play_command():
    global last_ball_status_payload
    play_payload_base_hex = "61fa000000" 
    derived_params_hex = "00000000" # Default/fallback (generic play)

    if last_ball_status_payload is None:
        print("Play CMD: No ball status received yet. Sending generic initial play command.")
    elif len(last_ball_status_payload) == 71:
        print("Play CMD: Using 71-byte ball status to derive play params.")
        s_byte16 = last_ball_status_payload[16] # Byte at offset 16 (0-indexed)
        print(f"Play CMD: Ball status[16] = 0x{s_byte16:02x}")
        if s_byte16 == 0x5e: 
            derived_params_hex = "ff330000"
            print("Play CMD: Matched s_byte16=0x5e, using derived_params=ff330000")
        elif s_byte16 == 0xbb: 
            derived_params_hex = "01040100"
            print("Play CMD: Matched s_byte16=0xbb, using derived_params=01040100")
        else: 
            print(f"Play CMD: Unknown S_byte16 (0x{s_byte16:02x}) in 71B status. Fallback to generic.")
    elif len(last_ball_status_payload) == 47:
        print("Play CMD: Received 47-byte ball status. Derivation logic TBD. Sending generic play.")
    else:
        print(f"Play CMD: Last ball status unexpected length {len(last_ball_status_payload)}B. Generic play.")

    final_play_payload_hex = play_payload_base_hex + derived_params_hex
    play_payload_bytes = bytes.fromhex(final_play_payload_hex)
    print(f"Play CMD: Sending {play_payload_bytes.hex()}")
    send_udp_broadcast(play_payload_bytes)

def stop_sequence_play():
    print(f"Sending STOP command (idle: {PAYLOAD_IDLE_BYTES.hex()})...")
    send_udp_broadcast(PAYLOAD_IDLE_BYTES)

# --- Main ---
if __name__ == "__main__":
    setup_sender_socket() # For UDP broadcasts

    # Start TCP Controller Thread
    tcp_controller_thread = threading.Thread(target=ball_tcp_controller, daemon=True)
    tcp_controller_thread.start()
    print("TCP Controller thread started...")

    # Start UDP Listener Thread
    udp_listener_thread = threading.Thread(target=ball_status_listener, daemon=True)
    udp_listener_thread.start()
    print("UDP Ball status listener started...")
    
    print(f"Using BALL_IP: {BALL_IP}, TCP port: {BALL_TCP_CONTROL_PORT}, UDP port: {UDP_PORT}")
    print(f"Idle/Stop payload set to: {PAYLOAD_IDLE_HEX}")
    time.sleep(2.0) # Give threads a moment to start, TCP to try connecting

    print("\nEnsure a sequence has been uploaded to the ball.")
    
    try:
        while True:
            action = input("Enter 'p' to play, 's' to stop, 'q' to quit: ").strip().lower()
            if action == 'p': 
                construct_and_send_play_command()
            elif action == 's': 
                stop_sequence_play()
            elif action == 'q': 
                break
            else: 
                print("Invalid action.")
    except KeyboardInterrupt: 
        print("\nExiting by user request (Ctrl+C).")
    finally:
        print("Stopping all threads...")
        tcp_thread_stop_event.set()
        listener_thread_stop_event.set()
        
        if tcp_controller_thread.is_alive(): 
            tcp_controller_thread.join(timeout=2.5)
        if udp_listener_thread.is_alive(): 
            udp_listener_thread.join(timeout=2.5)
        
        if command_sender_socket: 
            command_sender_socket.close()
        if tcp_control_socket: # Ensure TCP socket is closed if controller didn't get to it
            try: tcp_control_socket.close()
            except: pass
            
        print("Script finished.")