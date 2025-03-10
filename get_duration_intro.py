def get_sequence(i):
    """
    Generate the sequence for a given value of i.
    
    For each row i, the sequence contains i pairs of hexadecimal values.
    The first value in each row increases by 0x13 from the previous row's first value.
    Within a row, each value increases by 0x2C from the previous value.
    The second value follows a specific pattern for indices.
    
    Examples:
    i=1: 3300
    i=2: 4600, 7201
    i=3: 5900, 8501, B102
    i=4: 6C00, 9801, C402, F003
    i=5: 7F00, AB01, D702, 0304, 2F05
    i=6: 9200, BE01, EA02, 1604, 4205, 6E06
    i=7: A500, D101, FD02, 2904, 5505, 8106, AD07
    """
    sequence = []
    first_value_step = 0x13  # Step between first values of consecutive rows
    within_row_step = 0x2C   # Step between values within the same row
    
    # Calculate the first value for row i
    first_value = 0x33 + (i - 1) * first_value_step
    
    # Generate the sequence for row i
    value = first_value
    for index in range(i):
        # Determine the second byte (index value) based on the pattern
        if index < 3:
            second_byte = index
        else:
            second_byte = index + 1
        
        # Format as two-digit hex values without '0x' prefix
        sequence.append(f"{value:02X}{second_byte:02X}")
        # Increment value for the next pair in this row
        value = (value + within_row_step) & 0xFF  # Keep within byte range (0-255)
    
    return sequence

# Example usage:
i = 5
result = get_sequence(i)
print(", ".join(result))
