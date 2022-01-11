import numpy as np


def bytes2int_list(byte_list):
    """Input a 'bytes' object. Add pairs of bytes together & yield generator of ints."""
    # fixme - there may be a pre-made "decode" way to do this.
    for n, b in enumerate(byte_list):
        if n % 2 == 0:
            continue
        else:
            # yield 256 * byte_list[n - 1] + byte_list[n]  # the other endian
            raw_int = 256 * byte_list[n] + byte_list[n - 1]
            midpoint = 2 ** 15
            if raw_int >= midpoint:
                scaled_int = raw_int - midpoint
            else:
                scaled_int = raw_int + midpoint
            yield scaled_int
            # indexing or list() on a 'bytes' obj auto-converts to 'int'


def file_to_int_list(wav_file, start_sample, n_symbols_to_read, baud):
    # Calculated and derived vars
    sample_rate = wav_file.getframerate()
    bytes_per_sample = wav_file.getsampwidth()
    samples_per_symbol = sample_rate / baud
    n_samples_to_read = int(samples_per_symbol * n_symbols_to_read)

    # Read from file
    wav_file.setpos(start_sample)
    wav_data = wav_file.readframes(n_samples_to_read)
    n_samples_actually_read = len(wav_data) / bytes_per_sample
    n_symbols_actually_read = n_samples_actually_read / sample_rate * baud
    int_list = list(bytes2int_list(wav_data))
    return int_list, n_symbols_actually_read


def freqs2bits(freq_list, elements_per_symbol=3):
    """Take np.array and output bitstream.
    Often input is like this:
    array([0, 7, 7, 7, 7, 7, 6, 1, 1, 1, 1, 1, 7, 7, 7, 7, 7, 7, 6, 1, 1, 1, 1, 1])
    """
    # fixme - elements_per_symbol is a critical param.
    #  In theory, could try to auto-set from histogram(rl).
    h = np.histogram(freq_list, bins=np.arange(15))  # Integer bins. Can ignore h[1].
    least_to_most = h[0].argsort()
    common_val_1 = least_to_most[-1]
    common_val_2 = least_to_most[-2]
    low = min(common_val_1, common_val_2)
    high = max(common_val_1, common_val_2)
    assert (high - low) > 1
    rl, values = rle(square_up(freq_list, high, low))
    npi = np.vectorize(int)
    rounded = npi(np.around(rl / elements_per_symbol))  # shortens all run lengths
    return run_length_to_bitstream(rounded, values, high, low), high, low


def run_length_to_bitstream(rl, values, v_high, v_low):
    """Do run length DECODING and map low/high signal to logic 0/1.
    Supposed to leave middle ones untouched.
    [1,2,1,1,1] [7,1,7,1,5] -->
    [1 0 0 1 0 5]
    """
    # fixme - weird results if pass list instead of np.array
    high_shifts = np.where(values == v_high, 1 - v_high, 0)
    low_shifts = np.where(values == v_low, 0 - v_low, 0)
    values_edited = values + high_shifts + low_shifts
    return np.repeat(values_edited, rl)


def square_up(a, v_high, v_low):
    """Move all elements within 1.0 of v_high to v_high, etc.
    Supposed to leave middle ones untouched.
    [1 1 1 1 2 7 7 7 7 6 7 7 7 5 ] -->
     1 1 1 1 1 7 7 7 7 7 7 7 7 5
    """
    is_high = abs(a - v_high) <= 1
    is_low = abs(a - v_low) <= 1
    fixed1 = np.where(is_high, v_high, a)
    return np.where(is_low, v_low, fixed1)


def rle(a):
    # https://newbedev.com/find-length-of-sequences-of-identical-values-in-a-numpy-array-run-length-encoding
    ia = np.asarray(a)
    n = len(ia)
    if n == 0:
        return None, None
    else:
        there_is_transition = ia[1:] != ia[:-1]  # pairwise unequal (string safe)
        transition_locations = np.append(np.where(there_is_transition), n - 1)  # must include last element pos
        run_lengths = np.diff(np.append(-1, transition_locations))
        # p = np.cumsum(np.append(0, run_lengths))[:-1]  # positions
        return run_lengths, ia[transition_locations]
