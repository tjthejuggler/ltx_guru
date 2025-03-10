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
    # First timing block - 1 second timing (0x0A = 10 * 0.1s)
    data.extend(bytes([0x87, 0x00, 0x00, 0x00]))  # Length/offset
    data.extend(bytes([0x07, 0x00]))              # Config
    data.extend(bytes([0x0A, 0x00]))              # Timing multiplier (1 second)
    data.extend(bytes([0x64, 0x00]))              # Base timing unit
    
    # Second timing block (matches structure from original)
    data.extend(bytes([0xa5, 0x00, 0x00, 0x00]))  # Length/offset
    data.extend(bytes([0x00, 0x00]))              # Config
    data.extend(bytes([0x04, 0x00]))              # Config
    data.extend(bytes([0x01, 0x00]))              # Config
    data.extend(bytes([0x00, 0x2c, 0x01, 0x00]))  # Size/length
    data.extend(bytes([0x00, 0x0A, 0x00]))        # Timing multiplier (1 second)
    data.extend(bytes([0x64, 0x00]))              # Base timing unit
    
    # CD section (color data)
    data.extend(b'CD')
    # Size of color data section (2 colors repeated 50 times = 100 colors)
    data.extend(b'\x2c\x01\x00\x00')  # 300 bytes of color data
    
    # Color data - alternating green and red
    for _ in range(50):  # Repeat pattern 50 times
        # Green (00 ff 00)
        data.extend(bytes([0x00, 0xff, 0x00]))
        data.extend(bytes([0x00, 0x00, 0x00]))  # Padding to match original format
        # Red (ff 00 00)
        data.extend(bytes([0xff, 0x00, 0x00]))
        data.extend(bytes([0x00, 0x00, 0x00]))  # Padding to match original format
    
    # End marker
    data.extend(b'BT\x00\x00\x00\x00')
    
    return data

if __name__ == '__main__':
    import os
    
    # Create the sequence
    sequence_data = create_test_sequence()
    
    # Ensure sequences directory exists
    os.makedirs('sequences', exist_ok=True)
    
    # Write to file
    output_file = 'sequences/1g_1r_10x.prg'
    with open(output_file, 'wb') as f:
        f.write(sequence_data)
    
    print(f"Created sequence file: {output_file}")
    print(f"File size: {os.path.getsize(output_file)} bytes")
