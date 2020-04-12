#!/usr/bin/env python
"""
Small decompress-only zstd wrapper.
"""

import io
import shutil

from _dezstd import ffi, lib


class ZSTDDecompressor(io.BufferedIOBase):
    """
    Streaming decompression of one stream.
    """

    def __init__(self, raw):
        self.raw = raw
        self._dctx = lib.ZSTD_createDCtx()
        self._outbuf = bytearray(lib.ZSTD_DStreamOutSize())

    def close(self):
        lib.ZSTD_freeDCtx(self._dctx)
        self._dctx = None

    def write(self, data):
        inbuf = ffi.new("ZSTD_inBuffer*")
        src = ffi.from_buffer(data)
        inbuf.src = src
        inbuf.size = len(src)

        outbuf = ffi.new("ZSTD_outBuffer*")
        dst = ffi.from_buffer(self._outbuf)
        outbuf.dst = dst
        outbuf.size = len(dst)

        while inbuf.pos < inbuf.size:
            outbuf.dst = dst
            outbuf.size = len(dst)
            outbuf.pos = 0

            ret = lib.ZSTD_decompressStream(self._dctx, outbuf, inbuf)
            # CHECK_ZSTD(ret)
            self.raw.write(self._outbuf[: outbuf.pos])


if __name__ == "__main__":
    infile = open("../zstddeclib.c.zst", "rb")
    z = ZSTDDecompressor(open("test.out", "wb+"))
    shutil.copyfileobj(infile, z)
