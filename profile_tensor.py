import csv
from datetime import datetime
import os
import subprocess
import re
import statistics
import matplotlib.pyplot as plt
import numpy as np  # kept for parity with the original script

# =========================
# Configuration (constants)
# =========================
# NOTE: Change only these constants to customize behavior/labels, without touching core logic.

# I/O and experiment setup
INPUT_PATH = "../input_data/torus-sd3x.stl"
OUTPUT_TMP = "../output_data/tmp.out"
BATCH_SIZES = [i for i in range(100, 1001, 100)]
NUM_RUNS = 1  # number of repetitions per batch

# Modes and their order (affects CSV column order and plotting order)
MODES = ("standard", "tensor")

# Per-mode working directory
WORKDIRS = {
    "standard": "bb-bem2-no-tcl",
    "tensor": "bb-bem2-no-tcl",
}

# Per-mode command templates (placeholders: {input}, {output}, {batch})
CMD_TEMPLATES = {
    "standard": "./bb_bem {input} -o {output} -m cuda --batch {batch}",
    "tensor": "./bb_bem {input} -o {output} -m cuda_wmma --batch {batch}",
}

# Plot labels and markers (must match original if you need identical figure legend)
PLOT_LABELS = {
    "standard": "No Tensor Cores",
    "tensor": "Tensor Cores",
}
PLOT_MARKERS = {
    "standard": "o",
    "tensor": "s",
}

# CSV headers (must match original exactly to keep output identical)
CSV_HEADERS = {
    "standard": "standard Time (s)",
    "tensor": "tensor cores Time (s)",
}

# Runner prefix (leave [] for local execution; original uses tssrun)
RUNNER_PREFIX = ["tssrun", "-p", "gr10561g", "--rsc", "p=1:t=64:c=64:m=500G"]

# Regex pattern to extract compute time
TIME_PATTERN = re.compile(r"Compute time:\s*([\d.]+)")

# Plot text (kept identical to original)
PLOT_TITLE = "BiCGStab with Tensor Cores"
XLABEL = "Batch Size"
YLABEL = "Compute Time (s)"

# Output files (kept identical to original)
OUTPUT_DIR = "output_image"
FILE_PREFIX = "profile_tensor_"  # keep this to preserve exact filenames

# =========================
# Results storage
# =========================
results = {mode: [] for mode in MODES}

# =========================
# Optional sanity checks (no change in outputs; fails fast if misconfigured)
# =========================
for m in MODES:
    if not (
        m in WORKDIRS
        and m in CMD_TEMPLATES
        and m in PLOT_LABELS
        and m in PLOT_MARKERS
        and m in CSV_HEADERS
    ):
        raise KeyError(f"Missing config for mode '{m}'")


# =========================
# Core functions
# =========================
def measure_time(command: str, cwd: str) -> float:
    """Run a command under the given working directory and extract compute time."""
    print(f"Running in {cwd}: {command}")
    proc = subprocess.run(
        RUNNER_PREFIX + command.split(),
        cwd=cwd,
        capture_output=True,
        text=True,
        check=True,
    )
    print("---- Output ----")
    print(proc.stdout)
    print("----------------")
    match = TIME_PATTERN.search(proc.stdout)
    if not match:
        # Preserve original behavior: warn and return NaN if pattern missing
        print(f"Warning: Compute time not found in output from {command}")
        return float("nan")
    return float(match.group(1))


# =========================
# Measurements
# =========================
for batch in BATCH_SIZES:
    print(f"\n=== Measuring batch size: {batch} ===")
    for mode in MODES:
        print(f"\n--- {mode.upper()} mode ---")
        batch_times = []
        cmd_template = CMD_TEMPLATES[mode]
        cwd = WORKDIRS[mode]
        for run in range(NUM_RUNS):
            print(f"[Run {run+1}/{NUM_RUNS}]")
            cmd = cmd_template.format(input=INPUT_PATH, output=OUTPUT_TMP, batch=batch)
            elapsed = measure_time(cmd, cwd)
            print(f" -> Time: {elapsed:.6f} s")
            batch_times.append(elapsed)
        average_time = statistics.mean(batch_times)
        # Keep exact print message
        print(
            f"===> {mode.capitalize()} mode, batch={batch}: avg time={average_time:.6f}s"
        )
        results[mode].append(average_time)

# =========================
# Plot (identical aesthetics and labels; order follows MODES)
# =========================
plt.figure()
for mode in MODES:
    plt.plot(
        list(BATCH_SIZES),
        results[mode],
        marker=PLOT_MARKERS[mode],
        label=PLOT_LABELS[mode],
    )
plt.xlabel(XLABEL)
plt.ylabel(YLABEL)
plt.title(PLOT_TITLE)
plt.legend()
plt.grid(True)
plt.tight_layout()

# Save image with timestamp (same naming as original)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
os.makedirs(OUTPUT_DIR, exist_ok=True)
png_path = os.path.join(OUTPUT_DIR, f"{FILE_PREFIX}{timestamp}.png")
plt.savefig(png_path)
print(f"Plot saved to {png_path}")

# =========================
# CSV (identical header and row order)
# =========================
csv_output_path = os.path.join(OUTPUT_DIR, f"{FILE_PREFIX}{timestamp}.csv")
with open(csv_output_path, mode="w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    # Exact header order: "Batch Size", then modes in MODES order
    writer.writerow(["Batch Size"] + [CSV_HEADERS[m] for m in MODES])
    # Rows follow the batch order and per-mode series order
    for idx, batch in enumerate(BATCH_SIZES):
        row = [batch] + [results[m][idx] for m in MODES]
        writer.writerow(row)

print(f"CSV saved to {csv_output_path}")
