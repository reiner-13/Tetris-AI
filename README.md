![](https://i.imgur.com/mgKOCl1.gif)

## Setup
*Works with Python 3.12.x*

1. Clone the repository on your system.
```git clone https://github.com/reiner-13/Tetris-AI.git```

2. Using Pip, install the required libraries.
```pip install -r requirements.txt```

3. To run the bot normally, use:
```python main.py```

4. To run the genetic algorithm for finding weights, edit the `ga_instance` parameters to your liking and use:
```python mainGA.py```

## Background
The Tetris Bot was created as a semester-long project for Artificial Intelligence (CPSC 476) at Slippery Rock University.

## How it Works
The Tetris Bot works by creating a tree of possible moves, evaluating those moves based on metrics, and moving the current piece to the target location.

Firstly, the tree is made of TreeNode instances which hold certain values about the piece and board it is associated with. This includes the coordinates of the piece, the orientation of the piece, and various metrics about the board state. It creates these nodes in a depth-first manner up to depth 2. Depth 1 contains all possible configurations of the current piece and depth 2 the next piece.

Next, each node is fed through the evaluation function. This evaluation determines how advantageous the node’s position is. It looks at the average height of the columns, bumpiness, hole count, and line count. The function contains algorithms for each of these metrics. 

After it finds these values, it dots them with associated weight values. These weight values determine how important the metric is and were determined using a genetic algorithm. They are heuristic, not optimal. Once it creates the evaluation for the node, the bot determines the path to take in the tree by looking at the grandchild nodes with the lowest evaluation values. Once it determines a path, it will move the current piece to the target position.
