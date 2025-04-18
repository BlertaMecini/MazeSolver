import maze_solver
import time
import sys
import matplotlib.pyplot as plt
from statistics import mean, stdev

LOG_FILE = "mazesolver_test_results.txt"

# Temporary maze generation functions for detailed cases
def generate_best_case_maze(self, rows, cols):
    maze = [[1 if i == 0 or i == rows-1 or j == 0 or j == cols-1 else 0 
             for j in range(cols)] for i in range(rows)]
    self.maze = maze
    self.start = (0, 0)
    self.end = (rows-1, cols-1)
    self.path = []
    self.visited = set()

def generate_worst_case_maze(self, rows, cols):
    if rows % 2 == 0: rows += 1
    if cols % 2 == 0: cols += 1
    maze = [[1 for _ in range(cols)] for _ in range(rows)]
    for i in range(min(rows, cols) // 2):
        for j in range(i, cols - i): maze[i][j] = 0
        for j in range(i, cols - i): maze[rows-1-i][j] = 0
        for j in range(i, rows - i): maze[j][i] = 0
        for j in range(i, rows - i): maze[j][cols-1-i] = 0
    center_x, center_y = rows // 2, cols // 2
    maze[center_x][center_y] = 0
    self.maze = maze
    self.start = (0, 0)
    self.end = (center_x, center_y)
    self.path = []
    self.visited = set()

def generate_unsolvable_maze(self, rows, cols):
    self.generate_maze(rows, cols, 0.1)
    maze = self.maze
    maze[rows-1][cols-1] = 1
    self.maze = maze

def generate_blocked_maze(self, rows, cols):
    maze = [[1 for _ in range(cols)] for _ in range(rows)]
    maze[0][0] = 0
    maze[rows-1][cols-1] = 0
    self.maze = maze
    self.start = (0, 0)
    self.end = (rows-1, cols-1)
    self.path = []
    self.visited = set()

setattr(maze_solver.MazeGame, 'generate_best_case_maze', generate_best_case_maze)
setattr(maze_solver.MazeGame, 'generate_worst_case_maze', generate_worst_case_maze)
setattr(maze_solver.MazeGame, 'generate_unsolvable_maze', generate_unsolvable_maze)
setattr(maze_solver.MazeGame, 'generate_blocked_maze', generate_blocked_maze)

def log_results(test_name, size, density, time_taken, iterations, path_length, memory):
    with open(LOG_FILE, "a") as f:
        f.write(f"Test: {test_name}, Size: {size}, Density: {density:.2f}, "
                f"Time: {time_taken:.3f}s, Iterations: {iterations}, Path Length: {path_length}, "
                f"Memory: {memory} bytes\n")

def run_experiment(game, rows, cols, density, num_trials=10, gen_func='generate_maze'):
    times, iters, paths, mems = [], [], [], []
    for _ in range(num_trials):
        if gen_func == 'generate_maze':
            game.generate_maze(rows, cols, extra_wall_percent=density)
        else:
            getattr(game, gen_func)(rows, cols)
        if gen_func != 'generate_unsolvable_maze' and gen_func != 'generate_blocked_maze' and not game.check_solvable():
            continue  # Skip unsolvable mazes for normal cases
        game.path = []
        game.visited = set()
        game.iterations = 0
        start_time = time.time()
        solver = game.a_star()
        for _ in solver:
            game.iterations += 1
        time_taken = time.time() - start_time
        path_length = len(game.path)
        memory = sys.getsizeof(game.maze) + sys.getsizeof(game.visited) + sys.getsizeof(game.path)
        times.append(time_taken)
        iters.append(game.iterations)
        paths.append(path_length)
        mems.append(memory)
        log_results(f"{gen_func} {rows}x{cols} Density {density}", f"{rows}x{cols}", density, 
                    time_taken, game.iterations, path_length, memory)
    return (mean(times) if times else 0, stdev(times) if len(times) > 1 else 0, 
            mean(iters) if iters else 0, mean(paths) if paths else 0, mean(mems) if mems else 0)

def get_custom_sizes():
    sizes = []
    print("Enter maze sizes as 'rows,cols' (e.g., '10,10'). Type 'done' to finish:")
    while True:
        user_input = input("> ").strip().lower()
        if user_input == "done":
            break
        try:
            rows, cols = map(int, user_input.split(","))
            if rows > 0 and cols > 0:
                sizes.append((rows, cols))
            else:
                print("Rows and columns must be positive integers.")
        except ValueError:
            print("Invalid format. Use 'rows,cols' (e.g., '10,10').")
    return sizes if sizes else [(10, 10)]

def plot_size_graphs(results, sizes):
    size_labels = [f"{r}x{c}" for r, c in sizes]
    areas = [r[0] for r in results]
    times = [r[1] for r in results]
    errors = [r[2] for r in results]
    iters = [r[3] for r in results]
    paths = [r[4] for r in results]

    plt.figure(figsize=(12, 4))
    plt.subplot(1, 3, 1)
    plt.errorbar(areas, times, yerr=errors, fmt='o-', label="Runtime")
    plt.xticks(areas, size_labels, rotation=45)
    plt.xlabel("Maze Size")
    plt.ylabel("Time (s)")
    plt.title("Runtime vs. Maze Size")
    plt.grid(True)

    plt.subplot(1, 3, 2)
    plt.plot(areas, iters, 'o-', label="Iterations")
    plt.xticks(areas, size_labels, rotation=45)
    plt.xlabel("Maze Size")
    plt.ylabel("Iterations")
    plt.title("Iterations vs. Maze Size")
    plt.grid(True)

    plt.subplot(1, 3, 3)
    plt.plot(areas, paths, 'o-', label="Path Length")
    plt.xticks(areas, size_labels, rotation=45)
    plt.xlabel("Maze Size")
    plt.ylabel("Path Length")
    plt.title("Path Length vs. Maze Size")
    plt.grid(True)

    plt.tight_layout()
    plt.savefig("size_performance.png")
    plt.close()

def plot_density_graphs(results, rows, cols):
    densities = [r[0] for r in results]
    times = [r[1] for r in results]
    errors = [r[2] for r in results]
    iters = [r[3] for r in results]
    paths = [r[4] for r in results]

    plt.figure(figsize=(12, 4))
    plt.subplot(1, 3, 1)
    plt.errorbar(densities, times, yerr=errors, fmt='o-', label="Runtime")
    plt.xlabel("Extra Wall Removal (%)")
    plt.ylabel("Time (s)")
    plt.title(f"Runtime vs. Density ({rows}x{cols})")
    plt.grid(True)

    plt.subplot(1, 3, 2)
    plt.plot(densities, iters, 'o-', label="Iterations")
    plt.xlabel("Extra Wall Removal (%)")
    plt.ylabel("Iterations")
    plt.title(f"Iterations vs. Density ({rows}x{cols})")
    plt.grid(True)

    plt.subplot(1, 3, 3)
    plt.plot(densities, paths, 'o-', label="Path Length")
    plt.xlabel("Extra Wall Removal (%)")
    plt.ylabel("Path Length")
    plt.title(f"Path Length vs. Density ({rows}x{cols})")
    plt.grid(True)

    plt.tight_layout()
    plt.savefig("density_performance.png")
    plt.close()

def plot_detailed_cases(results):
    labels = ["Best (10x10)", "Worst (10x10)", "Edge Min (3x3)", "Edge Unsolvable (10x10)", "Edge Blocked (10x10)"]
    times = [r[1] for r in results]
    errors = [r[2] for r in results]
    iters = [r[3] for r in results]
    paths = [r[4] for r in results]

    plt.figure(figsize=(12, 4))
    plt.subplot(1, 3, 1)
    plt.bar(labels, times, yerr=errors, capsize=5)
    plt.xticks(rotation=45)
    plt.xlabel("Test Case")
    plt.ylabel("Time (s)")
    plt.title("Runtime vs. Test Case")
    plt.grid(True, axis='y')

    plt.subplot(1, 3, 2)
    plt.bar(labels, iters)
    plt.xticks(rotation=45)
    plt.xlabel("Test Case")
    plt.ylabel("Iterations")
    plt.title("Iterations vs. Test Case")
    plt.grid(True, axis='y')

    plt.subplot(1, 3, 3)
    plt.bar(labels, paths)
    plt.xticks(rotation=45)
    plt.xlabel("Test Case")
    plt.ylabel("Path Length")
    plt.title("Path Length vs. Test Case")
    plt.grid(True, axis='y')

    plt.tight_layout()
    plt.savefig("detailed_cases_performance.png")
    plt.close()

def test_experiments():
    game = maze_solver.MazeGame()
    with open(LOG_FILE, "w") as f:
        f.write("Test Results\n=================\n")

    # Experiment 1: Custom Maze Sizes
    sizes = get_custom_sizes()
    densities = [0.1]
    size_results = []
    print("\nExperiment 1: Varying Maze Size")
    for rows, cols in sizes:
        avg_time, std_time, avg_iters, avg_path, avg_mem = run_experiment(game, rows, cols, densities[0])
        size_results.append((rows * cols, avg_time, std_time, avg_iters, avg_path, avg_mem))
        print(f"Size {rows}x{cols}: Time={avg_time:.3f}s (σ={std_time:.3f}), "
              f"Iters={avg_iters:.0f}, Path={avg_path:.0f}, Mem={avg_mem:.0f} bytes")

    # Experiment 2: Vary Maze Density (using first custom size)
    densities = [0.0, 0.1, 0.3, 0.5]
    density_results = []
    rows, cols = sizes[0]
    print(f"\nExperiment 2: Varying Maze Density ({rows}x{cols})")
    for density in densities:
        avg_time, std_time, avg_iters, avg_path, avg_mem = run_experiment(game, rows, cols, density)
        density_results.append((density, avg_time, std_time, avg_iters, avg_path, avg_mem))
        print(f"Density {density:.2f}: Time={avg_time:.3f}s (σ={std_time:.3f}), "
              f"Iters={avg_iters:.0f}, Path={avg_path:.0f}, Mem={avg_mem:.0f} bytes")

    # New Section: Best, Worst, and Edge Cases
    detailed_results = []
    print("\nDetailed Test Cases: Best, Worst, and Edge Cases")
    # Best Case
    avg_time, std_time, avg_iters, avg_path, avg_mem = run_experiment(game, 10, 10, 0, gen_func='generate_best_case_maze')
    detailed_results.append((10 * 10, avg_time, std_time, avg_iters, avg_path, avg_mem))
    print(f"Best Case (10x10, Open): Time={avg_time:.3f}s (σ={std_time:.3f}), Iters={avg_iters:.0f}, Path={avg_path:.0f}, Mem={avg_mem:.0f} bytes")
    # Worst Case
    avg_time, std_time, avg_iters, avg_path, avg_mem = run_experiment(game, 10, 10, 0, gen_func='generate_worst_case_maze')
    detailed_results.append((10 * 10, avg_time, std_time, avg_iters, avg_path, avg_mem))
    print(f"Worst Case (10x10, Spiral): Time={avg_time:.3f}s (σ={std_time:.3f}), Iters={avg_iters:.0f}, Path={avg_path:.0f}, Mem={avg_mem:.0f} bytes")
    # Edge Case: Minimal Size
    avg_time, std_time, avg_iters, avg_path, avg_mem = run_experiment(game, 3, 3, 0.1)
    detailed_results.append((3 * 3, avg_time, std_time, avg_iters, avg_path, avg_mem))
    print(f"Edge Case (3x3, Min Size): Time={avg_time:.3f}s (σ={std_time:.3f}), Iters={avg_iters:.0f}, Path={avg_path:.0f}, Mem={avg_mem:.0f} bytes")
    # Edge Case: Unsolvable
    avg_time, std_time, avg_iters, avg_path, avg_mem = run_experiment(game, 10, 10, 0, gen_func='generate_unsolvable_maze')
    detailed_results.append((10 * 10, avg_time, std_time, avg_iters, avg_path, avg_mem))
    print(f"Edge Case (10x10, Unsolvable): Time={avg_time:.3f}s (σ={std_time:.3f}), Iters={avg_iters:.0f}, Path={avg_path:.0f}, Mem={avg_mem:.0f} bytes")
    # Edge Case: Fully Blocked
    avg_time, std_time, avg_iters, avg_path, avg_mem = run_experiment(game, 10, 10, 0, gen_func='generate_blocked_maze')
    detailed_results.append((10 * 10, avg_time, std_time, avg_iters, avg_path, avg_mem))
    print(f"Edge Case (10x10, Fully Blocked): Time={avg_time:.3f}s (σ={std_time:.3f}), Iters={avg_iters:.0f}, Path={avg_path:.0f}, Mem={avg_mem:.0f} bytes")

    # Generate Graphs
    plot_size_graphs(size_results, sizes)
    plot_density_graphs(density_results, rows, cols)
    plot_detailed_cases(detailed_results)
    print(f"\nResults logged to {LOG_FILE}")

if __name__ == "__main__":
    test_experiments()