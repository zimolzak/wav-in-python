import sys
import wave
from wave_helpers import freqs2bits, file_to_int_list, Fourier
from printing import print_wav_file_basics, try_bitstream_shapes

wav_file = wave.open(sys.argv[1], 'r')  # fixme catch exception, "with"
print_wav_file_basics(wav_file)

# Free parameters
start_sample = 1  # 3080 is start of good mark/space in sample-data.wav
baud = 50  # symbol / sec
n_symbols_to_read = baud * 15  # 15 sec
seg_per_symbol = 3  # for STFT / FFT

# can't do without these, but move into other funcs later
sample_rate = wav_file.getframerate()

int_list, n_symbols_actually_read = file_to_int_list(wav_file, start_sample=1, n_symbols_to_read=750, baud=50)

# Short time Fourier transform

F = Fourier(int_list, sample_rate, baud=50)

F.apply_passband(400, 2000)

max_freq_indices = F.Zxx.argmax(0)  # list of which freq band is most intense, per time

F.print_summary()

F.save_plot('stft.png')

# shift of 850 Hz. Mine by inspection is about 581 Hz and 1431 Hz
# one symbol is about 450 - 470 samples by inspection
# calculated at 441 samples/symbol
# 11.62 cycles in a low freq symbol, 28.62 in high freq.

print("\nFrequency bin values over time:")
print(max_freq_indices)

# bitstream ########

print("\nBitstream:")
calculated_seg_per_symbol = len(max_freq_indices) / n_symbols_actually_read
print("Using %i segments / %i symbols = %f seg/sym" %
      (len(max_freq_indices), n_symbols_actually_read, calculated_seg_per_symbol))
bitstream, hi, lo = freqs2bits(max_freq_indices, calculated_seg_per_symbol)  # important
print("Inferred %i is high and %i is low (+/- 1)." % (hi, lo))
print(bitstream)
print()

try_bitstream_shapes(bitstream, 5, 12)
