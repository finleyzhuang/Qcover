import os
import sys
import logging
import time
import numpy as np
import networkx as nx
import random
import matplotlib.pyplot as plt
from Qcover.applications.common import get_ising_matrix, get_weights_graph, random_regular_graph


logger = logging.getLogger(__name__)


class MaxCut:
    """
    max cut problem:
    Divide the vertex set V of the graph into two sets so that the number of edges connecting
    the two vertex sets is as large as possible.
    For the weight graph, the weight sum of the edges connecting the two sets is required to be the largest.
    """
    def __init__(self,
                 graph: nx.Graph = None,
                 node_num: int = None,
                 node_degree: int = 3,
                 weight_range: int = 10,
                 seed: int = None) -> None:

        if graph is None:
            # generate random graph according to node_num and node_degree and weight_range
            self._node_num = node_num
            self._graph = random_regular_graph(node_num=self._node_num,
                                               degree=node_degree,
                                               weight_range=weight_range,
                                               seed=seed)
        else:
            self._node_num = len(graph.nodes)
            self._graph = graph

        self._qmatrix = None

    @property
    def node_num(self):
        return self._node_num

    @property
    def graph(self):
        return self._graph

    def update_random_graph(self, node_num, node_degree, weight_range, seed):
        self._node_num = node_num
        self._graph = random_regular_graph(node_num=self._node_num,
                                           degree=node_degree,
                                           weight_range=weight_range,
                                           seed=seed)

    def get_Qmatrix(self):
        """
        get the Q matrix in QUBO model of max cut problem
        Args:
            adjacent_mat (np.array): the adjacent matrix of graph G of the problem

        Returns:
            q_mat (np.array): the the Q matrix of QUBO model.
        """
        adj_mat = nx.adjacency_matrix(self._graph).A
        qubo_mat = adj_mat.copy()
        for i in range(self._node_num):
            qubo_mat[i][i] = - (np.sum(adj_mat[i]) - adj_mat[i][i])

        return qubo_mat

    def max_cut_value(self, x, w):
        """Compute the value of a cut.

        Args:
            x (numpy.ndarray): binary string as numpy array.
            w (numpy.ndarray): adjacency matrix.

        Returns:
            float: value of the cut.
        """
        X = np.outer(x, (1 - x))
        return np.sum(w * X)

    def run(self):
        if self._qmatrix is None:
            self._qmatrix = self.get_Qmatrix()

        qubo_mat = self._qmatrix
        ising_mat = get_ising_matrix(qubo_mat)
        mc_graph = get_weights_graph(ising_mat)
        return mc_graph

