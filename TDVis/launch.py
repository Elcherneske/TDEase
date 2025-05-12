from src import *

# Add missing imports at the top
import sys
import os
from streamlit.web import cli as stcli # <-- Add this import

def resolve_path(path):
    resolved_path = os.path.abspath(os.path.join(os.getcwd(), path))
    return resolved_path


if __name__ == "__main__":
    sys.argv = [
    "streamlit",
    "run",
    resolve_path("MainPage.py"),
    "--global.developmentMode=false",
    ]
    # Fix the execution call
    sys.exit(stcli.main())