#!/usr/bin/env python3

def create_test_sequence():
    # Initialize the sequence with header
    data = bytearray()
    
    # Header
    data.extend(b'PR\x03')  # PR + version 3
    data.extend(b'IN')      # Init marker
    data.extend(b'\x05\x00\x00\x00\x04\x00\x08\x64\x00')  # Config values from original
    
    # PI section (timing info)
    data.extend(b'PI')
    # Using slowest working value (0x01)
    data.extend(b'\x87\x00\x00\x00\x07\x00\x01\x00\x64\x00')  # First block: using 01
    data.extend(b'\xa5\x00\x00\x00\x00\x00\x04\x00\x01\x00\x00\x2c\x01\x00\x00\x01\x00\x64\x00')  # Second block: also using 01
    
    # CD section (color data)
    data.extend(b'CD')
    # Size of color data section (still keeping total size the same)
    data.extend(b'\x2c\x01\x00\x00')  # 300 bytes of color data
    
    # Color data - now repeating each color 20 times before switching
    for _ in range(2):  # Reduced outer loop since we're adding more repetitions
        # Red 20 times
        for _ in range(20):
            data.extend(bytes([0xff, 0x00, 0x00]))  # Red
            data.extend(bytes([0x00, 0x00, 0x00]))  # Padding
        # Blue 20 times
        for _ in range(20):
            data.extend(bytes([0x00, 0x00, 0xff]))  # Blue
            data.extend(bytes([0x00, 0x00, 0x00]))  # Padding
    
    # Add a few more to fill out the remaining space
    for _ in range(10):
        # Red
        data.extend(bytes([0xff, 0x00, 0x00]))
        data.extend(bytes([0x00, 0x00, 0x00]))
        # Blue
        data.extend(bytes([0x00, 0x00, 0xff]))
        data.extend(bytes([0x00, 0x00, 0x00]))
    
    # End marker
    data.extend(b'BT\x00\x00\x00\x00')
    
    return data

if __name__ == '__main__':
    # Create the sequence
    sequence_data = create_test_sequence()
    
    # Write to file
    with open('sequences/test_red_blue_correct_timing.prg', 'wb') as f:
        f.write(sequence_data)
    
    print("Created test sequence file: test_red_blue_correct_timing.prg")
