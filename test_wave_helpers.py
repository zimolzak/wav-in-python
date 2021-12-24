# py.test --cov=. --cov-report html
import pytest
from wave_helpers import pretty_hex_string, bytes2int_list, ints2dots


def test_pretty_hex_string():
    # with pytest.raises(ValueError):
    #    duh(42)
    assert list(pretty_hex_string("a")) == ["a"]
    assert list(pretty_hex_string("abc")) == ["a", "b", "c"]
    has_wrap = list(pretty_hex_string("a" * 4 * 9))
    assert "a\n" in has_wrap
    # assert list(pretty_hex_string("a" * )) == ["a", "b", "c"]


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
    print("Did %i auto tests of bytes2int_list()" % tests_complete)


def test_ints2dots():
    assert list(ints2dots([3])) == ['X']
    assert len(list(ints2dots([65535]))[0]) == 76
    assert '.' * 10 in list(ints2dots([65535]))[0]
    assert '.' * (75 // 10) in list(ints2dots([65535 // 10]))[0]
