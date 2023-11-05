#include "fnv.h"

namespace fnv {
auto Fnv1a32::update(const std::uint8_t* data, std::size_t size) -> void {
    for (auto idx = 0u; idx < size; ++idx) {
        _hash ^= data[idx];
        _hash *= FNV_PRIME_32;
    }
}

auto Fnv1a32::digest() const -> std::uint32_t {
    return _hash;
}
}