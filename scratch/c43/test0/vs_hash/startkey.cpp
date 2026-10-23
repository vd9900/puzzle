// Harness: VanitySearch start key = sha256(pbkdf2_hmac_sha512(seed,"VanitySearch",2048,64)) written into Int.bits64 (x86 little-endian)
#include <cstdio>
#include <cstdint>
#include <cstring>
#include <string>
#include "sha512.h"
#include "sha256.h"
int main(int argc, char **argv) {
  for (int a = 1; a < argc; a++) {
    std::string seed(argv[a]), salt("VanitySearch");
    unsigned char hseed[64];
    pbkdf2_hmac_sha512(hseed, 64, (const uint8_t *)seed.c_str(), seed.length(), (const uint8_t *)salt.c_str(), salt.length(), 2048);
    uint64_t bits64[5] = {0, 0, 0, 0, 0};
    sha256(hseed, 64, (unsigned char *)bits64);
    printf("%016llx%016llx%016llx%016llx %s\n", (unsigned long long)bits64[3], (unsigned long long)bits64[2],
           (unsigned long long)bits64[1], (unsigned long long)bits64[0], seed.c_str());
  }
}
