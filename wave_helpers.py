import numpy as np
import wave  # so we can refer to classes in annotations
from scipy import signal
import matplotlib.pyplot as plt
from typing import Generator

from printing import pretty_hex_string, ints2dots


def bytes2int_list(byte_list: bytes) -> Generator[int, None, None]:
    """Input a 'bytes' object. Add pairs of bytes together & yield generator of ints.

    :param byte_list: bytes object, like b'#\xff^\xff', usually right out of readframes()
    """
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


class WaveData:
    def __init__(self, wav_file: wave.Wave_read, start_sample=0, n_symbols_to_read=750, baud=50):
        self.wav_file = wav_file
        self.baud = baud

        # Derived and calculated vars
        self.sample_rate = wav_file.getframerate()
        self.bytes_per_sample = wav_file.getsampwidth()
        self.samples_per_symbol = self.sample_rate / baud
        n_samples_to_read = int(self.samples_per_symbol * n_symbols_to_read)

        # Read from file
        wav_file.setpos(start_sample)
        self.wav_bytes = wav_file.readframes(n_samples_to_read)  # important op, maybe catch exceptions?

        # Usual results
        self.n_samples_actually_read = len(self.wav_bytes) / self.bytes_per_sample
        self.n_symbols_actually_read = self.n_samples_actually_read / self.sample_rate * baud
        self.int_list = list(bytes2int_list(self.wav_bytes))

    def print_summary(self, n_samples_to_plot=15):
        """Reasonable metadata about WAV file, and text description of some of its data.

        :param n_samples_to_plot: How many WAV samples to display (as numbers, text graph)
        """
        char_per_byte = 2  # That means hex chars. 1 B = 2 hex digits '01' or '0F' etc.
        n_bytes_to_plot = n_samples_to_plot * self.bytes_per_sample

        # objects for printing
        pretty_hex_list = list(pretty_hex_string(self.wav_bytes.hex()))
        dot_list = list(ints2dots(self.int_list))

        print("\n\n# WAV file information\n")
        print("Params:\n", self.wav_file.getparams())
        print()
        print("File duration (s) =", self.wav_file.getnframes() / self.sample_rate)
        print("Samples / FSK symbol =", self.samples_per_symbol)
        print("Bytes in %f FSK symbols =" % self.n_symbols_actually_read, len(self.wav_bytes))
        print("Seconds read =", self.n_samples_actually_read / self.sample_rate)
        print()
        print("First %i bytes (%i samples):" % (n_bytes_to_plot, n_samples_to_plot))
        print(self.wav_bytes[:n_bytes_to_plot])
        print()
        print(''.join(pretty_hex_list[:n_bytes_to_plot * char_per_byte]))  # pretty hex list
        print()
        print(self.int_list[:n_samples_to_plot])  # int list
        print()
        print('\n'.join(dot_list[:n_samples_to_plot]))  # dot list


class Fourier:
    def __init__(self, wave_data: WaveData, seg_per_symbol=3):
        self.n_symbols_actually_read = wave_data.n_symbols_actually_read
        samples_per_symbol = wave_data.sample_rate / wave_data.baud
        self.f, self.t, self.Zxx = signal.stft(wave_data.int_list, fs=wave_data.sample_rate,
                                               nperseg=int(samples_per_symbol / seg_per_symbol))
        # Zxx's first axis is freq, second is times
        self.max_freq_indices = self.Zxx.argmax(0)  # Main output: list of which freq band is most intense, per time
        # fixme - it is possible I don't understand the "nperseg" parameter.

    def apply_passband(self, lo_freq=400, hi_freq=2000):
        selected_indices = ((lo_freq < self.f) * (self.f < hi_freq))
        self.f = self.f[selected_indices]
        self.Zxx = np.abs(self.Zxx[selected_indices])
        self.max_freq_indices = self.Zxx.argmax(0)

    def print_summary(self):
        print("\n\n# Fourier analysis of FSK\n")
        print("Zxx (FFT result) shape, frequencies * time points:", self.Zxx.shape)
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
    def __init__(self, fourier):
        """Take Fourier object and output bitstream.
        Often input in fourier.max_freq_indices is like this:
        array([0, 7, 7, 7, 7, 7, 6, 1, 1, 1, 1, 1, 7, 7, 7, 7, 7, 7, 6, 1, 1, 1, 1, 1])
        """
        #  elements (segments) per symbol is a critical param.
        #  In theory, could try to auto-set from histogram(rl).
        #  Now we auto-set by knowing N symbols read.
        #  Could also pass this in from knowledge of FFT setup (but it was 2x as much, overlap?).
        self.n_symbols_actually_read = fourier.n_symbols_actually_read
        self.max_freq_indices = fourier.max_freq_indices  # need to save it for print later.
        self.calculated_seg_per_symbol = len(self.max_freq_indices) / self.n_symbols_actually_read
        h = np.histogram(self.max_freq_indices, bins=np.arange(15))  # Integer bins. Can ignore h[1].
        least_to_most = h[0].argsort()
        common_val_1 = least_to_most[-1]
        common_val_2 = least_to_most[-2]
        self.low = min(common_val_1, common_val_2)
        self.high = max(common_val_1, common_val_2)
        assert (self.high - self.low) > 1
        rl, values = rle(square_up(self.max_freq_indices, self.high, self.low))
        npi = np.vectorize(int)
        rounded = npi(np.around(rl / self.calculated_seg_per_symbol))  # shortens all run lengths
        self.stream = run_length_to_bitstream(rounded, values, self.high, self.low)

    def print_summary(self):
        print("\n\n# Bitstream\n")
        print("Using %i segments / %i symbols = %f seg/sym" %
              (len(self.max_freq_indices), self.n_symbols_actually_read, self.calculated_seg_per_symbol))
        print("Inferred %i is high and %i is low (+/- 1)." % (self.high, self.low))
        print(self.stream)
        print("%i bits" % len(self.stream))
        print()

    def print_shapes(self, column_widths):
        # fixme - make an 8N1 and 5N1 decoder on B.stream
        # fixme - make guesses about B.stream width
        for cols in column_widths:
            # 5N1 = 7
            # 8N1 = 10
            if cols == 7:
                print("5N1")
            if cols == 10:
                print("8N1")
            n = len(self.stream)
            n_padding = cols - (n % cols)
            padding = [0] * n_padding
            bitstream_padded = np.append(self.stream, padding)
            rows = len(bitstream_padded) // cols
            print(np.reshape(bitstream_padded, (rows, cols)))
            print()
