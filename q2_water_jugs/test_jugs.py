from jugs import JugProblem, breadth_first_search, solution


def test_initial_state_is_not_goal():
    problem = JugProblem()
    assert not problem.is_goal(problem.initial)


def test_pour_transitions():
    problem = JugProblem()
    assert problem.result((12, 0, 0), ("pour", 0, 1)) == (4, 8, 0)
    assert problem.result((4, 8, 0), ("pour", 0, 2)) == (1, 8, 3)
    assert problem.result((0, 6, 3), ("pour", 2, 1)) == (0, 8, 1)


def test_bfs_finds_goal():
    problem = JugProblem()
    goal = breadth_first_search(problem)
    assert goal is not None
    assert problem.is_goal(goal.state)


def test_solution_is_shortest():
    problem = JugProblem()
    goal = breadth_first_search(problem)
    # fill 12, pour 12->8, pour 12->3 leaves 1 gallon in the 12 jug
    assert goal.path_cost == 3


def test_every_step_is_legal():
    problem = JugProblem()
    goal = breadth_first_search(problem)
    state = problem.initial
    for action, new_state in solution(goal):
        assert action in problem.actions(state)
        assert problem.result(state, action) == new_state
        state = new_state
    assert problem.is_goal(state)


def test_unsolvable_returns_failure():
    # capacities 4 and 6 can only ever make even amounts, so 1 is unreachable
    problem = JugProblem(capacities=(4, 6), target=1)
    assert breadth_first_search(problem) is None