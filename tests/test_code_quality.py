import subprocess
import sys


def test_black_formatting():
    """Check that the code is formatted with black."""
    try:
        subprocess.run([sys.executable, "-m", "black", "--check", "."], check=True)
    except subprocess.CalledProcessError:
        assert False, "Code is not formatted with black. Run 'black .' to fix."


def test_isort_formatting():
    """Check that imports are sorted with isort."""
    try:
        subprocess.run([sys.executable, "-m", "isort", "--check", "."], check=True)
    except subprocess.CalledProcessError:
        assert False, "Imports are not sorted with isort. Run 'isort .' to fix."
