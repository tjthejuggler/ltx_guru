def get_sequence(i):
    """
    Generate the sequence for a given value of i.
    
    For each row i, the sequence contains i pairs of hexadecimal values.
    The first value in each row increases by 0x13 from the previous row's first value.
    Within a row, each value increases by 0x2C from the previous value.
    The second value in each pair is the index (0, 1, 2, etc.).
    
    Examples:
    i=1: 3300
    i=2: 4600, 7201
    i=3: 5900, 8501, B102
    i=4: 6C00, 9801, C402, F003
    i=5: 7F00, AB01, D702, 0303, 2F04
    i=6: 9200, BE01, EA02, 1603, 4204, 6E05
    i=7: A500, D101, FD02, 2903, 5504, 8105, AD06
    """
    sequence = []
    first_value_step = 0x13  # Step between first values of consecutive rows
    within_row_step = 0x2C   # Step between values within the same row
    
    # Calculate the first value for row i
    first_value = 0x33 + (i - 1) * first_value_step
    
    # Generate the sequence for row i
    value = first_value
    for index in range(i):
        # Format as two-digit hex values without '0x' prefix
        sequence.append(f"{value:02X}{index:02X}")
        # Increment value for the next pair in this row
        value = (value + within_row_step) & 0xFF  # Keep within byte range (0-255)
    
    return sequence

# Example usage:
i = 8
result = get_sequence(i)
print(", ".join(result))
