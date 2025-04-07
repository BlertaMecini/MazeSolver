# Maze Solver

## Overview
Maze Solver is a Python application that generates random mazes and solves them using the A* pathfinding algorithm, visualized in real-time with Pygame. Developed as part of my master’s studies, it offers an interactive experience with predefined difficulty levels and a dynamic solving animation.

## Problem Statement
This project aims to create an efficient maze-solving tool that:
- Generates solvable mazes of varying difficulty.
- Implements A* to find the shortest path from start to goal.
- Visualizes the solving process step-by-step.
- Displays performance metrics like solving time and iterations.

## Features
- **Predefined Mazes**: Select from Easy (11x11), Medium (21x21), or Hard (31x31) levels.
- **(A star) Algorithm**: Computes the shortest path efficiently.
- **Real-time Visualization**: Shows visited cells (blue) and the final path (yellow).
- **Performance Metrics**: Displays solving time and iteration count.
- **User Interface**: Gradient menu, buttons (Start, Back, Restart), and a pulsating alert.

## Refined Design

### 1. Data Structures
- **Grid Representation**: 2D list where `1` = wall, `0` = path, with start (0,0) and end (rows-1, cols-1).
- **Priority Queue**: Uses `heapq` to manage nodes by `f` cost (g + h) for A*.
- **Tracking**: Sets and dictionaries store visited cells, g-scores, f-scores, and parent pointers.

### 2. Algorithm Implementation
- **Maze Generation**: Depth-first search (DFS) with extra random paths (10% of cells) ensures solvability and variety.
- **A***:
  - **G Cost**: Distance from start (1 per step).
  - **H Cost**: Manhattan distance (`|x1 - x2| + |y1 - y2|`).
  - **F Cost**: `g + h`, prioritizing exploration of lowest-cost nodes.
  - Explores four directions (up, down, left, right) until the goal is reached.

### 3. User Interface (Pygame)
- **Visualization**: Grid with colors for walls (black), start (green), end (red), visited (blue), and path (yellow).
- **Controls**: Mouse clicks on buttons to start solving, return to menu, or restart.
- **Menu**: Gradient background with difficulty options.

## Complexity Analysis
- **Maze Generation (DFS)**:
  - **Time**: O(rows * cols) – DFS visits each cell, plus extra paths.
  - **Space**: O(rows * cols) – Grid and visited set.
- **A***:
  - **Time**: O(rows * cols * log(rows * cols)) – Heap operations dominate in worst case.
  - **Space**: O(rows * cols) – Stores grid, queue, and tracking data.

## Prerequisites
- **Python 3.7+**
- **Pygame**: Install with:
  ```bash
  pip install pygame

## How to run the app
**1. Clone the Repository:**
```bash
git clone https://github.com/BlertaMecini/MazeSolver.git
cd MazeSolver
```
**2. Run the script:**
```bash
python maze_solver.py
```
**3. For tests run the script:**
```bash
python test_maze_solver.py
```
**3. Interact:**
- **Menu:** Click "Easy," "Medium," or "Hard."
- **Playing:** Click "Start" to solve, "Back" to menu.
- **Solved:** Click "Restart" or "X" on alert.

## Controls
- **Mouse Left Click:** Interact with buttons (Start, Back, Restart, difficulty selection).
- **Window Close:** Exit the app.

## Future Improvements
- Add multiple pathfinding algorithms (e.g., Dijkstra’s) for comparision.
- Support custom maze sizes and maze generation.
- Enhance performance for larger grids.
