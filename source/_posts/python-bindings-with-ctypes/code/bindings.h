#pragma once

#include "fnv.h"

#if defined(_WIN32) || defined(_WIN64)
  #define EXPORT __declspec(dllexport)
#else
  #define EXPORT
#endif

extern "C" {
  EXPORT auto new_fnv() -> fnv::Fnv1a32*;
  EXPORT void delete_fnv(fnv::Fnv1a32* fnv);
  EXPORT void fnv_update_bytes(fnv::Fnv1a32* fnv, const std::uint8_t* data, std::size_t size);
  EXPORT void fnv_update_uint32(fnv::Fnv1a32* fnv, std::uint32_t data);
  EXPORT void fnv_update_uint64(fnv::Fnv1a32* fnv, std::uint64_t data);
  EXPORT void fnv_update_float(fnv::Fnv1a32* fnv, float data);
  EXPORT auto fnv_digest(fnv::Fnv1a32* fnv) -> std::uint32_t;
}