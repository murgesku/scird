__all__ = [
    "BlockPar",
    "from_txt",
    "to_txt",
    "from_dat",
    "from_code",
]

from enum import IntEnum
import zlib, struct

from _blockpar_helper import *
import stream


class BlockPar:

    class Element:

        class Kind(IntEnum):
            UNDEF = 0
            PARAM = 1
            BLOCK = 2

        def __init__(self, name="", content=None, comment=""):
            self.name = name
            if isinstance(content, str):
                self.kind = self.Kind.PARAM
            elif isinstance(content, BlockPar):
                self.kind = self.Kind.BLOCK
            else:
                self.kind = self.Kind.UNDEF
            self.content = content
            self.comment = comment

        def __repr__(self):
            return f"<\"{self.name}\">"

    def __init__(self, sort=True):
        self._order_map = LinkedList()
        self._search_map = RedBlackTree()
        self.sorted = sort

    def __setitem__(self, key, value):
        elem = BlockPar.Element(key, value)
        self._order_map.append(elem)
        self._search_map.append(elem)

    def __getitem__(self, key):
        node = self._search_map.find(key)
        result = [None for i in range(node.count)]
        for i in range(node.count):
            result[i] = node.content
            node = node.next
        return result

    def __delitem__(self, key):
        raise NotImplementedError

    def __contains__(self, key):
        return self._search_map.__contains__(key)

    def __len__(self):
        return self._order_map.count

    def __iter__(self):
        if self.sorted:
            src = self._search_map.__iter__()
        else:
            src = self._order_map.__iter__()
        for i in range(len(self)):
            node = next(src)
            yield node.content

    def _clear(self):
        pass

    def save(self, f, *, new_format=False):
        """
        @type f: io.BufferedWriter
        """
        s = stream.from_io(f)

        s.write_bool(self.sorted)
        s.write_uint(len(self))

        is_sort = self.sorted
        if is_sort:
            curblock = self._search_map.__iter__()
        else:
            curblock = self._order_map.__iter__()
        left = len(self)
        count = 1
        index = 0

        level = 0
        stack = list()

        while level > -1:
            if left > 0:
                node = next(curblock)
                el = node.content

                if new_format and is_sort:
                    if node.count > 1:
                        count = node.count
                        index = 0
                    s.write_uint(index)
                    if index == 0:
                        s.write_uint(count)
                    else:
                        s.write_uint(0)

                if el.kind == BlockPar.Element.Kind.PARAM:
                    s.write_byte(int(BlockPar.Element.Kind.PARAM))
                    s.write_widestr(el.name)
                    s.write_widestr(el.content)

                    left -= 1

                    index += 1
                    if index >= count:
                        count = 1
                        index = 0

                elif el.kind == BlockPar.Element.Kind.BLOCK:
                    s.write_byte(int(BlockPar.Element.Kind.BLOCK))
                    s.write_widestr(el.name)

                    stack.append((curblock, left, is_sort, count, index))
                    is_sort = el.content.sorted
                    if is_sort:
                        curblock = self._search_map.__iter__()
                    else:
                        curblock = self._order_map.__iter__()
                    left = len(el.content)
                    count = 1
                    index = 0

                    s.write_widestr(is_sort)
                    s.write_uint(left)

                    level += 1

            else:
                if level > 0:
                    curblock, left, is_sort, count, index = stack.pop()
                    left -= 1
                    index += 1
                    if index >= count:
                        count = 1
                        index = 0
                level -= 1

    def load(self, f, *, new_format=False):
        s = stream.from_io(f)

        self._clear()

        curblock = self
        curblock.sorted = s.read_bool()

        left = s.read_uint()

        level = 0
        stack = list()

        while level > -1:
            if left > 0:
                if new_format and curblock.sorted:
                    s.read(8)

                type = s.read_byte()
                name = s.read_widestr()

                if type == BlockPar.Element.Kind.PARAM:
                    curblock[name] = s.read_widestr()
                    left -= 1

                elif type == BlockPar.Element.Kind.BLOCK:
                    stack.append((curblock, left))

                    prevblock = curblock
                    curblock = BlockPar()
                    prevblock[name] = curblock

                    curblock.sorted = s.read_bool()
                    left = s.read_uint()
                    level += 1
                    continue

            else:
                if level > 0:
                    curblock, left = stack.pop()
                    left -= 1
                level -= 1

    def load_txt(self, f):
        """
        @type f: io.TextIO
        """
        self._clear()

        curblock = self

        level = 0
        stack = list()

        line_no = 0

        while True:
            line = f.readline()
            line_no += 1
            if line == '':  # EOF
                break

            line = line.strip('\x09\x0a\x0d\x20')  # \t\r\n\s

            comment = ''
            if line.find('//') != -1:
                line, comment = line.split('//', 1)
                line = line.rstrip('\x09\x20')  # \t\s

            if line.find('{') != -1:
                stack.append(curblock)

                head = line.split('{', 1)[0]
                head = head.rstrip('\x09\x20')  # \t\s

                if head.endswith(('^', '~')):
                    curblock.is_sort = head.endswith('^')
                    head = head[:-1]
                    head = head.rstrip('\x09\x20')  # \t\s
                else:
                    curblock.is_sort = True

                path = ''
                if head.find('=') != -1:
                    name, path = line.split('=', 1)
                    name = name.rstrip('\x09\x20')  # \t\s
                    path = path.lstrip('\x09\x20')  # \t\s
                else:
                    name = head

                if path != '':
                    curblock[name] = from_txt(path)
                else:
                    prevblock = curblock
                    curblock = BlockPar()
                    prevblock[name] = curblock

                    level += 1

            elif line.find('}') != -1:
                if level > 0:
                    curblock = stack.pop()
                level -= 1

            elif line.find('=') != -1:
                name, value = line.split('=', 1)
                name = name.rstrip('\x09\x20')  # \t\s
                value = value.lstrip('\x09\x20')  # \t\s

                curblock[name] = value

            else:
                continue

    def save_txt(self, f):
        """
        @type f: io.TextIO
        """
        curblock = iter(self)
        left = len(self)

        level = 0
        stack = list()

        while level > -1:
            if left > 0:
                el = next(curblock)
                f.write(4 * '\x20' * level)

                if el.kind == BlockPar.Element.Kind.PARAM:
                    f.write(el.name)
                    f.write('=')
                    f.write(el.content)
                    f.write('\x0d\x0a')
                    left -= 1

                elif el.kind == BlockPar.Element.Kind.BLOCK:
                    stack.append((curblock, left))

                    curblock = iter(el.content)
                    left = len(el.content)

                    f.write(el.name)
                    f.write('\x20')  # space
                    if el.content.sorted:
                        f.write('^')
                    else:
                        f.write('~')
                    f.write('{')
                    f.write('\x0d\x0a')  # \r\n
                    level += 1
                    continue

                else:
                    f.write('\x0d\x0a')
            else:
                level -= 1
                if level > -1:
                    f.write(4 * '\x20' * level)  # 4 spaces level padding
                    f.write('}')
                    f.write('\x0d\x0a')  # \r\n
                    curblock, left = stack.pop()
                    left -= 1


