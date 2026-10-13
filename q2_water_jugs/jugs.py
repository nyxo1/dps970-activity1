"""
Water jug problem solved with breadth-first search (AIMA Figure 3.9).

State        : (a, b, c) gallons in the 12, 8 and 3 gallon jugs
Initial      : (0, 0, 0)
Goal         : any jug holds exactly 1 gallon
Actions      : ("fill", i), ("empty", i), ("pour", i, j)
Transition   : fill -> jug i = capacity; empty -> jug i = 0;
               pour i into j -> amount = min(jug i contents, space left in j)
Step cost    : 1 per action
"""
from collections import deque

CAPACITIES = (12, 8, 3)


class JugProblem:
    def __init__(self, capacities=CAPACITIES, target=1):
        self.capacities = capacities
        self.initial = tuple(0 for _ in capacities)
        self.target = target

    def is_goal(self, state):
        return self.target in state

    def actions(self, state):
        n = len(self.capacities)
        acts = []
        for i in range(n):
            acts.append(("fill", i))
            acts.append(("empty", i))
            for j in range(n):
                if i != j:
                    acts.append(("pour", i, j))
        return acts

    def result(self, state, action):
        s = list(state)
        kind = action[0]
        if kind == "fill":
            i = action[1]
            s[i] = self.capacities[i]
        elif kind == "empty":
            i = action[1]
            s[i] = 0
        else:  # pour
            i, j = action[1], action[2]
            amount = min(s[i], self.capacities[j] - s[j])
            s[i] -= amount
            s[j] += amount
        return tuple(s)

    def describe(self, action):
        caps = self.capacities
        if action[0] == "fill":
            return f"Fill the {caps[action[1]]}-gallon jug"
        if action[0] == "empty":
            return f"Empty the {caps[action[1]]}-gallon jug"
        return f"Pour the {caps[action[1]]}-gallon jug into the {caps[action[2]]}-gallon jug"


class Node:
    def __init__(self, state, parent=None, action=None, path_cost=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost


def expand(problem, node):
    for action in problem.actions(node.state):
        s = problem.result(node.state, action)
        yield Node(s, node, action, node.path_cost + 1)


def breadth_first_search(problem):
    """Returns a goal Node, or None (failure)."""
    node = Node(problem.initial)
    if problem.is_goal(node.state):
        return node
    frontier = deque([node])  # FIFO queue
    reached = {problem.initial}
    while frontier:
        node = frontier.popleft()
        for child in expand(problem, node):
            s = child.state
            if problem.is_goal(s):  # early goal test
                return child
            if s not in reached:
                reached.add(s)
                frontier.append(child)
    return None


def solution(node):
    """List of (action, resulting_state) from the initial state to node."""
    steps = []
    while node.parent is not None:
        steps.append((node.action, node.state))
        node = node.parent
    steps.reverse()
    return steps


if __name__ == "__main__":
    problem = JugProblem()
    goal = breadth_first_search(problem)
    if goal is None:
        print("No solution found")
    else:
        print(f"Start: {problem.initial}")
        for n, (action, state) in enumerate(solution(goal), 1):
            print(f"{n}. {problem.describe(action)} -> {state}")
        print(f"Solved in {goal.path_cost} steps")