import subprocess
import glob
import os
import sys

print("=== SomeWMULife Test Runner ===\n", flush=True)

# Find all .sml files in current directory
files = sorted(glob.glob("*.sml"))

if not files:
    print("No .sml files found in this directory.", flush=True)
    sys.exit(1)

for file in files:
    print("=" * 60, flush=True)
    print(f"Running test: {file}", flush=True)
    print("=" * 60, flush=True)

    try:
        result = subprocess.run(
            [sys.executable, "parser.py", file],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode != 0:
            print("❌ Runtime error:", flush=True)
            print(result.stderr.strip(), flush=True)
        else:
            output = result.stdout.strip()

            if "Type error" in output or "Syntax error" in output:
                print("❌ Program failed (expected for error tests):", flush=True)
                print(output, flush=True)
            else:
                print("✅ Program parsed successfully.", flush=True)
                print(output, flush=True)

    except subprocess.TimeoutExpired:
        print("❌ Test timed out", flush=True)

print("\n=== All tests completed ===", flush=True)
