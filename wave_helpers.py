import numpy as np
from scipy import signal
import matplotlib.pyplot as plt


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


class Fourier:
    def __init__(self, int_list, sample_rate, baud, seg_per_symbol=3):
        samples_per_symbol = sample_rate / baud
        self.f, self.t, self.Zxx = signal.stft(int_list, fs=sample_rate, nperseg=int(
            samples_per_symbol / seg_per_symbol))
        # Zxx's first axis is freq, second is times
        self.max_freq_indices = self.Zxx.argmax(0)  # list of which freq band is most intense, per time
        # fixme - it is possible I don't understand the "nperseg" parameter.

    def apply_passband(self, lo_freq=400, hi_freq=2000):
        selected_indices = ((lo_freq < self.f) * (self.f < hi_freq))
        self.f = self.f[selected_indices]
        self.Zxx = np.abs(self.Zxx[selected_indices])
        self.max_freq_indices = self.Zxx.argmax(0)

    def print_summary(self):
        print("\n\n# Fourier decoding of FSK\n")
        print("Zxx (FFT result) shape, frequencies X time points:", self.Zxx.shape)
        print("FFT frequencies in pass band:", self.f)
        print("\nFrequency bin values over time:")
        print(self.max_freq_indices)

    def save_plot(self, filename):
        # https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.stft.html
        z_max = np.max(self.Zxx)  # global max just used for plot scale
        plt.pcolormesh(self.t, self.f, self.Zxx, vmin=0, vmax=z_max, shading='gouraud')
        plt.title('STFT Magnitude')
        plt.ylabel('Frequency [Hz]')
        plt.xlabel('Time [sec]')
        plt.savefig(filename)
        # plt.show()


class Bitstream:
    def __init__(self, fourier, n_symbols_actually_read, elements_per_symbol=3):
        """Take np.array and output bitstream.
        Often input is like this:
        array([0, 7, 7, 7, 7, 7, 6, 1, 1, 1, 1, 1, 7, 7, 7, 7, 7, 7, 6, 1, 1, 1, 1, 1])
        """
        # fixme - elements_per_symbol is a critical param.
        #  In theory, could try to auto-set from histogram(rl).
        self.n_symbols_actually_read = n_symbols_actually_read
        self.max_freq_indices = fourier.max_freq_indices  # need to save it for print later.
        self.calculated_seg_per_symbol = len(self.max_freq_indices) / n_symbols_actually_read
        h = np.histogram(self.max_freq_indices, bins=np.arange(15))  # Integer bins. Can ignore h[1].
        least_to_most = h[0].argsort()
        common_val_1 = least_to_most[-1]
        common_val_2 = least_to_most[-2]
        self.low = min(common_val_1, common_val_2)
        self.high = max(common_val_1, common_val_2)
        assert (self.high - self.low) > 1
        rl, values = rle(square_up(self.max_freq_indices, self.high, self.low))
        npi = np.vectorize(int)
        rounded = npi(np.around(rl / elements_per_symbol))  # shortens all run lengths
        self.stream = run_length_to_bitstream(rounded, values, self.high, self.low)

    def print_summary(self):
        print("\n\n# Bitstream\n")
        print("Using %i segments / %i symbols = %f seg/sym" %
              (len(self.max_freq_indices), self.n_symbols_actually_read, self.calculated_seg_per_symbol))
        print("Inferred %i is high and %i is low (+/- 1)." % (self.high, self.low))
        print(self.stream)
        print()
