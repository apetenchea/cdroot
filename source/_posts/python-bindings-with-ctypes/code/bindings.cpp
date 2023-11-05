#include "bindings.h"

auto new_fnv() -> fnv::Fnv1a32* {
    return new fnv::Fnv1a32();
}

auto delete_fnv(fnv::Fnv1a32* fnv) -> void {
    delete fnv;
}

void fnv_update_bytes(fnv::Fnv1a32* fnv, const std::uint8_t* data, std::size_t size) {
    fnv->update(data, size);
}

void fnv_update_uint32(fnv::Fnv1a32* fnv, std::uint32_t data) {
    fnv->update(data);
}

void fnv_update_uint64(fnv::Fnv1a32* fnv, std::uint64_t data) {
    fnv->update(data);
}

void fnv_update_float(fnv::Fnv1a32* fnv, float data) {
    fnv->update(data);
}

auto fnv_digest(fnv::Fnv1a32* fnv) -> std::uint32_t {
    return fnv->digest();
}