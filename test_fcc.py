# import pytest
from wave_helpers import pretty_hex_string  # , bytes2int_list, ints2dots


def test_pretty_hex_string():
    # with pytest.raises(ValueError):
    #    duh(42)
    assert list(pretty_hex_string("a")) == ["a"]