def from_txt(path, encoding="cp1251"):
    blockpar = BlockPar()
    with open(path, "rt", encoding=encoding) as txt:
        blockpar.load_txt(txt)
    return blockpar


def to_txt(blockpar, path, encoding="cp1251"):
    with open(path, "wt", encoding=encoding) as txt:
        blockpar.save_txt(txt)


def from_dat(path):
    def rand31pm(seed):
        while True:
            hi, lo = divmod(seed, 0x1f31d)
            seed = lo * 0x41a7 - hi * 0xb14
            if seed < 1:
                seed += 0x7fffffff
            yield seed - 1

    def zl_unpack(b):
        if b[:4] not in (b'ZL01', b'ZL02'):
            return b'\x00'
        unzip_size = struct.unpack("<I", b[4:8])[0]
        unzip_b = zlib.decompress(b[8:], bufsize=unzip_size)
        return unzip_b

    blockpar = None

    seed_key = b'\x89\xc6\xe8\xb1'

    s = stream.from_file(path)

    content_hash = s.read_uint()

    seed = s.read(4)
    seed = bytes(x ^ y for (x, y) in zip(seed_key, seed))
    seed = struct.unpack("<i", seed)[0]

    size = s.size() - s.pos()

    temp_buf = bytearray(s.read(size))

    s.close()

    gen = rand31pm(seed)
    for i in range(len(temp_buf)):
        temp_buf[i] = temp_buf[i] ^ (next(gen) & 255)

    if zlib.crc32(temp_buf) == content_hash:
        temp_stream = stream.from_bytes(zl_unpack(temp_buf))
        blockpar = BlockPar()
        blockpar.load(temp_stream, new_format=True)
        temp_stream.close()

    return blockpar


def from_code(code):
    blockpar = BlockPar(sort=False)
    curblock = blockpar  # current level block

    stack = []  # previous (lower) levels info (curblock and num)

    level = 0  # nesting level
    num = 0  # order of element in block

    # head - current level content
    # tail - for processing
    head, tail = None, code

    while level > -1:
        has_subblock = False
        i_open = tail.find("{")
        i_close = tail.find("}")
        if i_open == i_close:
            # no code blocks
            head, tail = tail, None
        elif i_close > i_open > -1:
            # open paren before close - nested block
            has_subblock = True
            head, tail = tail[:i_open], tail[i_open+1:]
        elif i_open > i_close > -1:
            # close paren before open - current block closes, still have blocks
            head, tail = tail[:i_close], tail[i_close + 1:]
        elif i_open == -1 and i_close > -1:
            # last close paren - current block closes, last in parent block
            head, tail = tail[:i_close], tail[i_close + 1:]
        elif i_close == -1 and i_open > -1:
            # something went wrong
            break
        # algorithm body
        for line in head.splitlines():
            line = line.strip()
            if line == '': continue
            curblock[str(num)] = line
            num += 1
        if has_subblock:
            nextblock = BlockPar(sort=False)
            curblock[str(num)] = nextblock
            num += 1
            stack.append((curblock, num))
            curblock = nextblock
            num = 0
            level += 1
        else:
            curblock.is_sort = True
            if level > 0:
                curblock, num = stack.pop()
            level -= 1
    return blockpar
