
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

from src.main import app
from fastapi.routing import APIRoute

def print_routes():
    print("Registered Routes:")
    for route in app.routes:
        if isinstance(route, APIRoute):
            methods = ", ".join(route.methods)
            print(f"{methods} {route.path}")

if __name__ == "__main__":
    print_routes()
