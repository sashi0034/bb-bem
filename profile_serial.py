import csv
from datetime import datetime
import os
import subprocess
import re
import statistics
import matplotlib.pyplot as plt
import numpy as np

# Configuration parameters (easily adjustable)
input_path = "../input_data/torus-sd3x.stl"
output_tmp = "../output_data/tmp.out"
batch_sizes = [i for i in range(100, 1001, 100)]  # batch sizes to test
num_runs = 1  # number of repetitions per batch
parallel_cmd = "./bb_bem {input} -o {output} -m cuda_wmma --batch {batch}"
serial_cmd = "./bb_bem {input} -o {output} -m cuda --batch {batch}"
workdirs = {"parallel": "bb-bem2", "serial": "bb-bem2-serial"}

# Regular expression to extract compute time
time_pattern = re.compile(r"Compute time:\s*([\d.]+)")

# Storage for results
results = {"parallel": [], "serial": []}


# Function to run a command and extract compute time
def measure_time(command: str, cwd: str) -> float:
    print(f"Running in {cwd}: {command}")
    proc = subprocess.run(
        ["tssrun", "-p", "gr10561g", "--rsc", "p=1:t=64:c=64:m=500G"] + command.split(),
        cwd=cwd,
        capture_output=True,
        text=True,
        check=True,
    )
    print("---- Output ----")
    print(proc.stdout)
    print("----------------")
    match = time_pattern.search(proc.stdout)
    if not match:
        # raise RuntimeError(f"Compute time not found in output from {command}")
        print(f"Warning: Compute time not found in output from {command}")
        return float("nan")  # Return NaN if time not found
    return float(match.group(1))


# Perform measurements
for batch in batch_sizes:
    print(f"\n=== Measuring batch size: {batch} ===")
    for mode in ("parallel", "serial"):
        print(f"\n--- {mode.upper()} mode ---")
        cmd_template = parallel_cmd if mode == "parallel" else serial_cmd
        cwd = workdirs[mode]
        batch_times = []
        for run in range(num_runs):
            print(f"[Run {run+1}/{num_runs}]")
            cmd = cmd_template.format(input=input_path, output=output_tmp, batch=batch)
            elapsed = measure_time(cmd, cwd)
            print(f" -> Time: {elapsed:.6f} s")
            batch_times.append(elapsed)
        average_time = statistics.mean(batch_times)
        print(
            f"===> {mode.capitalize()} mode, batch={batch}: avg time={average_time:.6f}s"
        )
        results[mode].append(average_time)

# Plot results
plt.figure()
plt.plot(
    list(batch_sizes),
    results["parallel"],
    marker="o",
    label="Parallel (CUDA and Tensor Cores)",
)
plt.plot(list(batch_sizes), results["serial"], marker="s", label="Serial (CUDA)")
plt.xlabel("Batch Size")
plt.ylabel("Compute Time (s)")
plt.title("BiCGStab Performance Comparison: Parallel vs Serial")
plt.legend()
plt.grid(True)
plt.tight_layout()

# Save image with timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_dir = "output_image"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, f"profile_serial_{timestamp}.png")
plt.savefig(output_path)

print(f"Plot saved to {output_path}")

csv_output_path = os.path.join(output_dir, f"profile_serial_{timestamp}.csv")
with open(csv_output_path, mode="w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Batch Size", "Parallel Time (s)", "Serial Time (s)"])
    for batch, par_time, ser_time in zip(
        batch_sizes, results["parallel"], results["serial"]
    ):
        writer.writerow([batch, par_time, ser_time])

print(f"CSV saved to {csv_output_path}")
