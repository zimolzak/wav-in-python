from printing import pretty_hex_string, ints2dots


def test_pretty_hex_string():
    # with pytest.raises(ValueError):
    #    duh(42)
    assert list(pretty_hex_string("a")) == ["a"]
    assert list(pretty_hex_string("abc")) == ["a", "b", "c"]
    has_wrap = list(pretty_hex_string("a" * 4 * 9))
    assert "a\n" in has_wrap
    # assert list(pretty_hex_string("a" * )) == ["a", "b", "c"]


def test_ints2dots():
    assert list(ints2dots([3])) == ['X']
    assert len(list(ints2dots([65535]))[0]) == 76
    assert '.' * 10 in list(ints2dots([65535]))[0]
    assert '.' * (75 // 10) in list(ints2dots([65535 // 10]))[0]
