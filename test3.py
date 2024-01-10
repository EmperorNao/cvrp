import numpy as np

from core.cvrp import run_ants
from core.primitives import SolutionData, Task
import matplotlib.pyplot as plt


t = Task()
t.from_file("/home/emperornao/personal/cvrp/resources/A/A-n32-k5.vrp")

sol = SolutionData()
sol.from_file("/home/emperornao/personal/cvrp/resources/A/A-n80-k10.sol")

from core.algorithm import Node, Vehicle, AntsSimulator

nodes = [Node(value[1], key, value[2]) for key, value in t.nodes.items()]
vehicles = [Vehicle(t.capacity) for veh in range(t.n_vehicles)]

params = {
    "alpha": 0.6,
    "beta": 0.9,
    "rho": 0.99,
    "Q": 400,
    "q_0": 0.1,
    "k": 50,
    "start_pheromone": 1.0,
    "max_iterations": 1000,
    "n_steps_without_up": 10,
    "runs": 5
}

from core.cvrp import get_task
_, cost, _ = run_ants(t, params)

