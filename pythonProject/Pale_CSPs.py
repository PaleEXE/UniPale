import builtins
from collections import deque


def eq(x, y): return x == y


def nq(x, y): return x != y


def lt(x, y): return x < y


def gt(x, y): return x > y


def le(x, y): return x <= y


def ge(x, y): return x >= y


class Node:
    all_instance: list = []
    graphs: list = []

    def __init__(self, name: str, domain: list):
        self.name: str = name
        self.domain: list[any] = domain
        self.result_domain: list[any] = domain.copy()
        self.changed: bool = False
        Node.all_instance.append(self)

    constraints: tuple[tuple[builtins.staticmethod]] = (
        (eq, eq),
        (nq, nq),
        (lt, gt),
        (gt, lt),
        (le, ge),
        (ge, le),
    )

    @staticmethod
    def get_other_constraint(con: builtins.staticmethod):
        for method in Node.constraints:
            if con is method[0]:
                return method[1]

    def forward_check(self, other, con: builtins.staticmethod):
        ind = 0
        for value in self.result_domain:
            for other_value in other.result_domain:
                if con(value, other_value):
                    self.result_domain[ind] = value
                    ind += 1
                    break

        self.changed = len(self.result_domain) != ind

        self.result_domain = self.result_domain[0: ind]
        return self.result_domain

    @staticmethod
    def get_done(seen: list, node: list):
        back: list[tuple] = []
        for old in seen:
            if node is old[1]:
                back.append(old)
                seen.remove(old)

        return back

    @staticmethod
    def arc_consistency(all_constraints: list[tuple]):
        Q: deque[Node, Node, builtins.staticmethod] = deque()
        for left, right, con in all_constraints:
            Q.append([left, right, con])
            Q.append([right, left, Node.get_other_constraint(con)])

        done: list = []
        while Q:
            left, right, con = Q[0]
            left.forward_check(right, con)
            if left.changed:
                Q.extend(Node.get_done(done, left))

            done.append(Q.popleft())

    @staticmethod
    def show():
        print("---{Pale_exe CSPs}---".center(97))
        print(f'{"Before".rjust(30).ljust(47)} | {"After".center(40)}')
        for group in Node.graphs:
            for node in group:
                print(f' {node.name.ljust(5)}-{str(node.domain).center(40)} | {str(node.result_domain).center(40)}')
            print("\n")

    @staticmethod
    def group(*args):
        Node.graphs.append(args)


def main():
    A = Node('A', [1, 2, 3, 4])
    B = Node('B', [1, 2, 4])
    C = Node('C', [1, 3, 4])
    D = Node('D', [1, 2, 3, 4])
    E = Node('E', [1, 2, 3, 4])
    Node.group(A, B, C, D, E)

    wa = Node('WA', ["R"])
    nt = Node('NT', ["R", "G", "B"])
    q = Node('Q', ["G", "B"])
    nsw = Node('NSW', ["R", "G", "B"])
    v = Node('V', ["R", "G", "B"])
    sa = Node('SA', ["R", "G", "B"])
    t = Node('T', ["R", "G", "B"])
    Node.group(wa, nt, q, nsw, v, sa, t)

    L2 = [[A, B, nq],
          [A, D, eq],
          [B, D, nq],
          [B, C, nq],
          [C, B, nq],
          [C, D, lt],
          [E, A, lt],
          [E, B, lt],
          [E, D, lt]]

    L3 = [[sa, wa, nq],
          [sa, nt, nq],
          [sa, q, nq],
          [sa, nsw, nq],
          [sa, v, nq],
          [nt, q, nq],
          [nt, wa, nq],
          [nsw, q, nq],
          [nsw, v, nq]]

    Node.arc_consistency(L3)
    Node.arc_consistency(L2)
    Node.show()


if __name__ == '__main__':
    main()
