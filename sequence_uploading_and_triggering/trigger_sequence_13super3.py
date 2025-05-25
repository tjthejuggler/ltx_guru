import socket
import random
import time
import sys
import threading
from datetime import datetime
import pygame # For MP3 playback

# --- Configuration ---
BALL_IP = "192.168.40.133"  # VERIFY THIS IS STILL THE BALL'S CURRENT IP
PC_IP = "" # Leave blank to bind to all interfaces for sniffing
BROADCAST_ADDR = "255.255.255.255" # General broadcast
# BROADCAST_ADDR = "192.168.40.255" # Or, if you know your subnet broadcast
UDP_PORT = 41412
MP3_FILE_PATH = "/home/twain/Projects/ltx_guru/lubalin_you_know_me.mp3" # <--- !!! SET THIS TO YOUR MP3 FILE !!!
# Example: MP3_FILE_PATH = "C:/Users/YourName/Music/track1.mp3"
# Or on Linux/Mac: MP3_FILE_PATH = "/home/yourname/music/track1.mp3"

# NEW: Delay after sending PLAY command before starting MP3. Tune this based on observation.
BALL_STARTUP_DELAY = 0.2  # Seconds 

KNOWN_PLAY_NONCES = {
    # OpID: (Nonce1, Nonce2)
}
# --- End Configuration ---

# --- Globals for threaded sniffer ---
latest_sniffed_data_lock = threading.Lock()
latest_ts_b3 = None
latest_ts_b4 = None
latest_ball_status = None
latest_sniffed_cmd_byte2_val = None # Value from ball's data[10]
sniffer_thread_stop_event = threading.Event()
# ---

