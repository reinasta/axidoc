from pathlib import Path
import argparse
import runpy
import sys
import pytest  # Import pytest
import subprocess


def run_script(script_path):
    full_path = Path.cwd() / script_path
    if not full_path.exists():
        print(f"Script not found: {full_path}")
        sys.exit(1)
    
    # Check if the script is a test script
    if "tests/" in script_path:
        pytest.main([str(full_path)])
    else:
        # Add src directory to PYTHONPATH
        sys.path.append(str(Path(__file__).parent / 'src'))
        runpy.run_path(str(full_path), run_name='__main__')
        #subprocess.run([sys.executable, str(full_path)], check=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run Python scripts in the project.')
    parser.add_argument('script', type=str, help='Path to the Python script relative to the project root.')
    
    args = parser.parse_args()

    run_script(args.script)

