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
    # Modified timing data for slower sequence (1 second intervals)
    data.extend(b'\x87\x00\x00\x00\x07\x00\x01\x00\x64\x00')  # Changed 03 to 01 for timing
    data.extend(b'\xa5\x00\x00\x00\x00\x00\x04\x00\x01\x00\x00\x2c\x01\x00\x00\x01\x00\x64\x00')  # Changed 03 to 01
    
    # CD section (color data)
    data.extend(b'CD')
    # Size of color data section (2 colors repeated 50 times = 100 colors)
    data.extend(b'\x2c\x01\x00\x00')  # 300 bytes of color data
    
    # Color data - alternating red and blue
    for _ in range(50):  # Repeat pattern 50 times
        # Red (ff 00 00)
        data.extend(bytes([0xff, 0x00, 0x00]))
        data.extend(bytes([0x00, 0x00, 0x00]))  # Padding to match original format
        # Blue (00 00 ff)
        data.extend(bytes([0x00, 0x00, 0xff]))
        data.extend(bytes([0x00, 0x00, 0x00]))  # Padding to match original format
    
    # End marker
    data.extend(b'BT\x00\x00\x00\x00')
    
    return data

if __name__ == '__main__':
    # Create the sequence
    sequence_data = create_test_sequence()
    
    # Write to file
    with open('sequences/test_red_blue_slow.prg', 'wb') as f:
        f.write(sequence_data)
    
    print("Created test sequence file: test_red_blue_slow.prg")
