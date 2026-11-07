"""
app.py
Root entry-point for Streamlit Cloud and local dashboard execution.
Project: E-commerce clickstream analytics: A big-data clickstream processing pipeline Based Solution
Student: KOTAMSETTI MANOJ SRI HARSHA (23ME1A5433)
Guide: Mr. S.V. Swamy
"""

import os
import sys
import runpy

# Ensure root directory is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Path to the complete Marketing-Conversion Dashboard
DASHBOARD_PATH = os.path.join(BASE_DIR, "app", "dashboard.py")

if __name__ == "__main__" or "streamlit" in sys.modules:
    runpy.run_path(DASHBOARD_PATH, run_name="__main__")
