import socket
import time

BROADCAST_IP = "255.255.255.255"
UDP_PORT = 41412

# --- YOU MUST PROVIDE THESE FROM YOUR WIRESHARK ANALYSIS ---
# Get the *ENTIRE* UDP payload as a hex string from Wireshark's "Data" field

# Hex string for the full UDP payload when app is IDLE
# Example: PAYLOAD_IDLE_HEX = "ffffffff2c7ba01168aabbccddeeff0011223361f000000000000000" 
# THIS IS A PLACEHOLDER - Use your actual observed full idle payload
PAYLOAD_IDLE_HEX = "61f000000000000000"
PAYLOAD_TRIGGER_INITIAL_HEX = "61fa000000a2ec3500" # This is the one from your screenshot packet 531

# --- Convert hex strings to bytes ---
try:
    if PAYLOAD_IDLE_HEX == "YOUR_FULL_IDLE_UDP_PAYLOAD_HEX_STRING_HERE" or \
       PAYLOAD_TRIGGER_INITIAL_HEX == "YOUR_FULL_INITIAL_TRIGGER_UDP_PAYLOAD_HEX_STRING_HERE":
        raise ValueError("Please replace placeholder HEX strings with actual observed values.")
        
    payload_idle = bytes.fromhex(PAYLOAD_IDLE_HEX)
    payload_trigger_initial = bytes.fromhex(PAYLOAD_TRIGGER_INITIAL_HEX) # The first "play" packet you saw
except ValueError as e:
    print(f"ERROR: Invalid HEX string provided. Details: {e}")
    print("Please ensure you've replaced the placeholder hex strings and they are valid.")
    exit()

def send_udp_broadcast(payload_bytes):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) # Allow broadcasting
        s.sendto(payload_bytes, (BROADCAST_IP, UDP_PORT))
        # print(f"Sent: {payload_bytes.hex()} to {BROADCAST_IP}:{UDP_PORT}") # Optional: for debugging
        s.close()
    except Exception as e:
        print(f"Error sending UDP: {e}")

# --- Main Actions ---
def trigger_sequence_play():
    print("Sending PLAY command...")
    send_udp_broadcast(payload_trigger_initial)
    # You might need to send this continuously if the ball requires it.
    # For now, we try sending it once.

def stop_sequence_play():
    print("Sending STOP command (by sending IDLE state)...")
    send_udp_broadcast(payload_idle)

# --- Example Usage ---
if __name__ == "__main__":
    # 1. Make sure a sequence is uploaded to the ball first
    #    (using your TCP upload script or the official app)
    
    print("Ensure a sequence is uploaded to the ball.")
    input("Press Enter to send PLAY command...")
    trigger_sequence_play()
    print("PLAY command sent. Check the ball.")

    input("Press Enter to send STOP command...")
    stop_sequence_play()
    print("STOP command sent. Check the ball.")

    # To mimic continuous play state (if needed):
    # print("\nStarting continuous PLAY state broadcast for 10 seconds...")
    # start_time = time.time()
    # while time.time() - start_time < 10:
    #     # If the trailing bytes in payload_trigger_initial need to change
    #     # (e.g., increment a counter), you'd modify payload_trigger_initial here
    #     # before sending. For now, we send the same one.
    #     send_udp_broadcast(payload_trigger_initial)
    #     time.sleep(0.5) # Send twice a second, adjust as needed
    # print("Finished continuous PLAY state.")
    # stop_sequence_play() # Important to send stop after