# DPS970 Activity 1

## Question 1: Spam Filter Email Agent

### a) PEAS
- Performance measure: percentage of emails classified correctly; legitimate
  email wrongly sent to spam is the costliest error.
- Environment: .eml files (headers + text body), the allow list, restrict
  list, bad word list, and the spam/ and email/ directories.
- Actuators: moving the file into the spam directory or the email directory.
- Sensors: reading the .eml file (sender header, text body, text attachments).

### b) Task environment properties
- Fully observable: the whole email is available to the agent.
- Single agent: no other agents affect the outcome.
- Deterministic: the same email and lists always give the same result.
- Episodic: each email is classified independently of previous ones.
- Static: the email does not change while the agent decides.
- Discrete: finite set of files, words and two actions.
- Known: the rules for classification are given.

### c) Agent type
A simple reflex agent. The environment is fully observable and episodic, so
the correct action depends only on the current percept (one email). The rules
are fixed condition-action rules (allow list, restrict list, bad word count),
so no internal state, model, goal or learning is needed.

### d) Implementation
See q1_spam_agent/spam_agent.py. It follows SIMPLE-REFLEX-AGENT:
INTERPRET-INPUT -> RULE-MATCH -> action.
Rule order: allow list -> not spam; restrict list -> spam; more than 5 bad
words -> spam; otherwise not spam.
Assumptions: allow beats restrict if a domain is on both; every occurrence of
a bad word counts; subdomains match their parent domain.

## Question 2: Water Jug Search

### a) Problem formulation
- State: (a, b, c), gallons in the 12, 8 and 3 gallon jugs; 0<=a<=12,
  0<=b<=8, 0<=c<=3.
- Initial state: (0, 0, 0).
- Goal states: any state where a=1, b=1 or c=1.
- Actions: Fill(i), Empty(i), Pour(i, j).
- Transition model: Fill(i) sets jug i to its capacity. Empty(i) sets jug i
  to 0. Pour(i, j) moves amount = min(contents of i, capacity of j - contents
  of j) from i to j.
- Step cost: 1 per action.

### b) Heuristic
A heuristic can be defined, for example the smallest |amount - 1| over the
jugs, but it is not very informative. Reaching 1 often requires moving away
from it first (e.g. filling jugs to larger amounts), so the estimate does not
track real progress. That is why an uninformed search like BFS is suitable.

### c) Is a goal guaranteed to be reached?
A goal is reachable because gcd(12, 8, 3) = 1. For example: fill the 12
jug, pour into the 8, pour the remaining 4 into the 3, leaving 1 in the 12
jug. The state space is finite (at most 13 x 9 x 4 = 468 states), so BFS
with a reached set is complete: it either finds a goal or exhausts the space.
Since all step costs are equal it also finds a shortest solution (3 steps).
Not every algorithm is guaranteed: depth-first search without cycle checking
can loop forever (fill, empty, fill, empty...).

### d) Implementation
See q2_water_jugs/jugs.py, which follows BREADTH-FIRST-SEARCH (Figure 3.9):
FIFO queue, reached set, early goal test on generated children.