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
    # if i do this line instead of the line above then it just stays as solid blue the whole time and never changes, but with the line the way it is above it strobes as blue for awhile and then strobes as red for awhile
    # (b'\x87\x00\x00\x00\x07\x00\x01\x00\x64\x00')
    data.extend(b'\xa5\x00\x00\x00\x00\x00\x04\x00\x01\x00\x00\x2c\x01\x00\x00\x01\x00\x64\x00')  # Second block: also using 01
    
    # CD section (color data)
    data.extend(b'CD')
    # Size of color data section (2 colors repeated 50 times = 100 colors)
    data.extend(b'\x2c\x01\x00\x00')  # 300 bytes of color data
    
    # Color data - repeating each color 10 times before switching
    for _ in range(5):  # Outer loop 5 times
        # Red 10 times
        for _ in range(10):
            data.extend(bytes([0xff, 0x00, 0x00]))  # Red
            data.extend(bytes([0x00, 0x00, 0x00]))  # Padding
        # Blue 10 times
        for _ in range(10):
            data.extend(bytes([0x00, 0x00, 0xff]))  # Blue
            data.extend(bytes([0x00, 0x00, 0x00]))  # Padding
    
    # End marker
    data.extend(b'BT\x00\x00\x00\x00')
    
    return data

if __name__ == '__main__':
    # Create the sequence
    sequence_data = create_test_sequence()
    
    # Write to file
    with open('sequences/test_red_blue_repeated.prg', 'wb') as f:
        f.write(sequence_data)
    
    print("Created test sequence file: test_red_blue_repeated.prg")
