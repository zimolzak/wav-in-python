def pretty_hex_string(hs):  # fixme params for 2 and 16 magic nums
    """Input a string and add spaces and newlines every so often."""
    bytes_space = 2  # fixme make a function arg
    bytes_newline = 16
    cs = bytes_space * 2  # chars per space
    cn = bytes_newline * 2  # chars per newline
    for n, c in enumerate(hs):
        # every 16 bytes add a newline
        # fixme insert code here
        if n % cn == cn - 1:
            yield c + "\n"
        elif n % cs == cs - 1:
            # Every 4 char (2 bytes), add a space.
            yield c + " "  # fixme should we yield 2 things?
        else:
            yield c


def bytes2int_list(byte_list):
    for n, b in enumerate(byte_list):
        if n % 2 == 0:
            continue
        else:
            yield 256 * byte_list[n - 1] + byte_list[n]
            # indexing or list() on a 'bytes' obj auto-converts to 'int'


def ints2dots(ints):
    max_int = 256 * 255 + 255  # 65535
    max_spaces = 75
    for x in ints:
        n_spaces = int(x / max_int * max_spaces)
        yield '.' * n_spaces + 'X'