def log_print(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    print(f"[{timestamp}] {message}")
    sys.stdout.flush()

def background_sniffer_thread_func():
    global latest_ts_b3, latest_ts_b4, latest_ball_status, latest_sniffed_cmd_byte2_val
    log_print("Sniffer thread started.")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind((PC_IP, UDP_PORT))
        log_print(f"Sniffer bound to {PC_IP if PC_IP else 'all interfaces'}:{UDP_PORT}")
    except OSError as e:
        log_print(f"Critical Sniffer Error: Could not bind sniff socket: {e}. Thread terminating.")
        sniffer_thread_stop_event.set() # Signal main thread if it's waiting
        return
    
    sock.settimeout(1.0) # Timeout to allow checking stop_event

    while not sniffer_thread_stop_event.is_set():
        try:
            data, addr = sock.recvfrom(1024)
            if addr[0] == BALL_IP:
                packet_len = len(data)
                # hex_data = data.hex() # Keep for potential deeper debugging
                
                current_ts_b3, current_ts_b4 = None, None
                current_ball_status, current_cmd_byte2_val = None, None

                if packet_len >= 17: # Ensure packet is long enough for these fields
                    current_ts_b3 = data[15]
                    current_ts_b4 = data[16]
                    current_ball_status = data[12] 
                    current_cmd_byte2_val = data[10]

                    with latest_sniffed_data_lock:
                        latest_ts_b3 = current_ts_b3
                        latest_ts_b4 = current_ts_b4
                        latest_ball_status = current_ball_status
                        latest_sniffed_cmd_byte2_val = current_cmd_byte2_val
                    
                    # Verbose logging for sniffing (can be commented out for cleaner output)
                    # log_print(f"Sniffed Pkt (len {packet_len}): "
                    #           f"Status:{current_ball_status:02x}, CmdByte2Src:{current_cmd_byte2_val:02x}, TS:{current_ts_b3:02x}{current_ts_b4:02x}")

        except socket.timeout:
            continue 
        except Exception as e:
            log_print(f"Error in sniffer thread: {e}")
            time.sleep(0.1) 
    
    sock.close()
    log_print("Sniffer thread stopped.")

def get_latest_sniffed_values():
    with latest_sniffed_data_lock:
        return latest_ball_status, latest_sniffed_cmd_byte2_val, latest_ts_b3, latest_ts_b4

def trigger_play_sequence(play_op_id_byte, pc_nonce_byte1, pc_nonce_byte2):
    log_print(f"Attempting to trigger PLAY (OpID {play_op_id_byte:02x})")
    
    _, _, ts_b3_from_sniffer, ts_b4_from_sniffer = get_latest_sniffed_values()
    
    if ts_b3_from_sniffer is None or ts_b4_from_sniffer is None:
        log_print("No timestamp sniffed yet. Waiting briefly for sniffer...")
        time.sleep(1.6) 
        _, _, ts_b3_from_sniffer, ts_b4_from_sniffer = get_latest_sniffed_values()
        if ts_b3_from_sniffer is None or ts_b4_from_sniffer is None:
            log_print("Still no timestamp from sniffer. Aborting PLAY. Ensure ball is on and broadcasting.")
            return False, False # command_send_success, mp3_start_success

    command_group = 0x61
    command_byte2_to_use = 0x01  # KEY: ALWAYS USE 0x01 FOR SENDING PLAY/STOP
    
    payload = bytes([
        command_group, play_op_id_byte, command_byte2_to_use, 0x00, 0x00,
        pc_nonce_byte1, pc_nonce_byte2, ts_b3_from_sniffer, ts_b4_from_sniffer
    ])
    log_print(f"Preparing Play Command (OpID {play_op_id_byte:02x}, SentCmdByte2 {command_byte2_to_use:02x}, Echoed_TS {ts_b3_from_sniffer:02x}{ts_b4_from_sniffer:02x}). Payload: {payload.hex()}")
    
    send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    send_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    command_send_success = False
    mp3_start_success = False

    try:
        # 1. Send command to the ball
        send_sock.sendto(payload, (BROADCAST_ADDR, UDP_PORT))
        log_print("Play command sent to ball.")
        command_send_success = True

        # 2. Wait for BALL_STARTUP_DELAY for the ball to react before starting MP3
        if command_send_success: # Only proceed if command was sent
            log_print(f"Waiting {BALL_STARTUP_DELAY}s for ball to initialize sequence before starting MP3...")
            time.sleep(BALL_STARTUP_DELAY)

            # 3. Attempt to play MP3
            try:
                if MP3_FILE_PATH and MP3_FILE_PATH != "path/to/your/music.mp3": # Ensure path is set
                    pygame.mixer.music.load(MP3_FILE_PATH)
                    pygame.mixer.music.play()
                    log_print(f"MP3 playback initiated: {MP3_FILE_PATH}")
                    mp3_start_success = True
                else:
                    log_print("MP3_FILE_PATH not set or default, skipping music playback.")
                    # mp3_start_success remains False
            except Exception as e:
                log_print(f"Error starting MP3: {e}")
                # mp3_start_success remains False
        
        return command_send_success, mp3_start_success

    except socket.error as e: # More specific exception for network errors
        log_print(f"Socket error sending Play command: {e}")
        # command_send_success remains False
        # mp3_start_success remains False
        return False, False
    except Exception as e: # Generic exception for other unexpected errors
        log_print(f"Unexpected error during Play sequence: {e}")
        return command_send_success, False # Command might have sent, MP3 likely not
    finally:
        send_sock.close()

def stop_play_sequence(stop_op_id_byte):
    log_print(f"Attempting to trigger STOP (OpID {stop_op_id_byte:02x})")
    
    command_group = 0x61
    command_byte2_to_use = 0x01  # KEY: ALWAYS USE 0x01 FOR SENDING PLAY/STOP

    payload = bytes([
        command_group, stop_op_id_byte, command_byte2_to_use, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00 # v13.1 stop payload (no TS echo)
    ])
    log_print(f"Preparing Stop Command (OpID {stop_op_id_byte:02x}, SentCmdByte2 {command_byte2_to_use:02x}). Payload: {payload.hex()}")
    
    send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    send_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    command_send_success = False
    mp3_stopped_successfully = False
    try:
        send_sock.sendto(payload, (BROADCAST_ADDR, UDP_PORT))
        log_print("Stop command sent.")
        command_send_success = True
        
        # Stop MP3
        try:
            if pygame.mixer.music.get_busy(): 
                pygame.mixer.music.stop()
                log_print("MP3 playback stopped.")
                mp3_stopped_successfully = True
            # else:
                # log_print("MP3 was not playing or already stopped.")
        except Exception as e:
            log_print(f"Error stopping MP3: {e}")
            # mp3_stopped_successfully remains False

        return command_send_success, mp3_stopped_successfully
    except socket.error as e:
        log_print(f"Socket error sending Stop command: {e}")
        return False, False
    except Exception as e:
        log_print(f"Unexpected error during Stop sequence: {e}")
        return False, False # Assume worst case for mp3 stop if command send had issues
    finally:
        send_sock.close()

if __name__ == "__main__":
    script_version = "v17.0_DelayedMP3Start"
    log_print(f"LED Juggling Ball Interactive Control ({script_version})")
    log_print("--------------------------------------------------------------------------------")
    log_print(f"Target Ball IP: {BALL_IP}, UDP Port: {UDP_PORT}")
    log_print(f"PC IP for sniffing: '{PC_IP}' (blank means all available).")
    log_print(f"MP3 File: '{MP3_FILE_PATH}'")
    log_print(f"Ball startup delay for MP3 sync: {BALL_STARTUP_DELAY}s")
    if not (MP3_FILE_PATH and MP3_FILE_PATH != "path/to/your/music.mp3"):
        log_print("WARNING: MP3_FILE_PATH is not set correctly. Music will not play.")
    log_print("Press 'p' to play, 's' to stop, 'q' to quit.")

    try:
        pygame.mixer.init()
        log_print("Pygame mixer initialized.")
    except Exception as e:
        log_print(f"CRITICAL: Failed to initialize pygame.mixer: {e}")
        log_print("MP3 playback will not be available. Exiting.")
        sys.exit(1)

    sniffer_thread = threading.Thread(target=background_sniffer_thread_func, daemon=True)
    sniffer_thread.start()

    op_id_for_next_play = 0x14 
    op_id_of_playing_sequence = 0x00 
    is_playing_assumed = False
    feedback_log = []

    time.sleep(0.5) # Give sniffer a moment

    try:
        while True:
            action_input_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            action_prompt_msg = f"[{action_input_time}] Enter command (p/s/q) [Next PlayOp: {op_id_for_next_play:02x}]: "
            action = input(f"\n{action_prompt_msg}").lower()

            if action == 'p':
                if is_playing_assumed:
                    log_print("Script assumes ball is already playing. Send 's' to stop first.")
                    continue
                
                play_op_to_send = op_id_for_next_play
                p1, p2 = KNOWN_PLAY_NONCES.get(play_op_to_send, 
                                               (random.randint(1, 254), random.randint(1, 254)))
                log_print(f"Using {'KNOWN' if play_op_to_send in KNOWN_PLAY_NONCES else 'RANDOM'} nonce P1=0x{p1:02x}, P2=0x{p2:02x} for Op ID {play_op_to_send:02x}.")

                cmd_sent_ok, mp3_began_ok = trigger_play_sequence(play_op_to_send, p1, p2)
                
                if cmd_sent_ok:
                    op_id_of_playing_sequence = play_op_to_send 
                    is_playing_assumed = True 
                    
                    mp3_status_msg = "MP3 playback initiated" if mp3_began_ok else "MP3 did NOT start (check path/file or error logs)"
                    log_print(f"OBSERVE BALL: Did it play or show red LED? ({mp3_status_msg})")
                    
                    feedback = input("    Did play work (y/n/r=red_led)? ").lower()
                    feedback_log.append(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}] "
                                        f"PLAY OpID {play_op_to_send:02x}, CmdSent: {cmd_sent_ok}, MP3_Began: {mp3_began_ok}, UserFeedback: {feedback}")
                    
                    if feedback == 'n' or feedback == 'r': # Ball play failed or showed error
                        is_playing_assumed = False
                        if mp3_began_ok and pygame.mixer.music.get_busy(): 
                           pygame.mixer.music.stop()
                           log_print("MP3 stopped as ball play reported failed/error by user.")
                else: # Command send failed
                    log_print("Play command send FAILED or aborted. Ball state unknown. MP3 not started.")
                    feedback_log.append(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}] "
                                        f"PLAY OpID {play_op_to_send:02x}, CmdSent: {cmd_sent_ok}, MP3_Began: {mp3_began_ok}, UserFeedback: send_aborted")

            elif action == 's':
                if not is_playing_assumed:
                    force_stop = input("    Script thinks ball is stopped. Force send stop (y/n)? ").lower()
                    if force_stop != 'y':
                        continue
                    log_print(f"Attempting to force stop. Last known playing OpID was {op_id_of_playing_sequence:02x} (this will be used to derive Stop OpID).")
                
                current_stop_op_id = (op_id_of_playing_sequence + 0x0A) & 0xFF 
                
                cmd_sent_ok, mp3_stopped_ok = stop_play_sequence(current_stop_op_id)
                
                if cmd_sent_ok:
                    is_playing_assumed_after_send = False 
                    mp3_status_msg = "MP3 stopped" if mp3_stopped_ok else "MP3 was not playing or error stopping"
                    log_print(f"OBSERVE BALL: Did it stop? ({mp3_status_msg})")
                    
                    feedback = input("    Did stop work (y/n)? ").lower()
                    feedback_log.append(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}] "
                                        f"STOP OpID {current_stop_op_id:02x}, CmdSent: {cmd_sent_ok}, MP3_Stopped: {mp3_stopped_ok}, UserFeedback: {feedback}")
                    
                    if feedback == 'n': # User says stop didn't work
                        is_playing_assumed_after_send = True # Assume it's still playing
                    
                    is_playing_assumed = is_playing_assumed_after_send
                    if not is_playing_assumed: # If stop was successful (or assumed successful)
                        op_id_for_next_play = (op_id_of_playing_sequence + 0x14) & 0xFF
                        if op_id_for_next_play == 0x00: 
                            op_id_for_next_play = 0x14 # Avoid 0x00 as a Play OpID if it's special
                        log_print(f"Stop confirmed or assumed. Next Play Op ID updated to 0x{op_id_for_next_play:02x}")
                else: # Stop command send failed
                    log_print("Stop command send FAILED or aborted. Ball state unknown.")
                    feedback_log.append(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}] "
                                        f"STOP OpID {current_stop_op_id:02x}, CmdSent: {cmd_sent_ok}, MP3_Stopped: {mp3_stopped_ok}, UserFeedback: send_aborted")

            elif action == 'q':
                log_print("Exiting.")
                break
            else:
                log_print("Invalid command. Use 'p', 's', or 'q'.")
    
    except KeyboardInterrupt:
        log_print("\nExiting due to Ctrl-C.")
    except Exception as e:
        log_print(f"\nAn unexpected error occurred in the main loop: {e}")
        import traceback
        traceback.print_exc()
    finally:
        log_print("Stopping sniffer thread...")
        sniffer_thread_stop_event.set()
        if pygame.mixer.get_init(): 
            pygame.mixer.music.stop() 
            pygame.mixer.quit()       
            log_print("Pygame mixer quit.")
        
        if sniffer_thread.is_alive(): # Check if thread is still running
             sniffer_thread.join(timeout=2.0) 
        if sniffer_thread.is_alive():
            log_print("Warning: Sniffer thread did not terminate cleanly.")
        
        log_print("\n--- Feedback Log ---")
        for entry in feedback_log:
            print(entry) 
        log_print("--- Control Script Finished ---")