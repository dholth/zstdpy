dezstd
======

dezsd wraps the Zstandard decompression-only library for streaming decompression. It may be useful when the additional size of a full-featured compressor/decompressor would be inconvenient.

usage
-----

::

  import dezstd, io
  output = io.BytesIO()
  z = dezstd.ZSTDDecompressor(output)
  z.write(b"(\xb5/\xfd\x04Xa\x00\x00hello hello\n\xffz\xd5\x1a")
  print(output.getvalue().decode('utf-8'))
  # hello hello

license
-------

dezstd includes the BSD-licensed Zstandard software. The unique parts of dezstd are made available under the 0BSD license.
