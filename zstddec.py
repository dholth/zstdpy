#!/usr/bin/env python

import sys
import pywasm
import os.path

if not len(sys.argv) == 3:
    print("usage: %s [infile.zst] [outfile]" % sys.argv[0])

infile, outfile = sys.argv[1:]


def grow(n):
    print("need more memory", n)


wasm_module = os.path.join(os.path.dirname(__file__), "zstddec.wasm")

vm = pywasm.load(wasm_module, {"env": {"emscripten_notify_memory_growth": grow}})

compressed = open(infile, "rb").read()

compressed_ptr = vm.exec("malloc", [len(compressed)])

# copy data into memory
vm.store.mems[0].data[compressed_ptr : compressed_ptr + len(compressed)] = compressed

decompressed_size = vm.exec(
    "ZSTD_findDecompressedSize", [compressed_ptr, len(compressed)]
)

print("%s -> %s" % (len(compressed), decompressed_size))

decompressed_ptr = vm.exec("malloc", [decompressed_size])

actual_size = vm.exec(
    "ZSTD_decompress",
    [decompressed_ptr, decompressed_size, compressed_ptr, len(compressed)],
)

with open(outfile, "wb+") as victory:
    victory.write(
        vm.store.mems[0].data[decompressed_ptr : decompressed_ptr + decompressed_size]
    )
