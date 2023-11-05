from fnv import Fnv


def test_fnv_bytes():
    fnv = Fnv()
    fnv.update(b'abcd')
    assert fnv.digest() == 0xce3479bd


def test_fnv_int():
    fnv = Fnv()
    fnv.update(0x12121212)
    assert fnv.digest() == 0x1c411b85
