This Chess environment is based on https://github.com/patrik-ha/explainable-minichess

Rules and Game: https://greenchess.net/rules.php?v=microchess

More information: https://en.wikipedia.org/wiki/Microchess

## Microchess Agents 
This project explores intelligent gameplay on a compact 5×4 Microchess board, where classic chess dynamics shrink into a tighter, trickier arena. I implemented multiple agents using minimax search, heuristic evaluation, and (optionally) learning-based strategies. The environment, agents, and autograding pipeline were provided as part of the assignment framework.

### Project Structure
```
agents/
 ├── task1_agent.py      # Depth-2 minimax vs Random agent
 ├── task2_agent.py      # Depth-4 minimax vs Rational agent
 ├── task3_agent.py      # Best agent (search + heuristics/RL)
 ├── base_agent.py
requirements.txt
report.pdf
autograder.py
visualize_gameplay.py
```

### Tasks Overview
**Task 1 – Beat the Random Player**

- Implemented a depth-2 minimax agent with fast handcrafted evaluation.

- Designed to play within 5ms per move.

- Goal: ≥27 points across 100 matches.

**Task 2 – Play Against Rational Agent**

- Built a depth-4 minimax agent with richer evaluation:

  - material balance

  - mobility

  - king safety

  - threats/captures

- Runs under 100ms per move.

- Goal: ≥20 points across 100 matches.

**Task 3 – Best Agent**

- Designed a stronger agent using:

  - improved heuristics

  - optional learning (policy search / RL episodes)

  - search depth ≤5

- Must score ≥50 points vs Random agent.

### How to Run
**Install environment:**
```
python -m pip install -r requirements.txt
```

**Run agents using the autograder:**
```
python autograder.py --task 1
python autograder.py --task 2
python autograder.py --task 3
```
**Enable FEN logging for visualization:**
```
python autograder.py --task 1 --save_fens
python visualize_gameplay.py --fens_path path/to/fenfile.fen
```
### Key Features of My Agents

- Efficient minimax with smart pruning and move ordering.

- Lightweight evaluation tuned for 5×4 Microchess.

- Optional trained policy for Task 3.

