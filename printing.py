from wave_helpers import bytes2int_list
import numpy as np


def print_wav_file_basics(wav_file, n_frames_to_plot=15, baud=50):
    char_per_byte = 2  # That means hex chars. 1 B = 2 hex digits '01' or '0F' etc.

    # interact with file
    sample_rate = wav_file.getframerate()
    bytes_per_sample = wav_file.getsampwidth()
    wav_file.setpos(0)
    wav_data = wav_file.readframes(n_frames_to_plot)

    # arithmetic
    n_bytes_to_plot = n_frames_to_plot * bytes_per_sample
    n_samples_actually_read = len(wav_data) / bytes_per_sample
    n_symbols_actually_read = n_samples_actually_read / sample_rate * baud
    samples_per_symbol = sample_rate / baud

    # objects for printing
    pretty_hex_list = list(pretty_hex_string(wav_data.hex()))
    int_list = list(bytes2int_list(wav_data))
    dot_list = list(ints2dots(int_list))

    print("Params:\n", wav_file.getparams())
    print()
    print("File duration (s) =", wav_file.getnframes() / sample_rate)
    print("Samples / FSK symbol =", samples_per_symbol)
    print("Bytes in %f FSK symbols =" % n_symbols_actually_read, len(wav_data))
    print("Seconds read =", n_samples_actually_read / sample_rate)
    print()
    print("First %i bytes (%i samples):" % (n_bytes_to_plot, n_frames_to_plot))
    print(wav_data[:n_bytes_to_plot])
    print()
    print(''.join(pretty_hex_list[:n_bytes_to_plot * char_per_byte]))  # pretty hex list
    print()
    print(int_list[:n_bytes_to_plot // bytes_per_sample])  # int list
    print()
    print('\n'.join(dot_list[:n_bytes_to_plot // bytes_per_sample]))  # dot list


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


def try_bitstream_shapes(bitstream, min_columns, max_columns):
    for cols in range(min_columns, max_columns):
        # 5N1 = 7
        # 8N1 = 10
        if cols == 7:
            print("5N1")
        if cols == 10:
            print("8N1")
        n = len(bitstream)
        n_padding = cols - (n % cols)
        padding = [0] * n_padding
        bitstream_padded = np.append(bitstream, padding)
        rows = len(bitstream_padded) // cols
        print(np.reshape(bitstream_padded, (rows, cols)))
        print()
