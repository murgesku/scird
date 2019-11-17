__all__ = [
    "RedBlackTree",
    "LinkedList",
]

BLACK = 0
RED = 1


class RedBlackTree:
    """
    :type _root: RedBlackTree.Node
    """
    class Node:
        """
        :type next: RedBlackTree.Node
        """
        def __init__(self, content=None, color=RED, parent=None, left=None, right=None):
            """Initialize a new Red-Black Tree node.
            :type parent: RedBlackTree.Node
            :type left: RedBlackTree.Node
            :type right: RedBlackTree.Node
            """
            self.content = content
            self.parent = parent
            self.left = left
            self.right = right
            self.color = color
            self.next = None
            self.count = 1

        def replace(self, other):
            other.count = self.count
            other.parent = self.parent
            other.left = self.left
            other.right = self.right
            other.color = self.color

            if self is self.parent.left:
                self.parent.left = other
            elif self is self.parent.right:
                self.parent.right = other

    def __init__(self):
        self._root = None
        self._count = 0

    def rotate_left(self, node):
        pivot = node.right
        node.right = pivot.left
        if pivot.left is not None:
            pivot.left.parent = node
        pivot.parent = node.parent
        if node.parent is None:
            self._root = pivot
        elif node is node.parent.left:
            node.parent.left = pivot
        else:
            node.parent.right = pivot
        pivot.left = node
        node.parent = pivot

    def rotate_right(self, node):
        pivot = node.left
        node.left = pivot.right
        if pivot.right is not None:
            pivot.right.parent = node
        pivot.parent = node.parent
        if node.parent is None:
            self._root = pivot
        elif node is node.parent.right:
            node.parent.right = pivot
        else:
            node.parent.left = pivot
        pivot.right = node
        node.parent = pivot

    def append(self, content):
        self._count += 1
        z = RedBlackTree.Node(content)
        if self._root is None:
            z.color = BLACK
            self._root = z
            return
        y = None
        x = self._root
        while x is not None:
            y = x
            if content.name < x.content.name:
                x = x.left
            elif content.name > x.content.name:
                x = x.right
            else:
                t = x
                for i in range(x.count-1):
                    t = t.next
                z.parent = x
                t.next = z
                x.count += 1
                return
        z.parent = y
        if content.name < y.content.name:
            y.left = z
        elif content.name > y.content.name:
            y.right = z
        self._append_repair(z)

    def _append_repair(self, node):
        while (node is not self._root) and (node.parent.color == RED):
            grandparent = node.parent.parent
            if node.parent is grandparent.left:
                uncle = grandparent.right
                if (uncle is not None) and (uncle.color == RED):
                    node.parent.color = BLACK
                    uncle.color = BLACK
                    grandparent.color = RED
                    node = grandparent
                else:
                    if node is node.parent.right:
                        node = node.parent
                        self.rotate_left(node)
                    node.parent.color = BLACK
                    grandparent.color = RED
                    self.rotate_right(grandparent)
            else:
                uncle = grandparent.left
                if (uncle is not None) and (uncle.color == RED):
                    node.parent.color = BLACK
                    uncle.color = BLACK
                    grandparent.color = RED
                    node = grandparent
                else:
                    if node is node.parent.left:
                        node = node.parent
                        self.rotate_right(node)
                    node.parent.color = BLACK
                    grandparent.color = RED
                    self.rotate_left(grandparent)
        self._root.color = BLACK

    def remove(self, name, index=0):
        x = self._root
        while x is not None:
            if name == x.content.name:
                if index == -1 or x.count == 0:
                    self._remove(x)
                    return
                if index < x.count:
                    prev = None
                    cur = x
                    for i in range(index):
                        prev = cur
                        cur = cur.next
                    if prev is not None:
                        prev.next = cur.next
                    else:
                        cur = x.next
                        x.replace(cur)
                        if x is self._root:
                            self._root = cur
                        x = cur
                    x.count -= 1
                    self._count -= 1
                    return
            elif name < x.content.name:
                x = x.left
            else:
                x = x.right
        if x is None:
            return
        else:
            self._remove(x)

    def remove_all(self, name):
        self.remove(name, -1)

    def _remove(self, node):
        self._count -= node.count
        if (node.left is None) or (node.right is None):
            x = node
        else:
            x = node.right
            while x.left is not None:
                x = x.left
        y = x.left if x.left is not None else x.right
        y.parent = x.parent
        if x.parent is None:
            self._root = y
        elif x is x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        if x.color == BLACK:
            self._remove_repair(y)

    def _remove_repair(self, node):
        while (node is not self._root) and (node is None or node.color == BLACK):
            if node is node.parent.left:
                sibling = node.parent.right
                if sibling.color == RED:
                    sibling.color = BLACK
                    node.parent.color = RED
                    self.rotate_left(node.parent)
                    sibling = node.parent.right
                if ((sibling.left is None or sibling.left.color == BLACK)
                    and
                   (sibling.right is None or sibling.right.color == BLACK)):
                    sibling.color = RED
                    node = node.parent
                else:
                    if (sibling.right is None) or (sibling.right.color == BLACK):
                        sibling.left.color = BLACK
                        sibling.color = RED
                        self.rotate_right(sibling)
                        sibling = node.parent.right
                    sibling.color = node.parent.color
                    node.parent.color = BLACK
                    if sibling.right is not None:
                        sibling.right.color = BLACK
                    self.rotate_left(node.parent)
                    node = self._root
            else:
                sibling = node.parent.left
                if sibling.color == RED:
                    sibling.color = BLACK
                    node.parent.color = RED
                    self.rotate_right(node.parent)
                    sibling = node.parent.left
                if ((sibling.left is None or sibling.left.color == BLACK)
                    and
                   (sibling.right is None or sibling.right.color == BLACK)):
                    sibling.color = RED
                    node = node.parent
                else:
                    if (sibling.left is None) or (sibling.left.color == BLACK):
                        sibling.right.color = BLACK
                        sibling.color = RED
                        self.rotate_left(sibling)
                        sibling = node.parent.left
                    sibling.color = node.parent.color
                    node.parent.color = BLACK
                    if sibling.left is not None:
                        sibling.right.color = BLACK
                    self.rotate_right(node.parent)
                    node = self._root
        if node is not None:
            node.color = BLACK

    def __contains__(self, name):
        return self.find(name) is not None

    def find(self, name):
        x = self._root
        while x is not None and name != x.content.name:
            if name < x.content.name:
                x = x.left
            else:
                x = x.right
        return x

    def get_max(self):
        x = self._root
        while x.right is not None:
            x = x.right
        return x

    def get_min(self):
        x = self._root
        while x.left is not None:
            x = x.left
        return x

    def __len__(self):
        return self._count

    def __iter__(self):
        return self.inorder_traverse()

    def preorder_traverse(self):
        node = self._root
        stack = [node]
        while stack:
            node = stack.pop()
            # yield node
            cur = node
            for i in range(node.count):
                yield cur
                cur = cur.next
            if node.right is not None:
                stack.append(node.right)
            if node.left is not None:
                stack.append(node.left)

    def inorder_traverse(self):
        node = self._root
        stack = []
        while stack or (node is not None):
            if node is not None:
                stack.append(node)
                node = node.left
            else:
                node = stack.pop()
                cur = node
                for i in range(node.count):
                    yield cur
                    cur = cur.next
                node = node.right

    def postorder_traverse(self):
        node = self._root
        stack = []
        last = None
        while stack or node is not None:
            if node is not None:
                stack.append(node)
                node = node.left
            else:
                peek = stack[-1]
                if peek.right is not None and last is not peek.right:
                    node = peek.right
                else:
                    cur = peek
                    for i in range(node.count):
                        yield cur
                        cur = cur.next
                    last = stack.pop()


class LinkedList:

    class Node:

        def __init__(self, content):
            self.content = content

    def __init__(self):
        self.head = None
        self.tail = None
        self.count = 0

    def append(self, content):
        node = LinkedList.Node(content)
        if self.head is None:
            self.head = node
            self.tail = node
        else:
            self.tail.next = node
            self.tail = node
        self.count += 1

    def remove(self, name, index=0):
        prev = None
        cur = self.head
        counter = 0
        while cur is not None:
            if cur.content.name == name:
                if counter != index:
                    counter += 1
                    continue
                if prev is not None:
                    prev.next = cur.next
                    if cur.next is None:
                        self.tail = prev
                else:
                    self.head = self.head.next
                    if self.head is None:
                        self.tail = None
                self.count -= 1
            prev = cur
            cur = cur.next
            if index != -1:
                return

    def remove_all(self, name):
        self.remove(name, -1)

    def __len__(self):
        return self.count

    def __iter__(self):
        cur = self.head
        for i in range(self.count):
            yield cur
            cur = cur.next
