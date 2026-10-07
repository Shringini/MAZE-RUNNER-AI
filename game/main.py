"""
Root entry point redirecting to MazeRunner/main.py
Enables running `python main.py` directly from workspace root.
"""
import os
import runpy

if __name__ == "__main__":
    runner_path = os.path.join(os.path.dirname(__file__), "MazeRunner", "main.py")
    runpy.run_path(runner_path, run_name="__main__")
