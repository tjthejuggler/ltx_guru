import os
import subprocess
import binascii
import tempfile

def get_hex_dump(data):
    """Converts binary data to a hex dump string."""
    return binascii.hexlify(data).decode('ascii')

def run_tests():
    """
    Runs tests by comparing the output of prg_generator.py with corresponding .prg files.
    """
    tests_directory = '/home/twain/Projects/ltx_guru/tests'
    prg_generator_script_name = 'prg_generator.py' # Keep it simple
    
    # Determine paths relative to this script's location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    prg_generator_script = os.path.join(script_dir, prg_generator_script_name)

    # Attempt to locate 'tests' directory relative to script_dir or its parent
    # This makes the script more portable if it's moved along with prg_generator.py and tests/
    potential_tests_dir_1 = os.path.join(script_dir, 'tests') # tests/ alongside this script
    potential_tests_dir_2 = os.path.join(os.path.dirname(script_dir), 'tests') # tests/ alongside parent of this script

    if os.path.isdir(tests_directory): # Explicit path first
        pass # Use the hardcoded path
    elif os.path.isdir(potential_tests_dir_1):
        tests_directory = potential_tests_dir_1
    elif os.path.isdir(potential_tests_dir_2):
        tests_directory = potential_tests_dir_2
    else:
        print(f"Error: Could not automatically locate tests directory. Tried: {tests_directory}, {potential_tests_dir_1}, {potential_tests_dir_2}")
        return

    if not os.path.exists(prg_generator_script):
        # Fallback if prg_generator.py is not next to run_prg_tests.py
        # Try the original hardcoded path if it exists
        hardcoded_prg_generator_path = '/home/twain/Projects/ltx_guru/prg_generator.py'
        if os.path.exists(hardcoded_prg_generator_path):
            prg_generator_script = hardcoded_prg_generator_path
        else:
            print(f"Error: prg_generator.py not found. Tried: {prg_generator_script} and {hardcoded_prg_generator_path}")
            return

    print(f"Looking for tests in: {tests_directory}")
    print(f"Using prg_generator: {prg_generator_script}")
    print("-" * 30)

    if not os.path.isdir(tests_directory): # Re-check after potential adjustments
        print(f"Error: Final tests directory not found at {tests_directory}")
        return

    json_files_found = False
    for filename in sorted(os.listdir(tests_directory)):
        if filename.endswith(".json"):
            json_files_found = True
            json_filepath = os.path.join(tests_directory, filename)
            base_name = filename[:-5]
            prg_filename = base_name + ".prg"
            prg_filepath = os.path.join(tests_directory, prg_filename)

            print(f"Test case: {base_name}")

            if not os.path.exists(prg_filepath):
                print(f"  SKIPPED: Corresponding .prg file '{prg_filename}' not found.")
                print("-" * 30)
                continue

            temp_output_prg_path = None  # Initialize for cleanup
            try:
                # Create a temporary file for prg_generator.py to write to
                # delete=False is needed because prg_generator.py opens it by path
                with tempfile.NamedTemporaryFile(delete=False, suffix=".prg") as tmp_file:
                    temp_output_prg_path = tmp_file.name
                
                # Inner try for subprocess and file operations
                try:
                    process = subprocess.run(
                        ['python3', prg_generator_script, json_filepath, temp_output_prg_path],
                        capture_output=True,
                        check=True,
                        text=True, # For easier debugging of prg_generator's prints
                        timeout=20 # Slightly longer timeout
                    )
                    # If prg_generator.py prints to stdout (e.g. its own verbose logs), show them
                    # if process.stdout:
                    #     print(f"    prg_generator stdout:\n{process.stdout.strip()}")
                    # if process.stderr: # Should be empty on success due to check=True
                    #     print(f"    prg_generator stderr:\n{process.stderr.strip()}")


                    with open(temp_output_prg_path, 'rb') as f_gen:
                        generated_prg_data = f_gen.read()
                    generated_hex = get_hex_dump(generated_prg_data)

                    with open(prg_filepath, 'rb') as f_exp:
                        expected_prg_data = f_exp.read()
                    expected_hex = get_hex_dump(expected_prg_data)

                    if generated_prg_data == expected_prg_data:
                        print(f"  PASS: Output matches {prg_filename}")
                    else:
                        print(f"  FAIL: Output does NOT match {prg_filename}")
                        len_gen = len(generated_prg_data)
                        len_exp = len(expected_prg_data)
                        print(f"    Generated Length: {len_gen}, Expected Length: {len_exp}")
                        
                        if len_gen != len_exp:
                            print(f"    Files differ in length.")
                        
                        # Find first differing byte
                        limit = min(len_gen, len_exp)
                        first_diff_offset = -1
                        for i in range(limit):
                            if generated_prg_data[i] != expected_prg_data[i]:
                                first_diff_offset = i
                                break
                        
                        if first_diff_offset != -1:
                            context_bytes = 10 # Number of bytes before and after the diff point
                            start_ctx = max(0, first_diff_offset - context_bytes)
                            end_ctx_gen = min(len_gen, first_diff_offset + context_bytes + 1)
                            end_ctx_exp = min(len_exp, first_diff_offset + context_bytes + 1)

                            gen_byte_hex = f"{generated_prg_data[first_diff_offset]:02X}"
                            exp_byte_hex = f"{expected_prg_data[first_diff_offset]:02X}"
                            print(f"    First difference at offset {first_diff_offset} (0x{first_diff_offset:X}):")
                            print(f"      Generated: {gen_byte_hex}")
                            print(f"      Expected:  {exp_byte_hex}")
                            
                            print(f"      Context (Generated): ...{binascii.hexlify(generated_prg_data[start_ctx:end_ctx_gen]).decode('ascii')}...")
                            print(f"      Context (Expected):  ...{binascii.hexlify(expected_prg_data[start_ctx:end_ctx_exp]).decode('ascii')}...")

                        elif len_gen != len_exp: # No byte diff found up to min_len, but lengths differ
                             if len_gen > len_exp:
                                 print(f"    Generated file is longer. First extra byte at offset {limit} (0x{limit:X}): {generated_prg_data[limit]:02X}")
                             else:
                                 print(f"    Expected file is longer. First extra byte at offset {limit} (0x{limit:X}): {expected_prg_data[limit]:02X}")
                                 
                except subprocess.CalledProcessError as e:
                    print(f"  ERROR: prg_generator.py execution failed for {filename}.")
                    print(f"    Return code: {e.returncode}")
                    if e.stdout:
                        print(f"    Stdout from prg_generator:\n{e.stdout}")
                    if e.stderr:
                        print(f"    Stderr from prg_generator:\n{e.stderr}")
                except subprocess.TimeoutExpired:
                    print(f"  ERROR: prg_generator.py timed out for {filename}.")
                except FileNotFoundError as e: # e.g. if temp_output_prg_path somehow vanishes
                    print(f"  ERROR: File not found during test for {filename}: {e}")
                except Exception as e:
                    print(f"  ERROR: An unexpected error occurred while processing {filename}: {e}")
            
            finally:
                # Clean up the temporary file if it was created
                if temp_output_prg_path and os.path.exists(temp_output_prg_path):
                    os.remove(temp_output_prg_path)
            
            print("-" * 30)
    
    if not json_files_found:
        print(f"No .json files found in {tests_directory}")

if __name__ == "__main__":
    run_tests()