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

    Parameters
    ----------
    buffer : object with .write(bytes) method. Receives decompressed data.
    windowLogMax=None: int, or None for the default.
        Select a size limit (in power of 2) beyond which
        the streaming API will refuse to allocate memory buffer
        in order to protect the host from unreasonable memory requirements.
    """

    def __init__(self, buffer, windowLogMax=None):
        self.buffer = buffer
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
            self.buffer.write(self._outbuf[: outbuf.pos])


class ZSTDPullDecompressor(io.RawIOBase):
    """
    Streaming decompression of one stream (pull version)

    Parameters
    ----------
    file : object with .readinto(buffer) method to get compressed data.
    windowLogMax=None: int, or None for the default.
        Select a size limit (in power of 2) beyond which
        the streaming API will refuse to allocate memory buffer
        in order to protect the host from unreasonable memory requirements.
    """

    def __init__(self, file=None, windowLogMax=None):
        self._file = file
        self._dctx = lib.ZSTD_createDCtx()
        if windowLogMax is not None:
            _check_error(
                lib.ZSTD_DCtx_setParameter(
                    self._dctx, lib.ZSTD_d_windowLogMax, windowLogMax
                )
            )

        self._inbuf = bytearray(lib.ZSTD_DStreamInSize())
        self._cinbuf = ffi.new("ZSTD_inBuffer*")
        self._cinbuf.src = ffi.from_buffer(self._inbuf)

    def close(self):
        lib.ZSTD_freeDCtx(self._dctx)
        self._dctx = None

    def write(self, b):
        """
        Write bytes to our internal buffer to be decompressed.

        Returns None unless the internal buffer is empty.
        """
        if self._cinbuf.pos < self._cinbuf.size:
            return None
        size = min(len(b), len(self._inbuf))
        self._inbuf[0:size] = b[:size]
        self._cinbuf.pos = 0
        self._cinbuf.size = size
        return size

    def readinto(self, b):
        """
        Inside-out compared to the ZSTDDecompressor.write() implementation...
        """
        _cinbuf = self._cinbuf
        if not _cinbuf.pos < _cinbuf.size:
            if not self._file:
                return None
            _cinbuf.pos = 0
            _cinbuf.size = self._file.readinto(self._inbuf)

        outbuf = ffi.new("ZSTD_outBuffer*")
        outbuf.pos = 0
        outbuf.dst = ffi.from_buffer(b)
        outbuf.size = len(b)

        # can this return 0 bytes and trick downstream into thinking the file
        # has closed?
        ret = lib.ZSTD_decompressStream(self._dctx, outbuf, self._cinbuf)
        if ret != 0:
            _check_error(ret)

        return outbuf.pos


def pull_version():
    with ZSTDPullDecompressor(open("../zstddeclib.c.zst", "rb")) as z3:
        with io.BytesIO() as outfile:
            shutil.copyfileobj(z3, outfile, length=lib.ZSTD_DStreamOutSize())


def push_version():
    with open("../zstddeclib.c.zst", "rb") as infile:
        with ZSTDDecompressor(io.BytesIO()) as z:
            shutil.copyfileobj(infile, z, length=lib.ZSTD_DStreamInSize())


if __name__ == "__main__":
    try:
        z2 = ZSTDDecompressor(io.BytesIO())
        z2.write(b"not zstd")
    except Exception as e:
        print(e)

    try:
        z3 = ZSTDDecompressor(io.BytesIO(), -1)
    except Exception as e:
        print(e)

    import timeit

    for i in range(10):
        print(
            "push version",
            timeit.timeit("import dezstd; dezstd.push_version()", number=100),
        )
        print(
            "pull version",
            timeit.timeit("import dezstd; dezstd.pull_version()", number=100),
        )
        print()
