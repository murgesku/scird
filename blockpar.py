import io

from _blockpar_helper import *

UNDEF = 0
PARAM = 1
BLOCK = 2


class BlockPar:

    class Element:

        def __init__(self, name="", content=None, comment=""):
            self.name = name
            if isinstance(content, str):
                self.kind = PARAM
            elif isinstance(content, BlockPar):
                self.kind = BLOCK
            else:
                self.kind = UNDEF
            self.content = content
            self.comment = comment

        def __repr__(self):
            return f"Element(\"{self.name}\", \"{self.content}\")"

    def __init__(self):
        self._order_map = LinkedList()
        self._search_map = RedBlackTree()
        self.sorted = True

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

    def load_txt(self, f):
        """:type f: io.TextIO"""
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
                    curblock, is_sort = stack.pop()
                level -= 1

            elif line.find('=') != -1:
                name, value = line.split('=', 1)
                name = name.rstrip('\x09\x20')  # \t\s
                value = value.lstrip('\x09\x20')  # \t\s

                curblock[name] = value

            else:
                continue
    
    # def save_txt(self, f, init_level=0):
    #     """
    #     :type f: io.TextIO
    #     :type init_level: int
    #     """
    #     curblock = iter(self)
    #     is_sort = self.is_sort
    #     left = len(self)
    #
    #     level = init_level
    #     stack = list()
    #
    #     while level > -1:
    #         if left > 0:
    #             elem = next(curblock)
    #
    #             f.write(4 * '\x20' * level)  # 4 spaces level padding
    #
    #             if isinstance(content, list):
    #                 for value in content:
    #                     if isinstance(value, BlockPar):
    #                         f.write(str(name))
    #                         f.write('\x20')  # space
    #                         if value.is_sort:
    #                             f.write('^')
    #                         else:
    #                             f.write('~')
    #                         f.write('{')
    #                         f.write('\x0d\x0a')  # \r\n
    #                         level += 1
    #                         value.txt_dump(io, level)
    #                         level -= 1
    #                         f.write(
    #                             4 * '\x20' * level)  # 4 spaces level padding
    #                         f.write('}')
    #                     else:
    #                         f.write(str(name))
    #                         f.write('=')
    #                         f.write(str(content))
    #                         f.write('\x0d\x0a')  # \r\n
    #                     left -= 1
    #             else:
    #                 if isinstance(content, BlockPar):
    #                     stack.append((curblock, left, is_sort))
    #
    #                     curblock = iter(content)
    #                     left = len(content)
    #                     is_sort = content.is_sort
    #
    #                     f.write(str(name))
    #                     f.write('\x20')  # space
    #                     if is_sort:
    #                         f.write('^')
    #                     else:
    #                         f.write('~')
    #                     f.write('{')
    #                     f.write('\x0d\x0a')  # \r\n
    #                     level += 1
    #                     continue
    #                 else:
    #                     f.write(str(name))
    #                     f.write('=')
    #                     f.write(str(content))
    #                     f.write('\x0d\x0a')  # \r\n
    #                     left -= 1
    #         else:
    #             level -= 1
    #             if level > -1:
    #                 f.write(4 * '\x20' * level)  # 4 spaces level padding
    #                 f.write('}')
    #                 f.write('\x0d\x0a')  # \r\n
    #                 curblock, left, is_sort = stack.pop()
    #                 left -= 1


def from_txt(path, encoding="utf-8"):
    blockpar = BlockPar()
    with open(path, "rt") as txt:
        blockpar.load_txt(txt)
    return blockpar
