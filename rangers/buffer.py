__all__ = [
    "Buffer",
    "from_bytes",
    "from_file",
]

from io import BytesIO, SEEK_CUR, SEEK_END, SEEK_SET
import zlib

from .stream import Stream


class Buffer(Stream):
    """
    Provide common data types I/O facilities with in-memory buffer.
    """

    def __init__(self, initial_bytes=b''):
        super().__init__(BytesIO(initial_bytes))

    @staticmethod
    def _rand31pm(seed):
        """
        :type seed: int
        :rtype : int
        """
        while True:
            hi, lo = divmod(seed, 0x1f31d)
            seed = lo * 0x41a7 - hi * 0xb14
            if seed < 1:
                seed += 0x7fffffff
            yield seed - 1

    def cipher(self, key, size=-1):
        """
        :type key: int
        :type size: int
        """
        if size == -1:
            size = self.size() - self.pos()
        gen = self._rand31pm(key)
        begin = self.pos()
        end = begin + size
        view = self._io.getbuffer()
        for i in range(begin, end):
            view[i] = view[i] ^ (next(gen) & 255)
        self._io.seek(size, SEEK_CUR)

    def decipher(self, key, size=-1):
        """
        :type key: int
        :type size: int
        """
        if size == -1:
            size = self.size() - self.pos()
        gen = self._rand31pm(key)
        begin = self.pos()
        end = begin + size
        view = self._io.getbuffer()
        for i in range(begin, end):
            view[i] = view[i] ^ (next(gen) & 255)
        self._io.seek(begin, SEEK_SET)

    def pack(self, size=-1):
        """
        :type size: int
        :rtype : Buffer
        """
        if size == -1:
            size = self.size() - self.pos()
        begin = self.pos()
        end = begin + size
        result = Buffer(b'ZL01')
        result._io.seek(4, SEEK_SET)
        result.write_int(size)
        data = zlib.compress(self._io.getbuffer()[begin:end],
                             level=9)
        result.write(data)
        result._io.seek(0, SEEK_SET)
        return result

    def unpack(self, size=-1):
        """
        :type size: int
        :rtype : Buffer
        """
        if size == -1:
            size = self.size() - self.pos()
        magic = self.read(4)
        if magic != b'ZL01':
            self.close()
            raise Exception("Buffer.unpack. Not ZL01 or ZL02")
        bufsize = self.read_int()
        begin = self.pos()
        end = begin + size-8
        result = zlib.decompress(self._io.getbuffer()[begin:end],
                                 bufsize=bufsize)
        self._io.seek(size-8, SEEK_CUR)
        return Buffer(result)

    def calc_hash(self, size=-1):
        """
        :type size: int
        :rtype : int
        """
        if size == -1:
            size = self.size() - self.pos()
        begin = self.pos()
        end = begin + size
        return zlib.crc32(self._io.getbuffer()[begin:end])


def from_file(path, mode='rb'):
    """
    :type path: str
    :type mode: str
    :rtype : Buffer
    """
    f = open(path, mode)
    return Buffer(f.read())


def from_bytes(buf):
    """
    :type buf: bytearray | bytes
    :rtype : Buffer
    """
    return Buffer(buf)