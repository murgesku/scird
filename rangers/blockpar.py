__all__ = [
    "BlockPar",
    "from_txt",
    "to_txt",
    "from_dat",
    "from_code",
]

from enum import IntEnum

from rangers._blockpar_helper import *
from rangers import stream, buffer
from rscript.file.utils import bytes_xor, bytes_to_int


class BlockPar:

    class Element:

        class Kind(IntEnum):
            UNDEF = 0
            PARAM = 1
            BLOCK = 2

        def __init__(self, name="", content=None, comment=""):
            """
            :type name: str
            :type content: str | BlockPar | None
            :type comment: str
            """
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
        """
        :type key: str
        :rtype: list[BlockPar.Element]
        """
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
        :type f: io.BufferedWriter | stream.Stream
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
        """
        :type f: io.BufferedReader | stream.Stream
        """
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
        :type f: io.TextIO
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

            line = line.strip('\x09\x0a\x0d\x20')  # \t\n\r\s

            comment = ''
            if '//' in line:
                line, comment = line.split('//', 1)
                line = line.rstrip('\x09\x20')  # \t\s

            if '{' in line:
                stack.append(curblock)

                head = line.split('{', 1)[0]
                head = head.rstrip('\x09\x20')  # \t\s

                if head.endswith(('^', '~')):
                    curblock.sorted = head.endswith('^')
                    head = head[:-1]
                    head = head.rstrip('\x09\x20')  # \t\s
                else:
                    curblock.sorted = True

                path = ''
                if '=' in head:
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

            elif '}' in line:
                if level > 0:
                    curblock = stack.pop()
                level -= 1

            elif '=' in line:
                name, value = line.split('=', 1)
                name = name.rstrip('\x09\x20')  # \t\s
                value = value.lstrip('\x09\x20')  # \t\s

                # multiline parameters - heredoc
                if value.startswith('<<<'):
                    value = ''
                    spacenum = 0
                    while True:
                        line = f.readline()
                        line_no += 1
                        if line == '':  # EOF
                            raise Exception("BlockPar.load_txt. "
                                            "Heredoc end marker not found")

                        if line.strip('\x09\x0a\x0d\x20') == '':
                            continue

                        if value == '':
                            spacenum = len(line) - len(line.lstrip('\x20'))
                            if spacenum > (4 * level):
                                spacenum = 4 * level

                        if line.lstrip('\x09\x20').startswith('>>>'):
                            value = value.rstrip('\x0a\x0d')
                            break

                        value += line[spacenum:]

                curblock[name] = value

            else:
                continue

    def save_txt(self, f):
        """
        :type f: io.TextIO
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
                    if '\x0d' in el.content or '\x0a' in el.content:
                        f.write('<<<')
                        f.write('\x0d\x0a')
                        content = el.content
                        for s in content.splitlines(keepends=True):
                            f.write(4 * '\x20' * level)
                            f.write(s)
                        f.write('\x0d\x0a')
                        f.write(4 * '\x20' * level)
                        f.write('>>>')
                    else:
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

    def get_par(self, path):
        """
        :type path: str
        :rtype: str
        """
        path = path.strip().split('.')
        result = self
        for part in path:
            result = result[part][0]
            if part != path[-1]:
                if result.kind is not BlockPar.Element.Kind.BLOCK:
                    raise Exception("BlockPar.get_par. Path do not exists")
            else:
                if result.kind is not BlockPar.Element.Kind.PARAM:
                    raise Exception("BlockPar.get_par. Not a parameter")
            result = result.content
        return result

    def get_block(self, path):
        """
        :type path: str
        :rtype: BlockPar
        """
        path = path.strip().split('.')
        result = self
        for part in path:
            result = result[part][0]
            if part != path[-1]:
                if result.kind is not BlockPar.Element.Kind.BLOCK:
                    raise Exception("BlockPar.get_block. Path do not exists")
            else:
                if result.kind is not BlockPar.Element.Kind.BLOCK:
                    raise Exception("BlockPar.get_par. Not a block")
            result = result.content
        return result


def from_txt(path, encoding="cp1251"):
    """
    :type path: str
    :type encoding: str
    :rtype: BlockPar
    """
    blockpar = BlockPar()
    with open(path, "rt", encoding=encoding, newline='') as txt:
        blockpar.load_txt(txt)
    return blockpar


def to_txt(blockpar, path, encoding="cp1251"):
    """
    :type blockpar: BlockPar
    :type path: str
    :type encoding: str
    """
    with open(path, "wt", encoding=encoding, newline='') as txt:
        blockpar.save_txt(txt)


def from_dat(path):
    """
    :type path: str
    :rtype : BlockPar
    """
    blockpar = None
    seed_key = b'\x89\xc6\xe8\xb1'

    b = buffer.from_file(path)

    content_hash = b.read_uint()

    seed = bytes_xor(b.read(4), seed_key)
    seed = bytes_to_int(seed)

    size = b.size() - b.pos()

    b.decipher(seed, size)
    calc_hash = b.calc_hash(size)

    if calc_hash == content_hash:
        unpacked = b.unpack(size)
        blockpar = BlockPar()
        blockpar.load(unpacked, new_format=True)
        unpacked.close()
    else:
        raise Exception("BlockPar.from_dat. Wrong content hash")

    b.close()

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
