import os
import json
import numpy as np
import matplotlib.pyplot as plt
from constants import LOCAL_DIR


def load(file):
    with open(file) as fr:
        return json.load(fr)


def plot_hist(data, name):
    plt.figure(figsize=(15, 10))
    plt.title(name, fontdict={'fontsize': 20})
    plt.hist(data)
    plt.show()


def get_errors(data):
    errors = []
    for sol in data:
        errors.append((abs(sol['optimal'] - sol['cost']) / float(sol['optimal'])) * 100)
    return errors


def get_time(data):
    time = []
    for sol in data:
        time.append(int(sol['time']))
    return time


if __name__ == "__main__":
    data = {}
    for task_type in ["A", "B", "E"]:
        data[task_type] = load(os.path.join(LOCAL_DIR, "resources", f"result_{task_type}_custom.json"))

    for task_type in ["A", "B", "E"]:
        errors = get_errors(data[task_type].values())
        time = get_time(data[task_type].values())
        avg_time = np.mean(time)
        count = len(errors)
        avg_error = np.mean(errors)
        std_error = np.std(errors)
        median_error = np.median(errors)
        plot_hist(errors,
                  f"{task_type} tasks, count =  {count}, avg_time = {avg_time}\n"
                  f"avg error = {avg_error}, median error = {median_error}, std error = {std_error}"
                  )

    all_data = []
    for key, d in data.items():
        for tname, t_d in d.items():
            all_data.append(t_d)

    def filter_by_size(data, concrete_filter):
        return list(filter(concrete_filter, data))

    def get_size(data):
        return int(data['name'].split('-')[1].strip('n'))

    small_data = filter_by_size(all_data, lambda x: get_size(x) <= 30)
    medium_data = filter_by_size(all_data, lambda x: 30 < get_size(x) <= 60)
    large_data = filter_by_size(all_data, lambda x: get_size(x) > 60)

    for task_type, data in {"small": small_data, "medium": medium_data, "large": large_data}.items():
        errors = get_errors(data)
        time = get_time(data)
        avg_time = np.mean(time)
        count = len(errors)
        avg_error = np.mean(errors)
        std_error = np.std(errors)
        median_error = np.median(errors)
        plot_hist(errors,
                  f"{task_type} tasks, count =  {count}, avg_time = {avg_time}\n"
                  f"avg error = {avg_error}, median error = {median_error}, std error = {std_error}"
                  )

    size = [get_size(d) for d in all_data]
    time = get_time(all_data)
    idxs = np.argsort(size)

    plt.figure(figsize=(15, 10))
    plt.title("T(N) dependency", fontdict={'fontsize': 20})
    plt.xlabel("N, nodes", fontdict={'fontsize': 20})
    plt.ylabel("T, seconds", fontdict={'fontsize': 20})
    plt.plot(np.array(size)[idxs], np.array(time)[idxs])
    plt.show()





