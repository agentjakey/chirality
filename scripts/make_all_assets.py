"""
Run all demo, sweep, video, and summary scripts in sequence.

Expected total runtime: 30-50 minutes on a modern laptop.

Run from repo root: python scripts/make_all_assets.py
"""
import sys
import os
import subprocess
import time

scripts = [
    "scripts/run_particle_demo.py",
    "scripts/run_pattern_demo.py",
    "scripts/run_phase_sweeps.py",
    "scripts/make_video.py",
    "scripts/make_summary_panels.py",
]


def run_script(path):
    print(f"\n{'='*60}")
    print(f"Running: {path}")
    print(f"{'='*60}")
    t0 = time.time()
    result = subprocess.run([sys.executable, path], capture_output=False)
    elapsed = time.time() - t0
    status = "OK" if result.returncode == 0 else f"FAILED (exit {result.returncode})"
    print(f"\n  {status} in {elapsed:.1f}s")
    return result.returncode == 0


print("=== Chirality Atlas: Generate All Assets ===")
print()
print("Scripts to run:")
for s in scripts:
    print(f"  {s}")
print()

failures = []
for script in scripts:
    ok = run_script(script)
    if not ok:
        failures.append(script)

print()
print("=== Summary ===")
if failures:
    print(f"FAILED scripts ({len(failures)}):")
    for f in failures:
        print(f"  {f}")
    sys.exit(1)
else:
    print("All scripts completed successfully.")
    print()
    print("Output directories:")
    print("  outputs/demo/           -- 10 particle and pattern figures")
    print("  outputs/phase_sweeps/   -- 7 phase diagrams + sanity_check.txt")
    print("  outputs/videos/         -- 4 GIF animations")
    print("  outputs/summary/        -- 4 presentation-ready panels")
    print("  outputs/data/           -- 3 CSV data files")
