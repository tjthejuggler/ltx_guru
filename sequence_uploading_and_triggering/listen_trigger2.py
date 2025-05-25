import socket
import time
import threading

# --- Configuration ---
BALL_IP = "192.168.40.205"  # <<< Your current ball IP
BROADCAST_IP = "255.255.255.255"
UDP_PORT = 41412
APP_IP = "192.168.40.40" # Your desktop IP

PAYLOAD_IDLE_HEX = "611e00000000000000" # Update with current app's idle
#PAYLOAD_IDLE_BYTES = bytes.fromhex(PAYLOAD_IDLE_HEX)

last_ball_status_payload = None
listener_thread_stop_event = threading.Event()
command_sender_socket = None

APP_IDLE_PING_HEX = "611e00000000000000" # Example, verify this!
APP_IDLE_PING_BYTES = bytes.fromhex(APP_IDLE_PING_HEX)

# PAYLOAD_IDLE_BYTES for our script's STOP command can be the same
PAYLOAD_IDLE_BYTES = APP_IDLE_PING_BYTES

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

def ball_status_listener():
    global last_ball_status_payload, listener_thread_stop_event
    print(f"Listener: Binding to 0.0.0.0:{UDP_PORT} for packets from {BALL_IP} or {APP_IP}")
    listen_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        listen_sock.bind(("0.0.0.0", UDP_PORT))
        print(f"Listener: Successfully bound.")
    except OSError as e:
        print(f"Listener: CRITICAL BIND ERROR: {e}")
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
            print(f"Listener PKT#{pk_count}: From {ip_src}:{port_src}, Len={len_data}, Hex={data[:16].hex()}...") # Print more info

            if ip_src == BALL_IP and port_src == UDP_PORT:
                if len_data == 71:
                    print(f"Listener: --- Ball Status (71B) DETECTED ---")
                    last_ball_status_payload = data # This is what we want for deriving play cmd
                elif len_data == 47:
                    print(f"Listener: --- Ball Status (47B) DETECTED --- Hex: {data.hex()}")
                    # If this is the new status, we need to analyze IT
                    # For now, we still prioritize the 71-byte one if seen
                    if last_ball_status_payload is None or len(last_ball_status_payload) != 71 : # Prioritize 71B if available
                         last_ball_status_payload = data # Tentatively use 47B if no 71B seen yet
                elif len_data == 9 and data.startswith(bytes.fromhex("61fa")): # Ball echoing play cmd
                     print(f"Listener: --- Ball Echoed Play CMD (9B) --- Hex: {data.hex()}")
                else:
                    print(f"Listener: Ball packet of unexpected length {len_data}")

        except socket.timeout:
            continue
        except Exception as e:
            print(f"Listener Recv Error: {e}")
            time.sleep(0.1)
    listen_sock.close()
    print("Listener: Stopped.")

def construct_and_send_play_command():
    global last_ball_status_payload
    
    play_payload_base_hex = "61fa000000" 
    
    # --- TEMPORARY TEST ---
    # Try sending a known good derived parameter set that worked for the official app
    # when it received a 71-byte status.
    # Will the ball accept this even if it's currently sending 47-byte statuses?
    # known_good_derived_params_hex = "ff330000" # From official app's Pkt 514
    known_good_derived_params_hex = "01040100" # From official app's Pkt 516
    
    print(f"Play CMD: TESTING with PREVIOUSLY OBSERVED good derived_params: {known_good_derived_params_hex}")
    # --- END TEMPORARY TEST ---

    # Comment out the derivation logic for now
    # derived_params_hex = "00000000" # Default/fallback
    # if last_ball_status_payload is None:
    #     print("Play CMD: No ball status received yet. Sending generic initial play command.")
    # elif len(last_ball_status_payload) == 71: # We have the rich 71-byte status
    #     # ... (71-byte derivation logic would go here if we had it) ...
    #     print("Play CMD: Logic for 71B status not fully implemented. Fallback.")
    # elif len(last_ball_status_payload) == 47: # We have the shorter 47-byte status
    #     print("Play CMD: Using 47-byte ball status. Derivation logic TBD for this format.")
    #     print(f"Play CMD: 47B Ball Status Hex: {last_ball_status_payload.hex()}")
    # else:
    #     print(f"Play CMD: Last ball status is of unexpected length {len(last_ball_status_payload)}B. Generic play.")

    final_play_payload_hex = play_payload_base_hex + known_good_derived_params_hex # Use the hardcoded one
    play_payload_bytes = bytes.fromhex(final_play_payload_hex)
    
    print(f"Play CMD: Sending {play_payload_bytes.hex()}")
    send_udp_broadcast(play_payload_bytes)

