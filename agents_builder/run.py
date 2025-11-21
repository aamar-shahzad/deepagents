#!/usr/bin/env python3
"""
Deep Agents Builder - Cross-platform Startup Script
"""

import os
import sys
import subprocess
import time
import signal
import socket
from pathlib import Path

def check_port(port):
    """Check if a port is in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def main():
    print("🧠🤖 Deep Agents Builder")
    print("=======================\n")
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Check Python version
    if sys.version_info < (3, 11):
        print("❌ Python 3.11 or higher is required")
        sys.exit(1)
    
    processes = []
    
    try:
        # Install dependencies
        print("📦 Checking backend dependencies...")
        backend_venv = script_dir / "backend" / "venv"
        
        if not backend_venv.exists():
            print("Creating virtual environment...")
            subprocess.run(
                [sys.executable, "-m", "venv", str(backend_venv)],
                check=True
            )
            
            # Determine pip path based on OS
            if sys.platform == "win32":
                pip_path = backend_venv / "Scripts" / "pip.exe"
                python_path = backend_venv / "Scripts" / "python.exe"
            else:
                pip_path = backend_venv / "bin" / "pip"
                python_path = backend_venv / "bin" / "python"
            
            print("Installing dependencies...")
            subprocess.run(
                [str(pip_path), "install", "-q", "-r", "backend/requirements.txt"],
                check=True
            )
            subprocess.run(
                [str(pip_path), "install", "-q", "../"],
                check=True,
                cwd=script_dir / "backend"
            )
        else:
            if sys.platform == "win32":
                python_path = backend_venv / "Scripts" / "python.exe"
            else:
                python_path = backend_venv / "bin" / "python"
        
        # Start backend
        if check_port(8000):
            print("⚠️  Port 8000 is already in use. Backend might already be running.")
        else:
            print("🚀 Starting backend server on http://localhost:8000")
            backend_process = subprocess.Popen(
                [str(python_path), "main.py"],
                cwd=script_dir / "backend"
            )
            processes.append(backend_process)
            time.sleep(2)
        
        # Start frontend
        if check_port(8080):
            print("⚠️  Port 8080 is already in use. Frontend might already be running.")
        else:
            print("🚀 Starting frontend server on http://localhost:8080")
            frontend_process = subprocess.Popen(
                [sys.executable, "-m", "http.server", "8080"],
                cwd=script_dir / "frontend"
            )
            processes.append(frontend_process)
            time.sleep(1)
        
        print("\n✅ Deep Agents Builder is running!\n")
        print("   Frontend: http://localhost:8080")
        print("   Backend API: http://localhost:8000")
        print("   API Docs: http://localhost:8000/docs\n")
        print("Press Ctrl+C to stop all servers\n")
        
        # Wait for interrupt
        while True:
            time.sleep(1)
            # Check if processes are still running
            for proc in processes:
                if proc.poll() is not None:
                    print("⚠️  A server process has stopped unexpectedly")
                    raise KeyboardInterrupt
    
    except KeyboardInterrupt:
        print("\n🛑 Stopping servers...")
        for proc in processes:
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
        print("✅ Servers stopped")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        for proc in processes:
            proc.kill()
        sys.exit(1)

if __name__ == "__main__":
    main()
