import os
import json
import glob

import vrplib
from constants import LOCAL_DIR
from core.cvrp import get_solution
from tqdm import tqdm

from core.cvrp_alns import custom_alns_solver


def run_alns(solver, path):
    history = {}

    tasks_path = glob.glob(os.path.join(path, '*' + ".vrp"))
    sols_path = glob.glob(os.path.join(path, '*' + ".sol"))

    for task_path, sol_path in tqdm(zip(sorted(tasks_path), sorted(sols_path))):
        task_name = task_path.rsplit("/", 1)[1].strip(".vrp")
        data = vrplib.read_instance(task_path)
        optimal = get_solution(sol_path).cost
        history[task_name] = {}

        history[task_name]["name"] = task_name
        history[task_name]["optimal"] = optimal

        sol = solver(data)

        history[task_name]['time'] = float(sol.get_time())
        history[task_name]['cost'] = float(sol.cost)
        history[task_name]['routes'] = [[int(vert) for vert in route] for route in sol.routes]

    return history


def save_history(history, path):
    with open(path, 'w') as fp:
        json.dump(history, fp, indent=4)


for task_type in ['A', 'B', 'E']:
    hist = run_alns(custom_alns_solver, os.path.join(LOCAL_DIR, "resources", task_type))
    save_history(hist, os.path.join(LOCAL_DIR, "resources", f"result_{task_type}_custom.json"))