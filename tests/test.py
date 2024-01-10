import os
import json
import glob
from core.cvrp import get_task, get_solution, run_ants, run_tasks
from constants import LOCAL_DIR


for task_type in ["A", "B", "E"]:

    tasks_path = glob.glob(os.path.join(LOCAL_DIR, "resources", task_type, '*' + ".vrp"))
    sols_path = glob.glob(os.path.join(LOCAL_DIR, "resources", task_type, '*' + ".sol"))

    params = {
        "alpha": 0.8,
        "beta": 0.5,
        "rho": 0.9,
        "Q": 100,
        "q_0": 0.0,
        "k": 100,
        "start_pheromone": 1.0,
        "max_iterations": 200,
        "n_steps_without_up": 10,
        "runs": 5
    }

    task_names = []
    optimals = []
    true_tasks = []
    for task_path, sol_path in zip(sorted(tasks_path), sorted(sols_path)):
        task_name = task_path.rsplit("/", 1)[1].strip(".vrp")
        task_names.append(task_name)
        true_tasks.append(get_task(task_path))
        optimals.append(get_solution(sol_path).cost)

    history = run_tasks(true_tasks, params)

    for i, (task_name, optimal) in enumerate(zip(task_names, optimals)):
        history[i]["optimal"] = optimal
        history[i]["name"] = task_name

    print(history)
    with open(os.path.join(LOCAL_DIR, "resources", f"result_{task_type}.json"), 'w') as fp:
        json.dump(history, fp)
