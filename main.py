import sys
import wave
from scipy import signal
import numpy as np
from wave_helpers import bytes2int_list, freqs2bits, file_to_int_list
from printing import print_wav_file_basics, try_bitstream_shapes, plot_fourier_data

wav_file = wave.open(sys.argv[1], 'r')  # fixme catch exception, "with"
print_wav_file_basics(wav_file)

# Free parameters
start_sample = 1  # 3080 is start of good mark/space in sample-data.wav
baud = 50  # symbol / sec
n_symbols_to_read = baud * 15  # 15 sec
seg_per_symbol = 3  # for STFT / FFT

# can't do without these, but move into other funcs later
sample_rate = wav_file.getframerate()
samples_per_symbol = sample_rate / baud


int_list, n_symbols_actually_read = file_to_int_list(wav_file, start_sample=1, n_symbols_to_read=750, baud=50)


# Short time Fourier transform

f, t, Zxx = signal.stft(int_list, fs=sample_rate, nperseg=int(samples_per_symbol / seg_per_symbol))  # important (baud, sample rate, seg per symbol, int list, pass, pass)
# Zxx first axis is freq, second is times
# fixme - it is possible I don't understand the "nperseg" parameter.
selected_indices = ((400 < f) * (f < 2000))
f_filtered = f[selected_indices]
Zxx_filtered = np.abs(Zxx[selected_indices])


max_freq_indices = Zxx_filtered.argmax(0)  # list of which freq band is most intense, per time

print("\n\n# Fourier decoding of FSK\n")
print("Zxx (FFT result) shape, frequencies X time points:", Zxx.shape)
print("FFT frequencies in pass band:", f_filtered)
plot_fourier_data(f_filtered, t, Zxx_filtered, 'stft.png')
# shift of 850 Hz. Mine by inspection is about 581 Hz and 1431 Hz
# one symbol is about 450 - 470 samples by inspection
# calculated at 441 samples/symbol
# 11.62 cycles in a low freq symbol, 28.62 in high freq.

print("\nFrequency bin values over time:")
print("One FFT segment MAYBE = %f ms = %i samples NOT REALLY" %
      (1000 / (baud * seg_per_symbol), samples_per_symbol / seg_per_symbol))
print(max_freq_indices)
print("\nBitstream:")
calculated_seg_per_symbol = len(max_freq_indices) / n_symbols_actually_read
print("Using %i segments / %i symbols = %f seg/sym" %
      (len(max_freq_indices), n_symbols_actually_read, calculated_seg_per_symbol))
bitstream, hi, lo = freqs2bits(max_freq_indices, calculated_seg_per_symbol)  # important
print("Inferred %i is high and %i is low (+/- 1)." % (hi, lo))
print(bitstream)
print()

try_bitstream_shapes(bitstream, 5, 12)
