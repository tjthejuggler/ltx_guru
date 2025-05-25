import socket
import time

BROADCAST_IP = "255.255.255.255"
UDP_PORT = 41412

# === CORRECTED 9-BYTE UDP PAYLOADS ===
PAYLOAD_IDLE_HEX = "61f000000000000000"
PAYLOAD_TRIGGER_INITIAL_HEX = "61fa000000a2ec3500" # This is the one from your screenshot packet 531
# =======================================

# --- Convert hex strings to bytes ---
try:
    payload_idle = bytes.fromhex(PAYLOAD_IDLE_HEX)
    payload_trigger_initial = bytes.fromhex(PAYLOAD_TRIGGER_INITIAL_HEX)
    
    # Sanity check lengths (should be 9 bytes)
    if len(payload_idle) != 9:
        print(f"Warning: Idle payload length is {len(payload_idle)}, expected 9.")
    if len(payload_trigger_initial) != 9:
        print(f"Warning: Trigger payload length is {len(payload_trigger_initial)}, expected 9.")

except ValueError as e:
    print(f"ERROR: Invalid HEX string. Details: {e}")
    exit()

# Global socket to reuse for continuous sending if needed
s = None

def setup_socket():
    global s
    if not s: # Only create if it doesn't exist or was closed
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

def teardown_socket():
    global s
    if s:
        s.close()
        s = None # Mark as closed

def send_udp_broadcast_payload(payload_bytes): # Renamed for clarity
    global s
    setup_socket() # Ensure socket is ready
    try:
        s.sendto(payload_bytes, (BROADCAST_IP, UDP_PORT))
        # print(f"Sent: {payload_bytes.hex()}") # Potentially too verbose for continuous
    except Exception as e:
        print(f"Error sending UDP: {e}")


def trigger_sequence_play_continuous(duration_seconds=5, frequency_hz=2):
    print(f"Sending PLAY command ({payload_trigger_initial.hex()}) continuously for {duration_seconds} seconds ({frequency_hz} Hz)...")
    start_time = time.time()
    interval = 1.0 / frequency_hz
    packets_sent = 0
    while time.time() - start_time < duration_seconds:
        send_udp_broadcast_payload(payload_trigger_initial)
        packets_sent += 1
        time.sleep(interval)
    # teardown_socket() # Keep socket open if stop might be called right after
    print(f"Finished continuous PLAY state. Sent {packets_sent} packets.")

def stop_sequence_play_once():
    print(f"Sending STOP command ({payload_idle.hex()})...")
    send_udp_broadcast_payload(payload_idle) # Send it once
    teardown_socket() # Close socket after stop
    print("STOP command sent.")


if __name__ == "__main__":
    print("Ensure a sequence is uploaded to the ball.")
    
    input("Press Enter to send PLAY command continuously for 5 seconds...")
    trigger_sequence_play_continuous(duration_seconds=5, frequency_hz=2)
    print("PLAY attempt finished. Check the ball.")

    input("Press Enter to send STOP command...")
    stop_sequence_play_once()
    print("STOP attempt finished. Check the ball.")
    
    # Final cleanup if socket was left open by play and stop wasn't called immediately
    teardown_socket() 