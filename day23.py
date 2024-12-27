import networkx as nx
from typing import List

G = nx.Graph()

for con in open('data/day23.txt', 'r'):
    node_0, node_1 = con.strip().split('-')
    G.add_edge(node_0, node_1)

triplets = []
biggest_clique = []
for clique in nx.enumerate_all_cliques(G):
    if len(clique) == 3:
        triplets.append(clique)
    if len(clique) > len(biggest_clique):
        biggest_clique = clique

def clique_to_password(clique: List[str]) -> str:
    return ','.join(sorted(list(set(clique))))

chief_historian_triplets = [t for t in triplets if any([node[0] == 't' for node in t])]

print(f'Part 1: {len(chief_historian_triplets)}')
print(f'Part 2: {clique_to_password(biggest_clique)}')