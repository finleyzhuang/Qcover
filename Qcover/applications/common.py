""" common module """
import time
import random
from collections import OrderedDict, defaultdict

import numpy as np
import networkx as nx
from qiskit.aqua import aqua_globals
from qiskit.aqua.operators import StateFn


def get_ising_matrix(qubo_mat: np.array):
    """
    calculate the ising matrix according to the Q matrix of problems.

    Args:
        q_mat: the matrix Q in QUBO model of the problem

    Returns:
        ising_mat (np.array): the the matrix of ising model
    """

    ising_mat = np.zeros_like(qubo_mat, dtype='float')  #.copy()
    mat_len = np.size(qubo_mat, 0)
    for i in range(mat_len):
        for j in range(mat_len):
            if i == j:
                ising_mat[i][i] = 1.0 * np.true_divide(qubo_mat[i][i], 2.0) + np.sum(qubo_mat[i]) - qubo_mat[i][i]
            else:
                ising_mat[i][j] = 1.0 * np.true_divide(qubo_mat[i][j], 4.0)

    return ising_mat


def get_weights_graph(ising_mat: np.array, graph: nx.Graph=None):
    """
    use ising matirx as adjacency matrix to generate correspondence graph model
    Args:
        ising_mat (np.array): the Ising matrix that used to generate graph

    Returns:
        graph (nx.Graph): the graph model generated by ising matrix
    """

    cnt = np.size(ising_mat, 0)
    node_map = defaultdict(int)
    if graph is not None:
        node_list = list(graph.nodes)
        for i in range(len(node_list)):
            node_map[i] = node_list[i]
    else:
        for i in range(cnt):
            node_map[i] = i

    graph = nx.Graph()
    for i in range(cnt):
        for j in range(cnt):
            if i == j:
                graph.add_node(node_map[i], weight=ising_mat[i][i])
            else:
                if abs(ising_mat[i][j] - 0.) <= 1e-8:
                    continue
                graph.add_edge(node_map[i], node_map[j], weight=ising_mat[i][j])

    return graph    


def get_most_small_ising(state_count, ising_g):

    nodew = nx.get_node_attributes(ising_g, 'weight')
    edw = nx.get_edge_attributes(ising_g, 'weight')

    min_h = 999999
    for key, val in state_count.items():
        tmp_h = 0
        tw = []
        for i in range(len(key)):
            if key[i] == '0':
                tw.append(-1)
            else:
                tw.append(1)

        for nd in nodew:
            tmp_h += nodew[nd] * tw[nd]
        for ed in edw:
            if ed[0] == ed[1]:
                continue
            tmp_h += edw[ed] * tw[ed[0]] * tw[ed[1]]

        if min_h > tmp_h:
            min_h = tmp_h
            res_state = [int(key[i]) for i in range(len(key))]
    return res_state


def random_regular_graph(node_num, degree=3, weight_range=10, negative_weight=False, seed=None):
    """Generate random Erdos-Renyi graph.

    Args:
        node_num (int): number of nodes.
        weight_range (int): weights will be smaller than this value,
            in absolute value. range: [1, weight_range).
        degree (int): the number of edge belong to every node.
        negative_weight (bool): allow to have edge with negative weights
        # savefile (str or None): name of file where to save graph.
        seed (int or None): random seed - if None, will not initialize.

    Returns:
        numpy.ndarray: adjacency matrix (with weights).

    """
    assert (node_num * degree) % 2 == 0
    assert weight_range >= 0
    if seed is None:
        seed = np.random.randint(1, 10598)   # seed = 10598
        # random.seed(seed)

    random_g = nx.random_regular_graph(d=degree, n=node_num, seed=seed)

    for e in random_g.edges:
        w = random.uniform(1, weight_range)   # np.random.randint(1, weight_range)
        if np.random.random() >= 0.5 and negative_weight:
            w *= -1
        random_g.add_edge(e[0], e[1], weight=w)

    for e in random_g.nodes:
        w = random.uniform(1, weight_range)
        if np.random.random() >= 0.5 and negative_weight:
            w *= -1
        random_g.add_node(e, weight=w)
        random_g.add_edge(e, e, weight=w)
    return random_g


def random_number_list(n, weight_range=(1, 100), seed=None):
    """Generate a set of positive integers within the given range.

    Args:
        n (int): size of the set of numbers.
        weight_range (tuple/list): minimum and maximum absolute value of the numbers.
        savefile (str or None): write numbers to this file.
        seed (Union(int,None)): random seed - if None, will not initialize.

    Returns:
        numpy.ndarray: the list of integer numbers.
    """
    if seed:
        aqua_globals.random_seed = seed

    number_list = aqua_globals.random.integers(low=weight_range[0], high=(weight_range[1] + 1), size=n)
    return number_list