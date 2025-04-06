import maze_solver
import time
import sys
import matplotlib.pyplot as plt
from statistics import mean, stdev

LOG_FILE = "mazesolver_test_results.txt"

def log_results(test_name, size, density, time_taken, iterations, path_length, memory):
    # Log detailed results for each trial
    with open(LOG_FILE, "a") as f:
        f.write(f"Test: {test_name}, Size: {size}, Density: {density:.2f}, "
                f"Time: {time_taken:.3f}s, Iterations: {iterations}, Path Length: {path_length}, "
                f"Memory: {memory} bytes\n")

def run_experiment(game, rows, cols, density, num_trials=10):
    # Run multiple trials for a given size and density
    times, iters, paths, mems = [], [], [], []
    for _ in range(num_trials):
        game.generate_maze(rows, cols, extra_wall_percent=density)
        if game.check_solvable():
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
            log_results(f"{rows}x{cols} Density {density}", f"{rows}x{cols}", density, 
                        time_taken, game.iterations, path_length, memory)
    return mean(times), stdev(times), mean(iters), mean(paths), mean(mems)

def get_custom_sizes():
    # Prompt user to input custom maze sizes
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
    return sizes if sizes else [(10, 10)]  # Default to 10x10 if no valid input

def test_experiments():
    game = maze_solver.MazeGame()
    with open(LOG_FILE, "w") as f:
        f.write("Test Results\n=================\n")

    # Experiment 1: Custom Maze Sizes
    sizes = get_custom_sizes()
    densities = [0.1]  # Default density for size experiment
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
    rows, cols = sizes[0]  # Use first custom size for density experiment
    print(f"\nExperiment 2: Varying Maze Density ({rows}x{cols})")
    for density in densities:
        avg_time, std_time, avg_iters, avg_path, avg_mem = run_experiment(game, rows, cols, density)
        density_results.append((density, avg_time, std_time, avg_iters, avg_path, avg_mem))
        print(f"Density {density:.2f}: Time={avg_time:.3f}s (σ={std_time:.3f}), "
              f"Iters={avg_iters:.0f}, Path={avg_path:.0f}, Mem={avg_mem:.0f} bytes")

    # Generate Graphs
    plot_size_graphs(size_results, sizes)
    plot_density_graphs(density_results, rows, cols)
    print(f"\nResults logged to {LOG_FILE}")

def plot_size_graphs(results, sizes):
    # Plot performance metrics vs. maze size
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
    # Plot performance metrics vs. density
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

if __name__ == "__main__":
    test_experiments()