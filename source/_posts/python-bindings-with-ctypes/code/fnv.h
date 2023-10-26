#pragma once

#include <cstdint>
#include <cstdlib>

namespace fnv {
constexpr auto OFFSET_BIAS_32 = 2166136261u;
constexpr auto FNV_PRIME_32 = 16777619u;

class Fnv1a32 {
public:
  auto update(const char* data, std::size_t size) -> void;

  template<class T>
  auto update(const T& data) -> void {
    update(reinterpret_cast<const char*>(&data), sizeof(data));
  }

  auto digest() const -> std::uint32_t;

private:
  std::uint32_t _hash{OFFSET_BIAS_32};
};
}