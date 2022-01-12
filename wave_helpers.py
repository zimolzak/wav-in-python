import numpy as np
import matplotlib.pyplot as plt
import wave  # so we can refer to its classes in type hint annotations
from scipy import signal
from typing import Generator
import collections

from printing import pretty_hex_string, ints2dots


def bytes2int_list(byte_list: bytes) -> Generator[int, None, None]:
    """Input a 'bytes' object. Add pairs of bytes together & yield generator of ints.

    :param byte_list: bytes object, like b'#\xff^\xff', usually right out of readframes()
    :return: Yield decoded values (integers 0 to 65535).
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


def run_length_to_bitstream(rl: np.ndarray, values: np.ndarray, v_high: int, v_low: int) -> np.ndarray:
    """Do run length DECODING and map low/high signal to logic 0/1.
    Supposed to leave middle values untouched.
    [1,2,1,1,1] [7,1,7,1,5] -->
    [1 0 0 1 0 5]

    :param rl: Array of run lengths
    :param values: Array of corresponding values (positive ints)
    :param v_high: Value that will be mapped to 1
    :param v_low: Value that will be mapped to 0
    :return: Array of hopefully only {0,1} with runs re-expanded.
    :raises: ValueError if rl not exactly same size as values.
    """
    rl = np.asarray(rl)  # so that technically it works on lists
    values = np.asarray(values)
    if rl.shape != values.shape:
        raise ValueError("rl and values shapes unequal: %s %s" % (str(rl.shape), str(values.shape)))
    high_shifts = np.where(values == v_high, 1 - v_high, 0)
    low_shifts = np.where(values == v_low, 0 - v_low, 0)
    values_edited = values + high_shifts + low_shifts
    # fixme exception (or warn?) if values not in the set {v_high, v_low}
    return np.repeat(values_edited, rl)


def square_up(a: np.ndarray, v_high: int, v_low: int, tolerance: int = 1) -> np.ndarray:
    """Take all elements close to v_high, and nudge them equal to v_high. Same for v_low.
    Makes a nearly square wave into a very square wave.
    Supposed to leave middle ones untouched.
    [1 1 1 1 2 7 7 7 7 6 7 7 7 5 ] -->
     1 1 1 1 1 7 7 7 7 7 7 7 7 5

     :param a: Array of values (usually time series)
     :param v_high: High value to nudge to
     :param v_low: Low value to nudge to
     :param tolerance: How much are you allowed to nudge?
     :return: Array of squared-up values
     :raises: ValueError: if intervals overlap
    """
    if min(v_high + tolerance, v_low + tolerance) >= max(v_high - tolerance, v_low - tolerance):
        raise ValueError("Nudging intervals overlap: %f and %f +/- %f" % (v_low, v_high, tolerance))
    is_high = abs(a - v_high) <= tolerance
    is_low = abs(a - v_low) <= tolerance
    fixed1 = np.where(is_high, v_high, a)
    return np.where(is_low, v_low, fixed1)


def rle(a: np.ndarray) -> tuple:
    """Perform run-length encoding

    :param a: Array of arbitrary numbers, presumably with some repetition.
    :return: Array of run lengths, and array of numbers corresponding to those runs.
    """
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
    """Wrap a Wave_read object with awareness of baud and its sample values."""

    def __init__(self, wav_file: wave.Wave_read,
                 start_sample: int = 0, n_symbols_to_read: int = 750, baud: int = 50) -> None:
        """Decode a portion of an open WAV file to bytes and integer samples.

        Example:
        W = WaveData(fh)
        W.int_list -> [32547, 32606, 32964, 33108, ...]

        :param wav_file: Object opened by wave.open() but not yet read
        :param start_sample: Where in the file to start reading
        :param n_symbols_to_read: How many FSK symbols to read
        :param baud: Rate of FSK symbols per second
        """
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

    def print_summary(self, n_samples_to_plot: int = 15) -> None:
        """Show reasonable data and metadata from a WAV file, in plain text.

        :param n_samples_to_plot: How many WAV samples to display (as numbers and a text graph)
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
    def __init__(self, wave_data: WaveData, seg_per_symbol: int = 3) -> None:
        """Represent results of short-time Fourier transform applied to WAV audio, including spectrogram of max
        intensity frequency over time. Converts high-resolution sample time series to medium-resolution frequency
        time-series.

        Example:
        F = Fourier(W)
        F.max_freq_indices -> [1 1 7 6 7 7 7 7 1 1]
        ...where "1" means 600 Hz, and "7" means 1500 Hz.

        :param wave_data: Object containing list of WAV numeric samples to be processed.
        :param seg_per_symbol: How many FT segments are calculated for each FSK symbol.
        """
        self.n_symbols_actually_read = wave_data.n_symbols_actually_read
        samples_per_symbol = wave_data.sample_rate / wave_data.baud
        self.f, self.t, self.Zxx = signal.stft(wave_data.int_list, fs=wave_data.sample_rate,
                                               nperseg=int(samples_per_symbol / seg_per_symbol))  # important
        # Zxx's first axis is freq, second is times
        self.max_freq_indices = self.Zxx.argmax(0)  # Main output: vector of which freq band is most intense, per time
        # fixme - it is possible I don't understand the "nperseg" parameter.

    def apply_passband(self, lo_freq: float = 400, hi_freq: float = 2000) -> None:
        """Retain only certain rows (frequencies) in the FT and other result matrices/vectors.

        :param lo_freq: Lower cutoff frequency (below this will be blocked)
        :param hi_freq: Higher cutoff frequency
        """
        selected_indices = ((lo_freq < self.f) * (self.f < hi_freq))
        self.f = self.f[selected_indices]
        self.Zxx = np.abs(self.Zxx[selected_indices])
        self.max_freq_indices = self.Zxx.argmax(0)

    def print_summary(self):
        """Show data/metadata on STFT results."""
        print("\n\n# Fourier analysis of FSK\n")
        print("Zxx (FFT result) shape, frequencies * time points:", self.Zxx.shape)
        print("FFT frequencies in pass band:", self.f)
        print("\nFrequency bin values over time:")
        print(self.max_freq_indices)

    def save_plot(self, filename: str) -> None:
        """Render a spectrogram of the complete STFT of WAV data.

        :param filename: Name of the image file where the plot will be saved
        """
        # https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.stft.html
        z_max = np.max(self.Zxx)  # global max just used for plot scale
        plt.pcolormesh(self.t, self.f, self.Zxx, vmin=0, vmax=z_max, shading='gouraud')
        plt.title('STFT Magnitude')
        plt.ylabel('Frequency [Hz]')
        plt.xlabel('Time [sec]')
        plt.savefig(filename)
        # plt.show()

