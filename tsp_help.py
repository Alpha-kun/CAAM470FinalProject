import networkx as nx
from collections import deque


def read_in_graph(filename):
  """
  This method takes in a text file representation of a graph and creates a
  NetworkX graph from the file.
  """
  f = open(filename)

  nodes, edges = [int(n) for n in f.readline().split()]

  g = nx.Graph()
  for line in f.readlines():
    try:
      n1, n2, weight = (int(n) for n in line.split())
      g.add_edge(n1, n2, weight=weight)
    except ValueError:
      pass

  return g


def get_cycle(t):
  """
  Givne a graph t, this method finds a cycle in t.
  """
  start = next(iter(t.nodes))

  node = start
  cycle = [start]
  while True:
    new_edge = False
    for edge in t.edges(node):
      if edge[0] not in cycle or edge[1] not in cycle:
        e = edge
        new_edge = True
        break

    if not new_edge:
      break

    if e[0] == node:
      other = e[1]
    else:
      other = e[0]

    cycle.append(other)
    node = other

  cycle.append(start)
  return cycle


def get_connected_nodes(t):
  """
  Given a graph t, this method performs a BFS through t to get the
  maximal connected component that goes through an arbitray node in t.
  """
  start = next(iter(t.nodes))

  visited = set([])
  to_visit = deque([start])

  while to_visit:
    curr = to_visit.pop()
    visited.add(curr)

    for nbr in t.neighbors(curr):
      if nbr not in visited and nbr not in to_visit:
        to_visit.appendleft(nbr)

  return visited


def tsp_nearest_neighbor(g, source=None):
  """
  Given graph g, uses the nearest-neighbor heuristic to get a TSP route
  approximation for g.
  """

  # Initialize TSP graph
  tsp = nx.Graph()

  # Get starting node
  if source is None:
    source = next(iter(g.nodes))

  node = source

  # Go through nearest-neighbor heuristic
  searched = set([])
  while len(searched) != len(g.nodes()):
    edges = filter_searched(g.edges(node), searched)
    if len(edges) == 0:
      break

    edge_to_add = sorted(edges, key=lambda edge: get_weight(g, edge))[0]

    tsp.add_edge(edge_to_add[0],
                 edge_to_add[1],
                 weight=get_weight(g, edge_to_add))

    searched.add(node)
    node = edge_to_add[1]

  # Add final edge in cycle
  final_edge = (node, source)
  tsp.add_edge(node, source, weight=get_weight(g, final_edge))

  # Return solution
  return tsp


def get_weight(g, edge):
  return g[edge[0]][edge[1]]["weight"]


def edge_intersect(*edges):
  """
  Given a set of edges, check if any of the edges are incident to the same node.
  """
  node_set = set([])
  for edge in edges:
    node_set.add(edge[0])
    node_set.add(edge[1])

  return len(node_set) != 2 * len(edges)


def filter_searched(edges, searched):
  """
  Given a list of edges, filters out edges incident to any node in searched.
  """
  e_final = []
  for edge in edges:
    if edge[0] in searched or edge[1] in searched:
      continue
    e_final.append(edge)

  return e_final


def copy_graph(g):
  """
  Copy a networkx graph.
  """
  copy = nx.Graph()

  for edge in g.edges():
    copy.add_edge(edge[0], edge[1], get_weight(g, edge))
