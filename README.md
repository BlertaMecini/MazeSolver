# MazeSolver

## Overview

Maze Solver is a Python-based application that allows users to interact with mazes, either by selecting predefined ones or creating their own. The application uses the A* (A-star) pathfinding algorithm to find the shortest path from a start point to a goal, visualizing the solving process in real-time using Pygame.

## Problem Statement

The goal of this project is to implement an interactive maze solver that demonstrates the A* algorithm efficiently. The application should:

* Allow users to select predefined mazes or create their own.

* Visualize the solving process dynamically.

* Measure and display the solving speed.

* Provide an interactive, game-like experience for users.

## Features

* Predefined Mazes: Choose from different levels (easy, medium, hard).

* Custom Maze Creation: Draw your own maze by placing walls, start, and goal points.

* A* Algorithm Implementation: Find the shortest path efficiently.

* Real-time Visualization: See the algorithm solving the maze step by step.

* Performance Metrics: Display solving speed and step count.

* User Controls: Start, pause, reset the solver.

## Refined Design

1. Data Structures

Grid Representation: A 2D list representing open spaces, walls, start, and goal.

Node Class: Holds information like position, cost values (g, h, f), and parent reference.

Priority Queue (Heap): Used for efficient node selection in A*.

2. Algorithm Implementation

A* algorithm is used for pathfinding, calculating:

G Cost: Distance from start to current node.

H Cost: Heuristic estimation to goal (Manhattan distance).

F Cost: Sum of G and H.

Nodes are explored based on the lowest F cost until the goal is reached.

3. User Interface (Pygame)

Grid-based visualization where different colors represent walls, paths, and visited nodes.

Mouse interactions for maze creation.

Keyboard shortcuts for controlling execution.

## Complexity Analysis

### Time Complexity:

A Algorithm:* O(n log n) (with a priority queue like a binary heap).

Worst-case scenario approaches O(b^d), where b = branching factor, d = depth of the solution.

### Space Complexity:

O(n), where n is the number of nodes stored in memory.

## Prerequisites

Ensure you have the following installed:

* Python 3.7+

* Pygame (for visualization)

`pip install pygame`

## How to Run the App

Clone the Repository:

`git clone https://github.com/BlertaMecini/MazeSolver.git`

`cd MazeSolver`

Run the Python Script:

`python maze_solver.py`

## Controls

Left Click: Place/remove walls.

Right Click: Set start or goal.

S Key: Start solving.

R Key: Reset the maze.

## Future Improvements

Implementing additional pathfinding algorithms (Dijkstra, BFS, DFS).

Allowing different heuristic functions for A*.

Performance optimizations.
