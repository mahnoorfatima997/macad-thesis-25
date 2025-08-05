"""Test PyVis path resolution"""

from pathlib import Path

# Test different possible paths
possible_paths = [
    Path("results/visualizations/pyvis"),
    Path("benchmarking/results/visualizations/pyvis"),
    Path(__file__).parent / "benchmarking/results/visualizations/pyvis",
    Path.cwd() / "results/visualizations/pyvis",
    Path.cwd() / "benchmarking/results/visualizations/pyvis",
]

print(f"Current working directory: {Path.cwd()}")
print(f"Script location: {Path(__file__).parent}")
print("\nChecking possible PyVis paths:")

for path in possible_paths:
    print(f"\n{path}")
    print(f"  Exists: {path.exists()}")
    if path.exists():
        html_files = list(path.glob("*.html"))
        print(f"  HTML files: {len(html_files)}")
        if html_files:
            print(f"  Files: {[f.name for f in html_files[:3]]}...")

# Check the actual path that exists
actual_path = Path("C:/Users/aponw/OneDrive/Escritorio/MaCAD Thesis/macad-thesis-25/benchmarking/results/visualizations/pyvis")
print(f"\nActual absolute path:")
print(f"{actual_path}")
print(f"  Exists: {actual_path.exists()}")
if actual_path.exists():
    html_files = list(actual_path.glob("*.html"))
    print(f"  HTML files: {len(html_files)}")
    print(f"  Files: {[f.name for f in html_files]}")