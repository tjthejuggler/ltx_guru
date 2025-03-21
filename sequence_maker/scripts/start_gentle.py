#!/usr/bin/env python3
"""
Start Gentle Docker Container

This script starts the Gentle Docker container for lyrics alignment.
"""

import os
import subprocess
import sys
import time
import requests

def check_docker_installed():
    """Check if Docker is installed."""
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

def check_gentle_running():
    """Check if Gentle is already running."""
    try:
        response = requests.get("http://localhost:8765")
        return response.status_code == 200
    except requests.RequestException:
        return False

def start_gentle():
    """Start the Gentle Docker container."""
    # Get the path to the docker-compose.yml file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    docker_dir = os.path.join(os.path.dirname(script_dir), "gentle_docker")
    
    # Check if docker-compose.yml exists
    docker_compose_path = os.path.join(docker_dir, "docker-compose.yml")
    if not os.path.exists(docker_compose_path):
        print(f"Error: docker-compose.yml not found at {docker_compose_path}")
        return False
    
    # Start the container
    try:
        subprocess.run(
            ["docker-compose", "-f", docker_compose_path, "up", "-d"],
            check=True,
            cwd=docker_dir
        )
        
        # Wait for container to start
        print("Waiting for Gentle to start...")
        for _ in range(10):
            if check_gentle_running():
                print("Gentle is now running!")
                return True
            time.sleep(2)
        
        print("Timed out waiting for Gentle to start.")
        return False
    
    except subprocess.SubprocessError as e:
        print(f"Error starting Gentle: {e}")
        return False

def main():
    """Main function."""
    print("Sequence Maker - Starting Gentle Docker Container")
    print("===============================================")
    print()
    
    # Check if Docker is installed
    if not check_docker_installed():
        print("Error: Docker is not installed or not in PATH.")
        print("Please install Docker and try again.")
        sys.exit(1)
    
    # Check if Gentle is already running
    if check_gentle_running():
        print("Gentle is already running.")
        sys.exit(0)
    
    # Start Gentle
    if start_gentle():
        print("Gentle started successfully.")
        sys.exit(0)
    else:
        print("Failed to start Gentle.")
        sys.exit(1)

if __name__ == "__main__":
    main()