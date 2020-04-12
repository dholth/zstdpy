#!/usr/bin/env python
"""
Small decompress-only zstd wrapper.
"""

import io
import shutil

from _dezstd import ffi, lib


class ZSTDError(ValueError):
    pass


def _check_error(ret):
    if lib.ZSTD_isError(ret):
        error = ffi.string(lib.ZSTD_getErrorName(ret)).decode("utf-8")
        raise ZSTDError(error, ret)


class ZSTDDecompressor(io.BufferedIOBase):
    """
    Streaming decompression of one stream.
    """

    def __init__(self, raw, windowLogMax=None):
        self.raw = raw
        self._dctx = lib.ZSTD_createDCtx()
        if windowLogMax is not None:
            _check_error(
                lib.ZSTD_DCtx_setParameter(
                    self._dctx, lib.ZSTD_d_windowLogMax, windowLogMax
                )
            )
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
            if ret != 0:
                _check_error(ret)
            self.raw.write(self._outbuf[: outbuf.pos])


if __name__ == "__main__":
    infile = open("../zstddeclib.c.zst", "rb")
    z = ZSTDDecompressor(open("test.out", "wb+"))
    shutil.copyfileobj(infile, z, length=lib.ZSTD_DStreamInSize())

    try:
        z2 = ZSTDDecompressor(io.BytesIO())
        z2.write(b"not zstd")
    except Exception as e:
        print(e)

    try:
        z3 = ZSTDDecompressor(io.BytesIO(), -1)
    except Exception as e:
        print(e)
