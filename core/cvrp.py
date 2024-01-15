import copy
import time
from tqdm import tqdm
from core.primitives import SolutionData, Task
from core.cvrp_ants import Node, Vehicle, AntsSimulator


def get_task(vrp_file):
    t = Task()
    t.from_file(vrp_file)
    return t

def get_solution(sol_file):
    s = SolutionData()
    s.from_file(sol_file)
    return s


def run_ants(task, params):

    sim = AntsSimulator(params)

    best_run_cost = float("inf")
    best_history = []
    best_solution = []
    for r in range(params["runs"]):
        print("RUN")
        history, cost, route = sim.simulate(*sim.from_task(task))
        if cost < best_run_cost:
            best_run_cost = cost
            best_history = history
            best_solution = route

    return best_history, best_run_cost, best_solution


def params_optimization(task, grid):

    params_list = [key for key in reversed(sorted(grid.keys(), key=lambda x: len(grid[x])))]
    current_params = {key: grid[key][0] for key in params_list}
    return check_params(task, grid, current_params, params_list, 0)


def check_params(task, params_grid, current_params, params_list, current_index):
    key = params_list[current_index]

    best_cost = float("inf")
    best_params = {}
    for param in params_grid[key]:
        print(f"{key}: {param}")
        current_params[key] = param
        _, cost, _ = run_ants(task, current_params)
        if cost < best_cost:
            best_cost = cost
            best_params = copy.copy(current_params)
        if current_index + 1 < len(params_list) and len(params_grid[params_list[current_index + 1]]) > 1:
            cost, best_params = check_params(task, params_grid, copy.copy(current_params), params_list, current_index + 1)
            if cost < best_cost:
                best_cost = cost
                best_params = copy.copy(current_params)
    return best_cost, best_params


def run_tasks(tasks, params):
    history = []

    for task in tqdm(tasks):
        start_task = time.perf_counter_ns()
        _, cost, _ = run_ants(task, params)
        end_task = time.perf_counter_ns()
        history.append({"cost": cost, "time": end_task - start_task})

    return history