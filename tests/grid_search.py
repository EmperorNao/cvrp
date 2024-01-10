import os
from constants import LOCAL_DIR
from core.cvrp import params_optimization, get_task


params_grid = {
    "alpha": [0.8, 1.5, 2.5],
    "beta": [0.5, 1.5, 2.5],
    "rho": [0.99, 0.9, 0.6],
    "Q": [100],
    "q_0": [0.0, 0.1, 0.3],
    "k": [100],
    "start_pheromone": [1.0],
    "max_iterations": [500],
    "n_steps_without_up": [10, 20, 30],
    "runs": [5]
}

task = get_task(os.path.join(LOCAL_DIR, "resources/A/A-n32-k5.vrp"))
cost, params = params_optimization(task, params_grid)
print(cost, params)