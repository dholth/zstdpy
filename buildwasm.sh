#!/bin/sh
CC_FLAGS="-Wall -Wextra -Werror -Os -g0 -flto --llvm-lto 3"
emcc -o zstddec.wasm -O2 -s EXPORTED_FUNCTIONS="['_ZSTD_decompress', '_ZSTD_findDecompressedSize', '_ZSTD_isError']" -s ALLOW_MEMORY_GROWTH=1 zstddeclib.c
