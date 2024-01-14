import logging
import time
from typing import Dict, List, Optional, Protocol, Tuple

import numpy as np

from core.primitives import CvrpSolutionState


class CVRPALNS:

    MAX_STRING_REMOVALS = 2
    MAX_STRING_SIZE = 12

    def __init__(self, accept_start_gap, accept_end_gap, accept_num_iters, stop_max_iterations, max_runtime):
        self.accept_start_gap = accept_start_gap
        self.accept_end_gap = accept_end_gap
        self.accept_num_iters = accept_num_iters

        self.stop_max_iterations = stop_max_iterations
        self.max_runtime = max_runtime

    def reset(self, init):
        self.start_threshold = self.accept_start_gap * init.cost
        self.end_threshold = self.accept_end_gap * init.cost
        self.step = (self.start_threshold - self.end_threshold) / self.accept_num_iters
        self.threshold_ = self.start_threshold

        self._target = None
        self._counter = 0
        self._start_runtime = time.perf_counter()

    def stop_criterion(self, best, curr):
        if self._target is None or best.cost < self._target:
            self._target = best.cost
            self._counter = 0
        else:
            self._counter += 1

        return self._counter >= self.stop_max_iterations or \
            time.perf_counter() - self._start_runtime > self.max_runtime

    def accept(self, best, curr, cand):
        baseline = best
        self.threshold_ = max(self.end_threshold, self.threshold_ - self.step)
        return cand.cost - baseline.cost <= self.threshold_

    def nearest_neighbor(self, data):
        """
        Build a solution by iteratively constructing routes, where the nearest
        customer is added until the route has met the vehicle capacity limit.
        """
        routes = []
        unvisited = set(range(1, data["dimension"]))

        while unvisited:
            route = [0]  # Start at the depot
            route_demands = 0

            while unvisited:
                # Add the nearest unvisited customer to the route till max capacity
                current = route[-1]
                nearest = [nb for nb in self.neighbors(data, current) if nb in unvisited][0]

                if route_demands + data["demand"][nearest] > data["capacity"]:
                    break

                route.append(nearest)
                unvisited.remove(nearest)
                route_demands += data["demand"][nearest]

            customers = route[1:]  # Remove the depot
            routes.append(customers)

        return CvrpSolutionState(data['edge_weight'], routes)

    def neighbors(self, data, customer):
        locations = np.argsort(data["edge_weight"][customer])
        return locations[locations != 0]

    def destroy_operator(self, data, state):

        def remove_string(route, cust, max_string_size):
            # Find consecutive indices to remove that contain the customer
            size = np.random.randint(1, min(len(route), max_string_size) + 1)
            start = route.index(cust) - np.random.randint(size)
            idcs = [idx % len(route) for idx in range(start, start + size)]

            # Remove indices in descending order
            removed_customers = []
            for idx in sorted(idcs, reverse=True):
                removed_customers.append(route.pop(idx))

            return removed_customers

        destroyed = state.copy()

        avg_route_size = int(np.mean([len(route) for route in state.routes]))
        max_string_size = max(CVRPALNS.MAX_STRING_SIZE, avg_route_size)
        max_string_removals = min(len(state.routes), CVRPALNS.MAX_STRING_REMOVALS)

        destroyed_routes = []
        center = np.random.randint(1, data["dimension"])

        for customer in self.neighbors(data, center):
            if len(destroyed_routes) >= max_string_removals:
                break

            if customer in destroyed.unassigned:
                continue

            route = destroyed.find_route(customer)
            if route in destroyed_routes:
                continue

            customers = remove_string(route, customer, max_string_size)
            destroyed.unassigned.extend(customers)
            destroyed_routes.append(route)

        return destroyed

    def repair_operator(self, data, state):

        def insert_cost(customer, route, idx):
            dist = data["edge_weight"]
            pred = 0 if idx == 0 else route[idx - 1]
            succ = 0 if idx == len(route) else route[idx]

            return dist[pred][customer] + dist[customer][succ] - dist[pred][succ]

        def can_insert(customer, route):
            total = data["demand"][route].sum() + data["demand"][customer]
            return total <= data["capacity"]

        def best_insert(customer, state):
            best_cost, best_route, best_idx = None, None, None

            for route in state.routes:
                for idx in range(len(route) + 1):

                    if can_insert(customer, route):
                        cost = insert_cost(customer, route, idx)

                        if best_cost is None or cost < best_cost:
                            best_cost, best_route, best_idx = cost, route, idx

            return best_route, best_idx

        np.random.shuffle(state.unassigned)

        while len(state.unassigned) != 0:
            customer = state.unassigned.pop()
            route, idx = best_insert(customer, state)

            if route is not None:
                route.insert(idx, customer)
            else:
                state.routes.append([customer])

        return state

    def eval(self, best, curr, cand):

        # best
        if cand.cost < best.cost:
            return cand, cand

        # accept or better
        if self.accept(best, curr, cand):
            return best, cand

        return best, curr

    def __call__(self, data):
        curr = best = self.nearest_neighbor(data)
        self.reset(curr)

        while not self.stop_criterion(best, curr):
            destroyed = self.destroy_operator(data, curr)
            cand = self.repair_operator(data, destroyed)
            best, curr = self.eval(best, curr, cand)

        return best


def custom_alns_solver(data):

    alns = CVRPALNS(0.02, 0.0, 6000, 2500, 30)
    solution = alns(data)
    return solution