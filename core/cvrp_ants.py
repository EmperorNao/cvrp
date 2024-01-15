import copy
import numpy as np


class Node:
    def __init__(self, x, y, demand):
        self.x = x
        self.y = y
        self.demand = demand

class Vehicle:
    def __init__(self, capacity):
        self.capacity = capacity

def distance(node1, node2):
    return ((node1.x - node2.x) ** 2 + (node1.y - node2.y) ** 2) ** 0.5



class AntsSimulator:

    def __init__(self, params):
        self.alpha = params["alpha"]
        self.beta = params["beta"]
        self.rho = params["rho"]
        self.Q = params["Q"]
        self.q_0 = params["q_0"]
        self.k = params["k"]
        self.start_pheromone = params["start_pheromone"]
        self.max_iterations = params["max_iterations"]
        self.n_steps_without_up = params["n_steps_without_up"]

    def compute_distances(self, nodes):
        distance_matr = np.zeros((len(nodes), len(nodes)))
        for l_i, node_l in enumerate(nodes):
            for r_i, node_r in enumerate(nodes):
                distance_matr[l_i][r_i] = distance(node_l, node_r)
        return distance_matr

    def compute_cost(self, route, distances):
        s = 0
        for i in range(1, len(route)):
            s += distances[route[i - 1]][route[i]]
        return s

    def from_task(self, task):
        nodes = [Node(value[1], key, value[2]) for key, value in task.nodes.items()]
        vehicles = [Vehicle(task.capacity) for _ in range(task.n_vehicles)]
        return nodes, vehicles

    def simulate(self, nodes, vehicles):

        history = []

        n_nodes = len(nodes)
        n_vehicles = len(vehicles)
        capacity_ = vehicles[0].capacity
        pheromone_matrix = np.full((len(nodes), len(nodes)), self.start_pheromone)
        distance_matrix = self.compute_distances(nodes)
        demands_ = np.array([node.demand for node in nodes])

        best_cost = float("inf")
        best_routes = []

        step = 0
        for n_iter in range(self.max_iterations):

            vertexes_visited_ants_idx = [[[] for i in range(n_nodes)] for j in range(n_nodes)]
            ants_costs = np.zeros((self.k))
            best_local_cost = float("inf")
            best_local_routes = []

            for ant_idx in range(self.k):
                routes = []
                v_costs = np.zeros((len(vehicles)))
                demands = copy.copy(demands_)
                k_index = 0
                filled = set([0])

                while len(filled) != n_nodes:

                    capacity = capacity_
                    if len(routes) <= k_index:
                        routes.append([0])

                    while capacity != 0:
                        if not np.logical_and(demands != 0, demands < capacity).any():
                            routes.append([0])
                            break

                        current_node_idx = routes[k_index][-1]

                        probas = np.zeros(n_nodes)
                        for node_idx in range(1, len(nodes)):

                            if demands[node_idx] == 0 or demands[node_idx] > capacity:
                                continue
                            num = pheromone_matrix[current_node_idx][node_idx] ** self.alpha
                            denum = (1.0 / distance_matrix[current_node_idx][node_idx]) ** self.beta
                            probas[node_idx] = num / denum

                        probas /= probas.sum()

                        use_choice = np.random.choice([False, True], size=1, p=[self.q_0, 1 - self.q_0])[0]
                        if use_choice:
                            next_node = np.random.choice(np.arange(0, n_nodes), size=1, p=probas)[0]
                        else:
                            next_node = np.argmax(probas)
                        vertexes_visited_ants_idx[current_node_idx][next_node].append(ant_idx)

                        routes[k_index].append(next_node)
                        capacity -= demands[next_node]
                        if capacity < 0:
                            print("ERROR")
                        demands[next_node] = 0
                        filled.add(next_node)

                    if routes[k_index][-1] != 0:
                        routes[k_index].append(0)

                    k_index += 1
                    k_index %= n_vehicles

                for ts_index in range(n_vehicles):
                    v_costs[ts_index] = self.compute_cost(routes[ts_index], distance_matrix)

                s_cost = np.sum(v_costs)
                if s_cost < best_local_cost:
                    best_local_routes = copy.copy(routes)
                    best_local_cost = s_cost

                ants_costs[ant_idx] = s_cost

                # local update
                for route in routes:
                    for idx in range(1, len(route)):
                        x = route[idx - 1]
                        y = route[idx]
                        pheromone_matrix[x][y] = (1 - self.rho) * pheromone_matrix[x][y] + self.rho * self.start_pheromone

            best_vertexes_cost = [[0 for i in range(n_nodes)] for j in range(n_nodes)]
            for route in best_local_routes:
                for idx in range(1, len(route)):
                    best_vertexes_cost[route[idx - 1]][route[idx]] = best_local_cost

            for x in range(n_nodes):
                for y in range(n_nodes):
                    s = 0.0
                    # for ant_idx in vertexes_visited_ants_idx[x][y]:
                    #     s += self.Q / ants_costs[ant_idx]
                    s_best = 1.0
                    if best_vertexes_cost[x][y] != 0:
                        pheromone_matrix[x][y] = (1 - self.rho) * pheromone_matrix[x][y] + self.rho / best_vertexes_cost[x][y]

            if best_local_cost < best_cost:
                best_routes = copy.copy(best_local_routes)
                best_cost = best_local_cost
                step = 0
            history.append(best_cost)

            print(f"PH stats: {pheromone_matrix.mean()}, {pheromone_matrix.std()}")

            if step >= self.n_steps_without_up:
                print("Local minimum out")
                pheromone_matrix = np.full((len(nodes), len(nodes)), self.start_pheromone)

                best_vertexes_cost = [[0 for i in range(n_nodes)] for j in range(n_nodes)]
                for route in best_routes:
                    for idx in range(1, len(route)):
                        best_vertexes_cost[route[idx - 1]][route[idx]] = best_local_cost
                for x in range(n_nodes):
                    for y in range(n_nodes):
                        s_best = 0.0
                        if best_vertexes_cost[x][y] != 0:
                            s_best += best_vertexes_cost[x][y]
                        pheromone_matrix[x][y] = (1 - self.rho) * pheromone_matrix[x][y] + self.rho * s_best

                step = 0
                #break
            step += 1

            print(best_cost)

        return history, best_cost, best_routes


