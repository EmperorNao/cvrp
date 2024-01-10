import os.path


def read_vrp(path: str) -> dict:
    if not os.path.exists(path):
        raise FileNotFoundError(path)

    lines = None
    with open(path) as f:
        lines = f.readlines()

    if not lines:
        raise Exception(f"Task from {path} has incorrect inner format")

    solution_dict = {"nodes": [], "nodes_demand": []}
    index = 0
    while index < len(lines):
        line = lines[index]
        if line.startswith("NAME"):
            solution_dict["name"] = line.rsplit(":")[1].rstrip()
        elif line.startswith("COMMENT"):
            solution_dict["comment"] = line.rsplit(":")[1].rstrip()
        elif line.startswith("DIMENSION"):
            solution_dict["dimension"] = int(line.rsplit(":")[1].rstrip())
        elif line.startswith("CAPACITY"):
            solution_dict["capacity"] = int(line.rsplit(":")[1].rstrip())
        elif line.startswith("NODE_COORD_SECTION"):
            if "dimension" not in solution_dict:
                raise Exception(f"Task from {path} has incorrect inner format")
            dimension = solution_dict["dimension"]
            for node_index in range(dimension):
                index += 1
                line = lines[index]
                node_number, node_x, node_y = map(int, line.strip().split(" "))
                solution_dict["nodes"].append([node_number, node_x, node_y])
        elif line.startswith("DEMAND_SECTION"):
            if "dimension" not in solution_dict:
                raise Exception(f"Task from {path} has incorrect inner format")
            dimension = solution_dict["dimension"]
            for node_index in range(dimension):
                index += 1
                line = lines[index]
                node_number, node_demand = map(int, line.strip().split(" "))
                solution_dict["nodes_demand"].append([node_number, node_demand])

        index += 1

    return solution_dict


def read_solution(path: str) -> dict:
    if not os.path.exists(path):
        raise FileNotFoundError(path)

    lines = None
    with open(path) as f:
        lines = f.readlines()

    if not lines:
        raise Exception(f"Solution from {path} has incorrect inner format")

    route_index = 0
    solution_dict = {"routes": [], "cost": float("inf")}
    for line in lines:
        if line.startswith("Route"):
            route = line.rsplit(":", 1)[1]
            route_list = list(map(lambda x: int(x), route.strip().split(' ')))

            solution_dict["routes"].append(route_list)
            route_index += 1
        elif line.startswith("Cost"):
            cost = line.strip().rsplit(" ")[1]
            solution_dict["cost"] = int(cost)

    return solution_dict
