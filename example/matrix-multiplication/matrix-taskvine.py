#!/usr/bin/env python3
"""
Parallel matrix multiplication with TaskVine, where the manager has *no* NumPy import.
 - The manager side uses standard Python 'random' and nested lists for matrix data.
 - Each multiplication is offloaded to a PythonTask that imports NumPy on the worker,
   multiplies (A_i x B_i), and returns the result as a list-of-lists.
"""

import random
import ndcctools.taskvine as vine

def multiply_pair(A, B):
    import numpy as np  # Only on the worker
    A_np = np.array(A, dtype=float)
    B_np = np.array(B, dtype=float)
    C_np = A_np @ B_np
    return C_np.tolist()  # convert back to nested list

def main():
    N = 50      # 50x50 matrices
    num_pairs = 10  # We'll do 10 pairs for demonstration

    A_list = []
    B_list = []
    
    for _ in range(num_pairs):
        A_mat = [[random.random() for _ in range(N)] for _ in range(N)]
        B_mat = [[random.random() for _ in range(N)] for _ in range(N)]
        A_list.append(A_mat)
        B_list.append(B_mat)

    m = vine.Manager([9123,9150], name="matrix")
    
    print(f"[manager] Listening on port {m.port}")

    tasks_map = {}
    results = [None]*num_pairs

    for i in range(num_pairs):
        task = vine.PythonTask(multiply_pair, A_list[i], B_list[i])
        t_id = m.submit(task)
        tasks_map[t_id] = i
        print(f"[manager] Submitted multiplication for pair index {i}.")

    print("[manager] Waiting for tasks to complete...")
    while not m.empty():
        done_task = m.wait(5)
        if done_task:
            idx = tasks_map[done_task.id]
            if done_task.successful():
                C = done_task.output
                results[idx] = C
                print(f"[manager] Pair {idx} -> result row0 length = {len(C[0])}")
            else:
                print(f"[manager] Task for pair {idx} failed: {done_task.result}")

    print("\n[manager] All tasks done.")

if __name__ == "__main__":
    main()

