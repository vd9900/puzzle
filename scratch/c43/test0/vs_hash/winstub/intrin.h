// Linux stand-ins for the MSVC intrinsics used by VanitySearch v1.0 hash code
#pragma once
#include <cstdint>
#include <cstddef>
#include <x86intrin.h>
static inline uint32_t _byteswap_ulong(uint32_t x) { return __builtin_bswap32(x); }
static inline uint64_t _byteswap_uint64(uint64_t x) { return __builtin_bswap64(x); }
static inline uint64_t _rotr64(uint64_t x, int n) { return (x >> n) | (x << (64 - n)); }
#include <cstdio>
#define __declspec(x)
#define sprintf_s snprintf
