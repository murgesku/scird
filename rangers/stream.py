__all__ = [
    "Stream",
    "from_io",
    "from_bytes",
    "from_file",
]

from io import BytesIO, SEEK_CUR, SEEK_END, SEEK_SET
from struct import pack, unpack


class Stream(object):
    """Provide common data types I/O facilities in 'Rangers' style."""
    def __init__(self, io):
        self._io = io

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.close()

    def close(self):
        self._io.close()

    def seek(self, n):
        self._io.seek(n)

    def pos(self):
        return self._io.tell()

    def size(self):
        old_pos = self._io.tell()
        self._io.seek(0, SEEK_END)
        size = self._io.tell()
        self._io.seek(old_pos, SEEK_SET)
        return size

    def write(self, v):
        self._io.write(v)

    def write_bool(self, v: bool):
        self._io.write(pack('<B', int(v)))
    
    def write_byte(self, v: int):
        self._io.write(pack('<B', v))
    
    def write_word(self, v: int):
        self._io.write(pack('<H', v))
    
    def write_int(self, v: int):
        self._io.write(pack('<i', v))
    
    def write_uint(self, v: int):
        self._io.write(pack('<I', v))
    
    def write_single(self, v: float):
        self._io.write(pack('<f', v))
    
    def write_double(self, v: float):
        self._io.write(pack('<d', v))
    
    def write_widestr(self, v: str):
        self._io.write(v.encode('utf-16le'))
        self._io.write(b'\x00\x00')

    def read(self, size) -> bytes:
        return self._io.read(size)

    def read_bool(self) -> bool:
        return unpack('<B', self._io.read(1))[0] == 1

    def read_byte(self) -> int:
        return unpack('<B', self._io.read(1))[0]

    def read_word(self) -> int:
        return unpack('<H', self._io.read(2))[0]

    def read_int(self) -> int:
        return unpack('<i', self._io.read(4))[0]

    def read_uint(self) -> int:
        return unpack('<I', self._io.read(4))[0]

    def read_single(self) -> float:
        return unpack('<f', self._io.read(4))[0]

    def read_double(self) -> float:
        return unpack('<d', self._io.read(8))[0]

    def read_widestr(self) -> str:
        start = self._io.tell()
        size = 0
        while True:
            c = self._io.read(2)
            if c is None or len(c) < 2:
                return ''
            elif c == b'\x00\x00':
                size = self._io.tell() - start - 2
                break
            else:
                continue
        self._io.seek(start)
        s = self._io.read(size).decode('utf-16le')
        self._io.seek(2, SEEK_CUR)
        return s


def from_file(file, mode='rb'):
    f = open(file, mode)
    return Stream(f)


def from_bytes(buf=None):
    if buf is None:
        return Stream(BytesIO())
    else:
        return Stream(BytesIO(buf))


def from_io(io):
    if isinstance(io, Stream):
        return io
    else:
        return Stream(io)