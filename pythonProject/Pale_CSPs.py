from collections import deque
from typing import List, Tuple, Callable, Any


def eq(x: Any, y: Any) -> bool: return x == y


def nq(x: Any, y: Any) -> bool: return x != y


def lt(x: Any, y: Any) -> bool: return x < y


def gt(x: Any, y: Any) -> bool: return x > y


def le(x: Any, y: Any) -> bool: return x <= y


def ge(x: Any, y: Any) -> bool: return x >= y


class Node:
    all_instance: List['Node'] = []
    graphs: List[List['Node']] = []

    def __init__(self, name: str, domain: List[Any]):
        self.name: str = name
        self.domain: List[Any] = domain
        self.result_domain: List[Any] = domain.copy()
        self.changed: bool = False
        Node.all_instance.append(self)

    constraints: Tuple[Tuple[Callable[[Any, Any], bool]]] = (
        (eq, eq),
        (nq, nq),
        (lt, gt),
        (gt, lt),
        (le, ge),
        (ge, le),
    )

    @staticmethod
    def get_other_constraint(con: Callable[[Any, Any], bool]) -> Callable[[Any, Any], bool]:
        for method in Node.constraints:
            if con is method[0]:
                return method[1]

    def forward_check(self, other: 'Node', con: Callable[[Any, Any], bool]) -> List[Any]:
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
    def get_done(seen: List[Tuple[Any, 'Node']], node: 'Node') -> List[Tuple[Any, 'Node']]:
        back: List[Tuple[Any, 'Node']] = []
        for old in seen:
            if node is old[1]:
                back.append(old)
                seen.remove(old)

        return back

    @staticmethod
    def arc_consistency(all_constraints: List[List[Any]]):
        Q: deque[Tuple['Node', 'Node', Callable[[Any, Any], bool]]] = deque()
        for left, right, con in all_constraints:
            Q.append((left, right, con))
            Q.append((right, left, Node.get_other_constraint(con)))

        done: List[Tuple[Tuple['Node', 'Node', Callable[[Any, Any], bool]], Any]] = []
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
    def group(*args: 'Node'):
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
    nsw = Node('NSW', ["R", "B"])
    v = Node('V', ["R", "G", "B"])
    sa = Node('SA', ["R", "G", "B"])
    t = Node('T', ["R", "G", "B"])
    Node.group(wa, nt, q, nsw, v, sa, t)

    L2: List[List[Any]] = [
        [A, B, nq],
        [A, D, eq],
        [B, D, nq],
        [B, C, nq],
        [C, B, nq],
        [C, D, lt],
        [E, A, lt],
        [E, B, lt],
        [E, D, lt]
    ]

    L3: List[List[Any]] = [
        [sa, wa, nq],
        [sa, nt, nq],
        [sa, q, nq],
        [sa, nsw, nq],
        [sa, v, nq],
        [nt, q, nq],
        [nt, wa, nq],
        [nsw, q, nq],
        [nsw, v, nq]
    ]

    Node.arc_consistency(L3)
    Node.arc_consistency(L2)
    Node.show()


if __name__ == '__main__':
    main()