def stop_sequence_play():
    print(f"Sending STOP command (idle: {PAYLOAD_IDLE_BYTES.hex()})...")
    send_udp_broadcast(PAYLOAD_IDLE_BYTES)

app_pinger_stop_event = threading.Event()

def official_app_idle_pinger():
    """Periodically sends the official app's idle/ping packet."""
    print("Pinger: Starting to send app's idle ping periodically...")
    while not app_pinger_stop_event.is_set():
        send_udp_broadcast(APP_IDLE_PING_BYTES)
        # The official app likely sends these ~1-2 times per second
        time.sleep(0.7) # Adjust frequency as needed
    print("Pinger: Stopped.")


if __name__ == "__main__":
    setup_sender_socket()

    listener_thread = threading.Thread(target=ball_status_listener, daemon=True)
    listener_thread.start()
    print("Ball status listener started...")

    pinger_thread = threading.Thread(target=official_app_idle_pinger, daemon=True)
    pinger_thread.start()
    print("Official App idle pinger started...")
    
    time.sleep(2.0) # Give listener and pinger a moment

    print(f"\nUsing BALL_IP: {BALL_IP}")
    print(f"Idle/Stop payload (and periodic ping) set to: {APP_IDLE_PING_HEX}")
    print("\nEnsure sequence uploaded.")
    
    try:
        while True:
            action = input("Enter 'p' to play, 's' to stop, 'q' to quit: ").strip().lower()
            if action == 'p':
                # Important: Stop the pinger BEFORE sending play, 
                # as the app itself would stop its idle ping when sending a play command
                app_pinger_stop_event.set() 
                pinger_thread.join(timeout=1.0) # Wait for pinger to stop
                print("Pinger: Stopped by play command.")

                construct_and_send_play_command()
                
                # After sending play, the official app would then send PLAY state packets continuously.
                # For now, our script sends one derived play.
                # We might need to restart a "play pinger" if play needs continuous refresh.
                # For simplicity, we'll restart the idle pinger after a delay if not quitting.
                
            elif action == 's':
                app_pinger_stop_event.set()
                if pinger_thread.is_alive(): pinger_thread.join(timeout=1.0)
                print("Pinger: Stopped by stop command.")
                
                stop_sequence_play() # Sends the PAYLOAD_IDLE_BYTES (same as APP_IDLE_PING_BYTES)
                
                # Restart idle pinger after stop
                if not app_pinger_stop_event.is_set(): # Should be true unless we are quitting
                    app_pinger_stop_event.clear()
                    pinger_thread = threading.Thread(target=official_app_idle_pinger, daemon=True)
                    pinger_thread.start()
                    print("Pinger: Restarted after stop.")

            elif action == 'q':
                break
            else:
                print("Invalid.")
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        print("Stopping all threads...")
        app_pinger_stop_event.set()
        listener_thread_stop_event.set()
        if pinger_thread.is_alive(): pinger_thread.join(timeout=1.5)
        if listener_thread.is_alive(): listener_thread.join(timeout=1.5)
        if command_sender_socket: command_sender_socket.close()
        print("Script finished.")