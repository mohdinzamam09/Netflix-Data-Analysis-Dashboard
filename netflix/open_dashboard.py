"""Start only the backend + dashboard (data must already be prepared):  python open_dashboard.py"""
import subprocess, sys, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
if not os.path.exists("data/netflix.db"): subprocess.run([sys.executable, "scripts/01_clean_data.py"], check=True)
subprocess.run([sys.executable, "backend/app.py"])
