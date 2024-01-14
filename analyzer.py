import json
import matplotlib.pyplot as plt


def load(file):
    with open(file) as fr:
        return json.load(fr)

def plot_hist_of_errors(data, name):
    errors = []
    for task_name, sol in data.items():
        errors.append((abs(sol['optimal'] - sol['cost']) / float(sol['optimal'])) * 100)

    plt.figure(figsize=(15, 10))
    plt.title(name)
    plt.hist(errors)
    plt.show()


# for task_type in ["A", "B", "E"]:
#     plot_hist_of_errors(load(f"/home/emperornao/personal/cvrp/resources/result_{task_type}.json"), task_type)

