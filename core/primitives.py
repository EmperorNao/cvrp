import copy

import numpy as np

from vrp_io.reader import read_vrp, read_solution


class Task:
    def __init__(self):
        self.nodes = {}
        self.capacity = float("inf")
        self.n_vehicles = float("inf")
        self.name = ""
        self.dimension = ""
        self.data = None
        self.node_coord = None
        self.demand = None
        self.depot = None
        self.edge_weight = None

    def compute_distances(self, nodes):
        def distance(node1, node2):
            return ((node1[0] - node2[0]) ** 2 + (node1[1] - node2[1]) ** 2) ** 0.5
        distance_matr = np.zeros((len(nodes), len(nodes)))
        for idx_l, node_l in enumerate(nodes):
            for idx_r, node_r in enumerate(nodes):
                distance_matr[idx_l][idx_r] = distance(node_l, node_r)
        return distance_matr

    def from_dict(self, task: dict):
        self.name = task["name"]
        self.comment = task["comment"]
        self.dimension = task["dimension"]
        self.capacity = task["capacity"]
        self.n_vehicles = int(self.name.rsplit("-", 1)[1][1:])
        self.node_coord = np.array(task["nodes"])
        self.demand = np.array([node[1] for node in task["nodes_demand"]])
        self.depot = np.array([0])
        self.edge_weight = np.array(self.compute_distances(task['nodes']))
        self.data = {
            "name": self.name,
            "comment": self.comment,
            "dimension": self.dimension,
            "capacity": self.capacity,
            "n_vehicles": self.n_vehicles,
            "node_coord": self.node_coord,
            "demand": self.demand,
            "depot": self.depot,
            "edge_weight": self.edge_weight,
        }

    def from_file(self, path: str):
        task_dict = read_vrp(path)
        self.from_dict(task_dict)


class SolutionData:
    def __init__(self):
        self.routes = []
        self.cost = float("inf")

    def from_dict(self, solution: dict):
        self.routes = solution["routes"]
        self.cost = solution["cost"]

    def from_file(self, path: str):
        solution_dict = read_solution(path)
        self.from_dict(solution_dict)


class CvrpSolutionState:
    def __init__(self, distance, routes, unassigned=None):
        self.distance = distance
        self.routes = routes
        self.unassigned = unassigned if unassigned is not None else []
        self.time = None

    def set_time(self, time):
        self.time = time

    def get_time(self):
        return self.time

    def copy(self):
        return CvrpSolutionState(self.distance, copy.deepcopy(self.routes), self.unassigned.copy())

    def route_cost(self, route):
        tour = [0] + route + [0]
        return sum(self.distance[tour[idx]][tour[idx + 1]] for idx in range(len(tour) - 1))

    def find_route(self, customer):
        for route in self.routes:
            if customer in route:
                return route
        raise ValueError(f"Solution does not contain customer {customer}.")

    def objective(self):
        return sum(self.route_cost(route) for route in self.routes)

    @property
    def cost(self):
        return self.objective()
