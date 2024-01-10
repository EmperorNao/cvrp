import numpy as np
from vrp_io.reader import read_vrp, read_solution


class Task:
    def __init__(self):
        self.nodes = {}
        self.capacity = float("inf")
        self.n_vehicles = float("inf")
        self.name = ""
        self.dimension = ""

    def from_dict(self, task: dict):
        self.capacity = task["capacity"]
        self.dimension = task["dimension"]
        self.name = task["name"]
        self.n_vehicles = int(self.name.rsplit("-", 1)[1][1:])
        nodes = task["nodes"]
        nodes_demand = task["nodes_demand"]
        for node_pos, node_dem in zip(nodes, nodes_demand):
            node_id_pos, node_x, node_y = node_pos
            node_id_dem, node_demand = node_dem
            self.nodes[node_id_pos] = [node_x, node_y, node_demand]

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


class Parameters:

    def __init__(self):
        self.number_generations = 100000
        self.population_size = 800
        self.mutation_proba = 0.15
        self.crossingover_proba = 0.85