# By spec: FSK shift of 850 Hz. Mine by inspection is about 581 Hz and 1431 Hz
# one symbol is about 450 - 470 samples by inspection
# calculated at 441 samples/symbol
# 11.62 cycles in a low freq symbol, 28.62 in high freq.


class Bitstream:
    def __init__(self, fourier: Fourier) -> None:
        """Convert the medium-resolution frequency time series to low resolution bitstream (FSK symbol time series).

        Often input in fourier.max_freq_indices is like this:
        array([0, 7, 7, 7, 7, 7, 6, 1, 1, 1, 1, 1, 7, 7, 7, 7, 7, 7, 6, 1, 1, 1, 1, 1])
        B = Bitstream(F)
        B.stream -> [1, 0, 1, 0]

        :param fourier: Object containing array of max intensity frequency over time.
        """
        #  elements (segments) per symbol is a critical param.
        #  In theory, could try to auto-set from histogram(rl).
        #  Now we auto-set by knowing N symbols read.
        #  Could also pass this in from knowledge of FFT setup (but it was 2x as much, overlap?).
        self.n_symbols_actually_read = fourier.n_symbols_actually_read
        self.max_freq_indices = fourier.max_freq_indices  # Need to save these to print later.
        self.calculated_seg_per_symbol = len(self.max_freq_indices) / self.n_symbols_actually_read

        # Infer that the 2 most prevalent frequencies are mark and space
        h = np.histogram(self.max_freq_indices, bins=np.arange(15))  # Integer bins. Can ignore h[1].
        least_to_most = h[0].argsort()
        common_val_1 = least_to_most[-1]
        common_val_2 = least_to_most[-2]
        self.low = min(common_val_1, common_val_2)
        self.high = max(common_val_1, common_val_2)
        assert (self.high - self.low) > 1  # fixme - raise exception

        # Compress multiple FT segments into 1 symbol, and map mark/space frequencies to 0/1.
        rl, values = rle(square_up(self.max_freq_indices, self.high, self.low))
        npi = np.vectorize(int)
        rounded = npi(np.around(rl / self.calculated_seg_per_symbol))  # important - shortens all run lengths
        self.stream = run_length_to_bitstream(rounded, values, self.high, self.low)

    def print_summary(self):
        """Show reasonable data/metadata about the bitstream."""
        print("\n\n# Bitstream\n")
        print("Using %i segments / %i symbols = %f seg/sym" %
              (len(self.max_freq_indices), self.n_symbols_actually_read, self.calculated_seg_per_symbol))
        print("Inferred %i is high and %i is low (+/- 1)." % (self.high, self.low))
        print(self.stream)
        print("%i bits" % len(self.stream))
        print()

    def print_shapes(self, array_widths: collections.abc.Iterable) -> None:
        """Print bitstream reshaped in multiple ways. To look for start/stop bits.

        :param array_widths: list, range, or other iterable of matrix widths you want to try
        """
        # fixme - make an 8N1 and 5N1 decoder on B.stream
        # fixme - make guesses about B.stream width
        for n_columns in array_widths:
            # 5N1 = 7
            # 8N1 = 10
            if n_columns == 7:
                print("5N1")
            if n_columns == 10:
                print("8N1")
            n = len(self.stream)
            n_padding = n_columns - (n % n_columns)
            padding = [0] * n_padding
            bitstream_padded = np.append(self.stream, padding)
            n_rows = len(bitstream_padded) // n_columns
            print(np.reshape(bitstream_padded, (n_rows, n_columns)))
            print()


def whole_pipeline(infile: str = 'sample-data.wav', outfile: str = 'stft.png') -> None:
    """Chain together WAV reading, Fourier analysis, and Bitstream detection. Hard code reasonable defaults. Useful
    for main.py or for testing.

    :param infile: Name of input WAV file
    :param outfile: Name of output image file
    """
    with wave.open(infile, 'r') as wav_file:
        W = WaveData(wav_file, start_sample=0, n_symbols_to_read=750, baud=50)
    W.print_summary(n_samples_to_plot=15)

    F = Fourier(W, seg_per_symbol=3)
    F.apply_passband(400, 2000)
    F.print_summary()
    F.save_plot(outfile)

    B = Bitstream(F)
    B.print_summary()
    B.print_shapes(range(5, 12))
