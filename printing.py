def pretty_hex_string(hs):
    """Input a string. Yield a stream of chars with spaces and newlines added every so often."""
    bytes_space = 2  # fixme make these into function args
    bytes_newline = 16
    cs = bytes_space * 2  # chars per space (4)
    cn = bytes_newline * 2  # chars per newline (32)
    for n, c in enumerate(hs):
        # every 16 bytes add a newline
        if n % cn == cn - 1:
            yield c + "\n"
        elif n % cs == cs - 1:
            # Every 4 char (2 bytes), add a space.
            yield c + " "  # fixme should we yield 2 things?
        else:
            yield c


def ints2dots(ints):
    """Input a list of ints. Yield strings that make a bar graph of the ints."""
    max_int = 256 * 255 + 255  # 65535
    max_spaces = 75
    for x in ints:
        n_spaces = int(x / max_int * max_spaces)
        yield '.' * n_spaces + 'X'
