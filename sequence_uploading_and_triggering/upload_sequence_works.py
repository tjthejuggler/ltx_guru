import socket
import os
import time
import random

# --- Configuration ---
# IMPORTANT: Update these values as needed!
BALL_IP = '192.168.40.205'      # <<<< YOUR BALL IP (from last successful capture)
BALL_TCP_PORT = 8888

# PRG file details (for 4px_blue_10.prg example)
# Update this path if your file is elsewhere
PRG_FILE_ON_DISK = "/home/twain/4px_blue_10.prg"
FILENAME_FOR_HEADER = "4px_blue_10.prg" # Filename as sent in the protocol
# From analysis, for 4px_blue_10.prg (357 bytes on disk),
# the official app sent all 357 bytes of content.
PRG_CONTENT_LENGTH_TO_SEND = 357
# --- End Configuration ---

def generate_random_bytes(length):
    """Generates a specified number of random bytes."""
    return bytes(random.getrandbits(8) for _ in range(length))

def upload_sequence_to_ball(prg_filepath_on_disk,
                            effective_filename_for_header,
                            prg_content_length_to_send,
                            ball_ip=BALL_IP,
                            ball_tcp_port=BALL_TCP_PORT):
    """
    Uploads a sequence file to the ball.

    :param prg_filepath_on_disk: Path to the .prg file on your computer.
    :param effective_filename_for_header: The filename string to embed in the protocol header.
    :param prg_content_length_to_send: The exact number of bytes of PRG content
                                       to send (e.g., full file size or truncated).
    :param ball_ip: IP address of the juggling ball.
    :param ball_tcp_port: TCP port on the ball for uploads (8888).
    :return: True if successful, False otherwise.
    """
    if not os.path.exists(prg_filepath_on_disk):
        print(f"Error: PRG file not found at '{prg_filepath_on_disk}'")
        return False
    if not os.path.isfile(prg_filepath_on_disk):
        print(f"Error: '{prg_filepath_on_disk}' is not a file.")
        return False

    print(f"--- Preparing to upload '{effective_filename_for_header}' from '{prg_filepath_on_disk}' to {ball_ip}:{ball_tcp_port} ---")

    try:
        file_size_on_disk = os.path.getsize(prg_filepath_on_disk)
        print(f"Actual file size of '{prg_filepath_on_disk}' on disk: {file_size_on_disk} bytes.")

        # 1. Construct the 15-byte TCP prefix
        prefix_part1_fixed_nulls = b'\x00\x00\x00\x00'
        prefix_part2_file_size_le = file_size_on_disk.to_bytes(4, 'little') # Original file size
        prefix_part3_nonce = generate_random_bytes(4)
        prefix_part4_fixed_suffix = b'\x20\x00\x00' # Space + 2 nulls

        tcp_dynamic_prefix_15bytes = (
            prefix_part1_fixed_nulls +
            prefix_part2_file_size_le +
            prefix_part3_nonce +
            prefix_part4_fixed_suffix
        )
        print(f"Generated 15-byte dynamic prefix (hex): {tcp_dynamic_prefix_15bytes.hex()}")
        print(f"  Prefix Breakdown: FixedStart={prefix_part1_fixed_nulls.hex()}, "
              f"FileSizeLE={prefix_part2_file_size_le.hex()} (Dec: {file_size_on_disk}), "
              f"Nonce={prefix_part3_nonce.hex()}, FixedEnd={prefix_part4_fixed_suffix.hex()}")

        # 2. Filename string (ASCII encoded)
        filename_bytes = effective_filename_for_header.encode('ascii')
        print(f"Encoded filename '{effective_filename_for_header}' ({len(filename_bytes)} bytes).")

        # 3. Construct the full protocol header
        payload_header = tcp_dynamic_prefix_15bytes + b'\x00' + filename_bytes + b'\x00'
        expected_header_len = 15 + 1 + len(filename_bytes) + 1
        if len(payload_header) != expected_header_len:
            print(f"CRITICAL: Header length mismatch! Expected {expected_header_len}, got {len(payload_header)}")
            return False
        print(f"Constructed payload header ({len(payload_header)} bytes).")

        # 4. Read the PRG file content from disk
        with open(prg_filepath_on_disk, 'rb') as f:
            prg_content_from_file_full = f.read()
        print(f"Read {len(prg_content_from_file_full)} bytes from disk file.")

        # 5. Select the specified portion of PRG content
        if len(prg_content_from_file_full) < prg_content_length_to_send:
            print(f"Warning: File content ({len(prg_content_from_file_full)} bytes) is shorter than "
                  f"the specified PRG content length to send ({prg_content_length_to_send} bytes). "
                  f"Sending only {len(prg_content_from_file_full)} bytes of PRG data.")
            prg_core_data_to_send = prg_content_from_file_full
        elif len(prg_content_from_file_full) > prg_content_length_to_send:
            print(f"Warning: File content ({len(prg_content_from_file_full)} bytes) is longer than "
                  f"the specified PRG content length to send ({prg_content_length_to_send} bytes). "
                  f"Truncating and sending first {prg_content_length_to_send} bytes of PRG data.")
            prg_core_data_to_send = prg_content_from_file_full[:prg_content_length_to_send]
        else:
            prg_core_data_to_send = prg_content_from_file_full
        
        print(f"Selected {len(prg_core_data_to_send)} bytes of PRG core data to send.")

        # 6. Create the full TCP payload
        full_tcp_payload = payload_header + prg_core_data_to_send
        
        expected_total_payload_len = expected_header_len + len(prg_core_data_to_send)
        print(f"Total TCP payload to send: {len(full_tcp_payload)} bytes (Expected: {expected_total_payload_len} bytes)")

        if len(full_tcp_payload) != expected_total_payload_len:
             print(f"CRITICAL: Total payload length construction error! Expected {expected_total_payload_len}, got {len(full_tcp_payload)}")
             return False
        
        # Specific check for the example file based on Wireshark observation
        if effective_filename_for_header == "4px_blue_10.prg" and prg_content_length_to_send == 357:
            if len(full_tcp_payload) != 389: # 15+1+15+1 + 357 = 389
                print(f"CRITICAL INTERNAL ERROR: For 4px_blue_10.prg with 357 data bytes, expected 389 total bytes, got {len(full_tcp_payload)}")
                return False

    except Exception as e:
        print(f"Error preparing TCP payload: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 7. Send the TCP payload
    s = None
    try:
        print(f"Attempting TCP connection to {ball_ip}:{ball_tcp_port}...")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)
        s.connect((ball_ip, ball_tcp_port))
        print("Successfully connected to the ball via TCP.")

        print(f"Sending {len(full_tcp_payload)} bytes of TCP data...")
        s.sendall(full_tcp_payload)
        print(f"All {len(full_tcp_payload)} bytes sent.")

        print("Data sent. Shutting down write access to socket (sending FIN)...")
        s.shutdown(socket.SHUT_WR)

        print("Waiting for ball's ACK and FIN (closing its write side)...")
        s.settimeout(5.0)
        try:
            while True:
                response_chunk = s.recv(1024)
                if not response_chunk:
                    print("Ball closed its side of the TCP connection (received FIN). Upload likely successful.")
                    break
        except socket.timeout:
            print("Timeout waiting for ball's FIN/ACK after shutdown(WR). This might be okay if ball just closes.")
        except Exception as e_recv:
            print(f"Error receiving from ball after shutdown(WR): {e_recv}")

        print(f"--- Upload process for '{effective_filename_for_header}' completed. ---")
        return True

    except socket.timeout:
        print(f"Error: TCP Connection or operation timed out with {ball_ip}:{ball_tcp_port}.")
        return False
    except socket.error as e_sock:
        print(f"TCP Socket error during operation: {e_sock}")
        return False
    except Exception as e_gen:
        print(f"An unexpected error occurred during TCP upload: {e_gen}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if s:
            print("Closing TCP socket.")
            s.close()

if __name__ == "__main__":
    print(f"--- Juggling Ball Sequence Uploader (Upload ONLY) ---")
    print(f"Target Ball IP: {BALL_IP}")
    print(f"PRG File on Disk: {PRG_FILE_ON_DISK}")
    print(f"Filename for Header: {FILENAME_FOR_HEADER}")
    print(f"PRG Content Bytes to Send: {PRG_CONTENT_LENGTH_TO_SEND}")
    
    if not os.path.isfile(PRG_FILE_ON_DISK):
        print(f"CRITICAL ERROR: The PRG file '{PRG_FILE_ON_DISK}' does not exist.")
        print("Please check the 'PRG_FILE_ON_DISK' path in the script.")
    else:
        print(f"\nAttempting to UPLOAD: '{FILENAME_FOR_HEADER}'...")
        upload_successful = upload_sequence_to_ball(
            prg_filepath_on_disk=PRG_FILE_ON_DISK,
            effective_filename_for_header=FILENAME_FOR_HEADER,
            prg_content_length_to_send=PRG_CONTENT_LENGTH_TO_SEND
        )

        if upload_successful:
            print("\nUPLOAD SUCCEEDED (based on TCP communication).")
            print("The ball should now have the sequence. You can verify by:")
            print("  1. Listening to the ball's UDP broadcasts on port 41412.")
            print("     It should contain 'Mupload ok' and the filename.")
            print("  2. Attempting to trigger it with a separate trigger script or the official app.")
        else:
            print("\nUPLOAD FAILED.")
            print("Please check console logs for errors.")

    print("\n--- Upload Script Finished ---")