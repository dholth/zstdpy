#!/usr/bin/env python
import io
import sys
import wasmer

zstd_bytes = open("zstddec.wasm", "rb").read()
instance = wasmer.Instance(zstd_bytes)

def go():
    e = instance.exports
    m = instance.memory

    buffInSize = e.ZSTD_DStreamInSize()
    buffOutSize = e.ZSTD_DStreamOutSize()

    buffInData = e.malloc(buffInSize)
    buffOutData = e.malloc(buffOutSize)

    inBuffer = e.malloc(32)
    outBuffer = e.malloc(32)

    # struct to pass
    inBufferView = m.uint32_view(offset=inBuffer)
    outBufferView = m.uint32_view(offset=outBuffer)

    inBufferDataView = m.uint8_view(offset=buffInData)
    outBufferDataView = m.uint8_view(offset=buffOutData)

    class ZSTDBuffer:
        def __init__(self, mem, *args):
            self.mem = mem
            self.mem[:3] = [0, 0, 0]
            self.mem[:len(args)] = args

        @property
        def buf(self):
            return self.mem[0]

        @buf.setter
        def buf(self, val):
            print(type(val))
            self.mem[0] = val

        @property
        def size(self):
            return self.mem[1]

        @size.setter
        def size(self, val):
            self.mem[1] = val

        @property
        def pos(self):
            return self.mem[2]

        @buf.setter
        def pos(self, val):
            self.mem[2] = val

    input = ZSTDBuffer(inBufferView, buffInData)

    # the fast way to read memory but not write
    # bytearray(instance.memory.buffer)

    dctx = e.ZSTD_createDCtx()
    assert dctx != 0

    toRead = buffInSize

    example = open("zstddeclib.c.zst", "rb")

    out = []

    while True:
        block = example.read(buffInSize)
        input.buf[0:len(block)] = block
        input.size = len(block)
        break
        while input.pos < input.size:
            output = ZSTDBuffer(outBufferView, buffOutData)
            ret = e.ZSTD_decompressStream(dctx, outBuffer, inBuffer)
            sys.stdout.write(outBufferdata[0:output.pos])

        if not block:
            break

if __name__ == "__main__":
    go()