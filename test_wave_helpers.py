# py.test --cov=. --cov-report html
import pytest  # only need for with pytest.raises(WhateverError):
import numpy as np
import wave

from wave_helpers import bytes2int_list, run_length_to_bitstream, square_up, rle
from wave_helpers import WaveData, Fourier, Bitstream, whole_pipeline


def test_bytes2int_list():
    assert list(bytes2int_list(b'\x00\x80')) == [0]
    assert list(bytes2int_list(b'\x01\x80')) == [1]
    assert list(bytes2int_list(b'\xff\xff')) == [2 ** 15 - 1]  # 32767, midpoint
    assert list(bytes2int_list(b'\x00\x00')) == [2 ** 15]
    assert list(bytes2int_list(b'\xff\x7f')) == [2 ** 16 - 1]  # 65535, max

    # Do all possible 2-byte inputs and check bounds of output.
    tests_complete = 0
    for m in range(256):
        for n in range(256):
            b = bytes([m, n])
            i = list(bytes2int_list(b))[0]
            assert 0 <= i < 2 ** 16
            tests_complete += 1
    print("\n    Did %i auto tests of bytes2int_list()" % tests_complete, end='')


def test_rl2b():
    with pytest.raises(ValueError):
        dummy = run_length_to_bitstream(np.array([5, 5, 1]), np.array([7, 1]), 7, 1)  # throwaway
    bs = run_length_to_bitstream(np.array([5, 5]), np.array([7, 1]), 7, 1)
    assert np.all(bs == np.array([1] * 5 + [0] * 5))


def test_su():
    ary_in = np.array([7] * 5 + [6] + [8] + [1] * 5 + [0])
    ary_out = np.array([7] * 7 + [1] * 6)
    with pytest.raises(ValueError):
        dummy = square_up(ary_in, 7, 1, 10)  # throwaway
    x = square_up(ary_in, 7, 1)
    assert np.all(x == ary_out)


def test_rle():
    values_in = [2, 3, 5]
    rl_in = [4, 7, 11]
    ary_in = np.repeat(values_in, rl_in)
    rl_out, values_out = rle(ary_in)
    assert np.all(rl_out == rl_in) and np.all(values_out == values_in)
    rl_out, values_out = rle(np.array([]))
    assert rl_out is None and values_out is None


def test_bitstream_exception():
    with wave.open('sample-data.wav', 'r') as fh:
        w = WaveData(fh)
    f = Fourier(w)
    f.apply_passband(400, 2000)

    # Deliberately mess up data in `f`
    timeslots = len(f.max_freq_indices)
    a = timeslots // 2
    b = timeslots - a
    f.max_freq_indices = np.array([1] * a + [2] * b)

    with pytest.raises(ValueError):
        dummy = Bitstream(f)  # throwaway


def test_whole_pipeline():
    whole_pipeline(infile='sample-data.wav', outfile='plot_default.png', n_symbols_to_read=100)
    # throwaway return value
    # Quit at 100 symbols = 2 sec, so effectively read the whole of sample-data.wav, which is only 1 sec.
    # fixme - very basic, no asserts at all, just needs to run without error.
