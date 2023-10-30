from fnv import Fnv


def test_fnv():
    fnv = Fnv()
    fnv.update(b'abcd')
    assert fnv.digest() == 0xce3479bd
