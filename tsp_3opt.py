import networkx as nx
from time import process_time
from tsp_help import (read_in_graph, tsp_nearest_neighbor, get_cycle,
                      get_weight)


def apply_3opt(edges, g, cycle):
  """
  Helper method for perform a 3-opt. This method takes in a set of edges to
  optimize, essentially attempting to swap some of the edges for a cheaper tour.
  """
  # Get edge positions within cycle
  edge_starts = set([edge[0] for edge in edges])
  merged_edges = []
  for edge in edges:
    merged_edges.extend(edge)

  # Define static list of valid swaps
  # Normally: [(0,1), (2,3), (4,5)]
  swapped = [[(0, 1), (2, 4), (3, 5)], [(0, 2), (1, 4), (3, 5)],
             [(0, 2), (1, 3), (4, 5)], [(0, 3), (4, 1), (2, 5)],
             [(0, 3), (4, 2), (1, 5)], [(0, 4), (3, 1), (2, 5)],
             [(0, 4), (3, 2), (1, 5)]]

  # Create skeleton from t
  skeleton = nx.Graph()
  for node in range(len(cycle) - 1):
    u = cycle[node]
    v = cycle[node + 1]
    if u in edge_starts:
      continue

    skeleton.add_edge(u, v, weight=get_weight(g, (u, v)))

  min_swap = []
  min_edge_wt = float('inf')

  # Compute weights of candidate edge groups
  for swapper in swapped:
    wt = sum(
        get_weight(g, (merged_edges[e[0]], merged_edges[e[1]]))
        for e in swapper)
    if wt < min_edge_wt:
      min_swap = swapper
      min_edge_wt = wt

  # Add edges to skeleton to get (possibly) improved solution
  for edge_ids in min_swap:
    e0 = merged_edges[edge_ids[0]]
    e1 = merged_edges[edge_ids[1]]

    skeleton.add_edge(e0, e1, weight=get_weight(g, (e0, e1)))

  # Return best solution from candidates
  return skeleton


def tsp_3opt(g, source=None):
  """
  This method describes a heuristic for finding sub-optimal TSP tours.

  The 3-opt heuristic guarantees that swapping any set of three edges in the
  tour would not yield a more optimal tour.
  """
  t = tsp_nearest_neighbor(g, source=source)
  score = t.size(weight="weight")

  improved = True
  while improved:  # while there is an improving solution
    curr_cycle = get_cycle(t)
    improved = False

    # Pick three edges that don't connect
    for i in range(0, len(curr_cycle)):
      for j in range(i + 2, len(curr_cycle)):
        k_up = len(curr_cycle) - 2 if i == 0 else len(curr_cycle) - 1
        for k in range(j + 2, k_up):
          e1 = (curr_cycle[i], curr_cycle[i + 1])
          e2 = (curr_cycle[j], curr_cycle[j + 1])
          e3 = (curr_cycle[k], curr_cycle[k + 1])

          t_candidate = apply_3opt((e1, e2, e3), g, curr_cycle)
          c_score = t_candidate.size(weight="weight")

          # Update score, if necessary
          if c_score < score:
            score = c_score
            t = t_candidate
            improved = True
            break

        if improved:
          break

      if improved:
        break

  return t


if __name__ == "__main__":

  filenames = [
      "att48.txt", "gr21.txt", "ulysses22.txt", "hk48.txt", "berlin52.txt",
      "st70.txt", "pr76.txt"
  ]

  for file in filenames:
    g = read_in_graph("resources/" + file)

    print()
    print(25 * "=")
    print(file)

    t_s = process_time()
    tsp = tsp_3opt(g)
    t_e = process_time()
    print("Optimal tour weight (arbitrary node): ", tsp.size(weight="weight"))

    min_weight = float('inf')
    min_tour = tsp
    for node in g.nodes:
      tour = tsp_3opt(g, node)
      weight = tour.size(weight="weight")
      if weight < min_weight:
        min_weight = weight
        min_tour = tour

    print("Optimal tour weight (all nodes): ", min_weight)
