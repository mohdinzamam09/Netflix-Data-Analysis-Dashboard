"""Run the whole project:  python run_all.py
Steps 1-4 prepare the data; then the Flask backend starts and the dashboard opens in your browser."""
import subprocess, sys, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
for s in ["01_clean_data", "02_run_sql", "03_visualizations", "04_excel_workbook"]:
    print(f"\n=== Running {s}.py ===")
    if subprocess.run([sys.executable, f"scripts/{s}.py"]).returncode:
        sys.exit(f"Failed at {s}.py")
print("\n=== Starting backend server ===")
subprocess.run([sys.executable, "backend/app.py"])
