import struct
# gets a 10 byte number that goes directly before the color data starts
def get_color_data_intro(i):
    # Calculate numerical values
    part1 = 304 + (i - 1) * 300
    part2 = 100 * i

    # Pack integers into 4-byte little-endian format
    part1_hex = struct.pack('<I', part1).hex().upper()
    part2_hex = struct.pack('<I', part2).hex().upper()

    # Format hex values with spaces every two characters
    part1_formatted = ' '.join(part1_hex[j:j+2] for j in range(0, 8, 2))
    part2_formatted = ' '.join(part2_hex[j:j+2] for j in range(0, 8, 2))

    return f"{i} = {part1_formatted} {part2_formatted}"

# Example usage:
for num in range(1, 8):
    print(get_color_data_intro(num))