#!/usr/bin/env python

import cffi

ffibuilder = cffi.FFI()

ffibuilder.cdef(
    """
typedef ... ZSTD_DCtx_s;

typedef struct ZSTD_DCtx_s ZSTD_DCtx;

ZSTD_DCtx* ZSTD_createDCtx(void);
size_t     ZSTD_freeDCtx(ZSTD_DCtx* dctx);

typedef struct ZSTD_inBuffer_s {
  const void* src;
  size_t size;
  size_t pos;
} ZSTD_inBuffer;

typedef struct ZSTD_outBuffer_s {
  void* dst;
  size_t size;
  size_t pos;
} ZSTD_outBuffer;

typedef ZSTD_DCtx ZSTD_DStream;

ZSTD_DStream* ZSTD_createDStream(void);
size_t ZSTD_freeDStream(ZSTD_DStream* zds);
size_t ZSTD_initDStream(ZSTD_DStream* zds);

size_t ZSTD_decompressStream(ZSTD_DStream* zds, ZSTD_outBuffer* output, ZSTD_inBuffer* input);

size_t ZSTD_DStreamInSize(void);
size_t ZSTD_DStreamOutSize(void);
"""
)

ffibuilder.set_source("_dezstd", '#include "zstddeclib.c"')

if __name__ == "__main__":
    ffibuilder.emit_c_code("_dezstd.c")
