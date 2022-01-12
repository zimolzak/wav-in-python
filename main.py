import sys
import wave
from wave_helpers import file_to_int_list, Fourier, Bitstream
from printing import print_wav_file_basics, try_bitstream_shapes

wav_file = wave.open(sys.argv[1], 'r')  # fixme catch exception, "with"
print_wav_file_basics(wav_file)
sample_rate = wav_file.getframerate()

# Read data out of WAV file.
int_list, n_symbols_actually_read = file_to_int_list(wav_file, start_sample=1, n_symbols_to_read=750, baud=50)

# Short time Fourier transform
F = Fourier(int_list, sample_rate, baud=50, seg_per_symbol=3)
F.apply_passband(400, 2000)
F.print_summary()
F.save_plot('stft.png')

# shift of 850 Hz. Mine by inspection is about 581 Hz and 1431 Hz
# one symbol is about 450 - 470 samples by inspection
# calculated at 441 samples/symbol
# 11.62 cycles in a low freq symbol, 28.62 in high freq.

# Translate FFT data to FSK bitstream
B = Bitstream(F.max_freq_indices, n_symbols_actually_read, elements_per_symbol=3)
B.print_summary()
try_bitstream_shapes(B.stream, 5, 12)
