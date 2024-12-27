from graphlib import TopologicalSorter
import networkx as nx
from copy import deepcopy
from typing import Set, Tuple, Dict, List
import random

funcs = {
    'AND': lambda x, y: x & y,
    'OR': lambda x, y: x | y,
    'XOR': lambda x, y: x != y
}
            
def evaluate_graph(G: Dict[str, List[str]], x: str | None = None, y: str | None = None) -> str:
    
    G = deepcopy(G)
    
    x_nodes = sorted(node for node in G if node[0] == 'x')
    y_nodes = sorted(node for node in G if node[0] == 'y')
    z_nodes = sorted(node for node in G if node[0] == 'z')

    if x != None:
        x = x[::-1]
        for x_index, x_node in enumerate(x_nodes):
            if x_index < len(x):
                G[x_node] = [x[x_index]]
            else:
                G[x_node] = ['0']
    
    if y != None:
        y = y[::-1]
        for y_index, y_node in enumerate(y_nodes):
            if y_index < len(y):
                G[y_node] = [y[y_index]]
            else:
                G[y_node] = ['0']

    ts = TopologicalSorter(G)
    node_order = ts.static_order()

    solved_G = {}

    for node in node_order:
        if node not in G:
            continue

        operation = G[node]
        match operation:
            case [lit]:
                solved_G[node] = bool(int(lit))
            case [command_name, input_0, input_1]:
                
                f = funcs[command_name]
                solved_G[node] = f(solved_G[input_0], solved_G[input_1])
    

    res = ''
    for z_node in z_nodes:
        res = str(int(solved_G[z_node])) + res

    return res

def main() -> None:
    G = {}
    for line in open('data/day24.txt', 'r'):#test_input:
        args = line.strip().replace(':', '').split(' ')
        match args:
            case [wire, signal]:
                G[wire] = [signal]
            case [input_0, command_name, input_1, '->', output]:
                G[output] = [command_name, input_0, input_1]

    part_1 = evaluate_graph(G)

    part_1 = int(str(part_1), 2)

    print(f'Part 1: {part_1}')

    # Make a networkx DiGraph (for finding ancestors of nodes)
    H = nx.DiGraph()
    for node in G:
        operation = G[node]
        match operation:
            case [command_name, input_0, input_1]:
                H.add_edge(input_0, node)
                H.add_edge(input_1, node)
        
    def xy_descendants_up_to(n: int) -> Set[str]:
        return set(['x' + str(i).zfill(2) for i in range(n + 1)] + ['y' + str(i).zfill(2) for i in range(n + 1)])

    def find_switch_for_z_gate(z_gate: str) -> str:
        l = xy_descendants_up_to(int(z_gate[1:]))
        return [node for node in H.nodes() if (set([n for n in nx.ancestors(H, node) if n[0] in ['x', 'y']]) == l) and G[node][0] == 'XOR'][0]

    # By inspection - some z nodes have the wrong gate (i.e. a gate other than XOR) leading directly into them
    # Use find_switch_for_z_gate function above to find a XOR gate with the correct ancestors to switch with.

    bad_z_gates = [node for node in G if node[0] == 'z' and G[node][0] != 'XOR' and node != 'z45']

    switches = [(z_gate, find_switch_for_z_gate(z_gate)) for z_gate in bad_z_gates]

    for switch_0, switch_1 in switches:
        switch_to_1 = G[switch_0]
        switch_to_0 = G[switch_1]

        G[switch_0] = switch_to_0
        G[switch_1] = switch_to_1

    def try_switching_nodes(G: Dict[str, List[str]], nodes_to_try_switching: Set[str]) -> Tuple[str, str] | None:
        """
        Try switching certain nodes in G and see if it gives the right answer for 100 random binary additions.
        Return the first pair of nodes that give the right answer when switched.
        """
        res = []
        for switch_0 in nodes_to_try_switching:
            for switch_1 in nodes_to_try_switching:
                G2 = deepcopy(G)
                switch_to_1 = G2[switch_0]
                switch_to_0 = G2[switch_1]

                G2[switch_0] = switch_to_0
                G2[switch_1] = switch_to_1

                all_correct = True
                for _ in range(100):
                    x = random.randint(0, 2 ** 45 - 1)
                    y = random.randint(0, 2 ** 45 - 1)

                    z = x + y

                    binary_x = bin(x)[2:]
                    binary_y = bin(y)[2:]
                    binary_z = bin(z)[2:]
                    try:
                        test_z = evaluate_graph(G2, binary_x, binary_y)
                    except:
                        # invalid graph - carry on
                        all_correct = False
                        break

                    if binary_z.zfill(46) != test_z.zfill(46):
                        all_correct = False
                        break

                if all_correct:
                    return (switch_0, switch_1)
                
        return None
                
    # again by inspection, z11 is giving the wrong answer.
    # try switching all ancestors of z11 until it's right.
    z11_ancestors = nx.ancestors(H, 'z11')

    switches.append(try_switching_nodes(G, z11_ancestors))

    def flatten(l: List[Tuple[str, str]]) -> List[str]:
        return [x for y in l for x in y]

    print(f'Part 2: {','.join(sorted(flatten(switches)))}')

if __name__ == '__main__':
    main()