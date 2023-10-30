import ctypes
import pathlib


class Fnv:
    lib = ctypes.CDLL(pathlib.Path().absolute() / 'fnv.dll')

    # auto new_fnv() -> fnv::Fnv1a32*
    lib.new_fnv.restype = ctypes.c_void_p
    lib.new_fnv.argtypes = []

    # void delete_fnv(fnv::Fnv1a32* fnv)
    lib.delete_fnv.restype = None
    lib.delete_fnv.argtypes = [ctypes.c_void_p]

    # void fnv_update_bytes(fnv::Fnv1a32* fnv, const char* data, std::size_t size)
    lib.fnv_update_bytes.restype = None
    lib.fnv_update_bytes.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t]

    # void fnv_update_uint32(fnv::Fnv1a32* fnv, std::uint32_t data)
    lib.fnv_update_uint32.restype = None
    lib.fnv_update_uint32.argtypes = [ctypes.c_void_p, ctypes.c_uint32]

    # void fnv_update_uint64(fnv::Fnv1a32* fnv, std::uint64_t data)
    lib.fnv_update_uint64.restype = None
    lib.fnv_update_uint64.argtypes = [ctypes.c_void_p, ctypes.c_uint64]

    # void fnv_update_float(fnv::Fnv1a32* fnv, float data)
    lib.fnv_update_float.restype = None
    lib.fnv_update_float.argtypes = [ctypes.c_void_p, ctypes.c_float]

    # auto fnv_digest(fnv::Fnv1a32* fnv) -> std::uint32_t
    lib.fnv_digest.restype = ctypes.c_uint32
    lib.fnv_digest.argtypes = [ctypes.c_void_p]

    def __init__(self):
        self._fnv = Fnv.lib.new_fnv()

    def __del__(self):
        Fnv.lib.delete_fnv(self._fnv)

    def update(self, data: bytes | int | float) -> None:
        if type(data) is bytes:
            Fnv.lib.fnv_update_bytes(self._fnv, ctypes.c_char_p(data), ctypes.c_size_t(len(data)))
        elif type(data) is int:
            if data.bit_length() <= 32:
                Fnv.lib.fnv_update_uint32(self._fnv, ctypes.c_uint32(data))
            else:
                Fnv.lib.fnv_update_uint64(self._fnv, ctypes.c_uint64(data))
        elif type(data) is float:
            Fnv.lib.fnv_update_float(self._fnv, ctypes.c_float(data))
        else:
            raise TypeError('data must be bytes, int or float')

    def digest(self) -> int:
        return Fnv.lib.fnv_digest(self._fnv)