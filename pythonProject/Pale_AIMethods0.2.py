from collections import deque

import networkx as nx
import matplotlib.pyplot as plt
from icecream import ic


class AIMethods(nx.Graph):

    def bfs(self, start_node=None):
        if start_node is None:
            start_node = list(self.nodes())[0]

        visited = set()
        Q = deque([start_node])
        order = []

        while Q:
            current_node = Q.popleft()
            if current_node in visited:
                continue

            order.append(current_node)
            visited.add(current_node)

            for node in self[current_node]:
                if node in visited:
                    continue
                Q.append(node)

        return order

    def dfs(self, start_node=None, visited=None):
        if start_node is None:
            start_node = list(self.nodes())[0]

        if visited is None:
            visited = set()

        order = []

        if start_node in visited:
            return order

        order.append(start_node)
        visited.add(start_node)

        for node in self[start_node]:
            if node in visited:
                continue

            order.extend(AIMethods.dfs(self, start_node=node, visited=visited))

        return order

    def display(self, order, pos=None, ptime=0.2):
        if pos is None:
            pos = nx.spring_layout(self, seed=7)

        font_size = max(22 - len(order), 8)
        node_size = max(800 - len(order) * 25, 150)

        plt.style.use('dark_background')
        plt.subplots(nrows=1, ncols=1)
        visited = set()
        nx.draw_shell(self, with_labels=True)

        for i, node in enumerate(order, start=1):
            visited.add(node)
            plt.clf()
            nx.draw_networkx_labels(self, pos, font_size=font_size, font_color='whitesmoke')

            nx.draw_networkx_nodes(
                self,
                pos,
                node_size=node_size,
                alpha=0.9,
                edgecolors=[
                    'green' if n == node else
                    'pink' if n in visited else 'red'
                    for n in self.nodes
                ],

                node_color=[
                    'tab:green' if n == node else
                    'tab:purple' if n in visited else 'tab:red'
                    for n in self.nodes
                ]
            )
            nx.draw_networkx_edges(
                self,
                pos,
                width=node_size // 40,
                alpha=0.5,
                edge_color=[
                    'tab:purple' if e[1] in visited else 'tab:red'
                    for e in self.edges
                ],
            )

            plt.tight_layout()
            plt.draw()
            plt.pause(ptime)

        nx.draw_networkx_nodes(
            self, pos, node_size=node_size, alpha=0.99, edgecolors='whitesmoke', node_color='tab:purple'
        )
        plt.show()


def main():
    G = AIMethods()

    G.add_edges_from([
        ('A', 'B'),
        ('A', 'C'),
        ('A', 'E'),
        ('B', 'F'),
        ('B', 'D'),
        ('C', 'X'),
        ('C', 'R'),
        ('D', 'K'),
        ('D', 'A')
    ])
    L = nx.balanced_tree(2, 3)

    C = nx.cycle_graph(50)
    pos = nx.circular_layout(C)

    ptime = 0.5

    AIMethods.display(G, AIMethods.dfs(G), ptime=ptime)
    AIMethods.display(G, AIMethods.bfs(G, start_node="K"))
    AIMethods.display(L, AIMethods.dfs(L))
    AIMethods.display(L, AIMethods.bfs(L))
    AIMethods.display(C, AIMethods.dfs(C), pos=pos, ptime=0.1)
    AIMethods.display(C, AIMethods.bfs(C), pos=pos, ptime=0.1)


if __name__ == '__main__':
    main()