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
        result = subprocess.run(["docker", "--version"], check=True, capture_output=True, text=True)
        print(f"Docker version: {result.stdout.strip()}")
        return True
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        print(f"Docker not installed or not in PATH: {e}")
        return False

def check_gentle_running():
    """Check if Gentle is already running."""
    try:
        print("Checking if Gentle is already running on port 8765...")
        response = requests.get("http://localhost:8765", timeout=5)
        print(f"Gentle is running. Response status: {response.status_code}")
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"Gentle is not running: {e}")
        return False

def start_gentle():
    """Start the Gentle Docker container."""
    # Get the path to the docker-compose.yml file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    docker_dir = os.path.join(os.path.dirname(script_dir), "gentle_docker")
    
    print(f"Docker directory: {docker_dir}")
    
    # Check if docker-compose.yml exists
    docker_compose_path = os.path.join(docker_dir, "docker-compose.yml")
    if not os.path.exists(docker_compose_path):
        print(f"Error: docker-compose.yml not found at {docker_compose_path}")
        return False
    
    print(f"Found docker-compose.yml at: {docker_compose_path}")
    
    # Check if docker-compose is installed
    try:
        result = subprocess.run(
            ["docker-compose", "--version"],
            check=True,
            capture_output=True,
            text=True
        )
        print(f"docker-compose version: {result.stdout.strip()}")
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        print(f"docker-compose not installed or not in PATH: {e}")
        return False
    
    # Start the container
    try:
        print("Starting Gentle Docker container...")
        cmd = ["docker-compose", "-f", docker_compose_path, "up", "-d"]
        print(f"Running command: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            cwd=docker_dir
        )
        
        print(f"Command output: {result.stdout}")
        if result.stderr:
            print(f"Command error output: {result.stderr}")
        
        # Check if the container is actually running
        container_check = subprocess.run(
            ["docker", "ps", "--filter", "name=gentle", "--format", "{{.Names}}"],
            check=True,
            capture_output=True,
            text=True
        )
        
        if "gentle" in container_check.stdout:
            print("Gentle container is running according to docker ps")
        else:
            print("Warning: Gentle container not found in docker ps output")
            print(f"docker ps output: {container_check.stdout}")
        
        # Wait for container to start
        print("Waiting for Gentle API to become available...")
        max_attempts = 15  # Increase timeout to 30 seconds
        for attempt in range(max_attempts):
            print(f"Attempt {attempt+1}/{max_attempts} to connect to Gentle API...")
            if check_gentle_running():
                print("Gentle API is now running!")
                return True
            time.sleep(2)
        
        print("Timed out waiting for Gentle API to start.")
        
        # Check container logs to help diagnose the issue
        print("Checking Gentle container logs:")
        logs = subprocess.run(
            ["docker", "logs", "gentle_gentle_1"],
            capture_output=True,
            text=True
        )
        print(f"Container logs: {logs.stdout}")
        if logs.stderr:
            print(f"Container logs error: {logs.stderr}")
            
        return False
    
    except subprocess.SubprocessError as e:
        print(f"Error starting Gentle: {e}")
        return False

def main():
    """Main function."""
    print("Sequence Maker - Starting Gentle Docker Container")
    print("===============================================")
    print()
    
    # Print system information
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Script location: {os.path.abspath(__file__)}")
    
    # Check if Docker is installed
    print("Checking if Docker is installed...")
    if not check_docker_installed():
        print("Error: Docker is not installed or not in PATH.")
        print("Please install Docker and try again.")
        sys.exit(1)
    
    # Check if Docker daemon is running
    try:
        print("Checking if Docker daemon is running...")
        docker_info = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if docker_info.returncode != 0:
            print("Docker daemon is not running.")
            print(f"Docker info error: {docker_info.stderr}")
            sys.exit(1)
        else:
            print("Docker daemon is running.")
    except Exception as e:
        print(f"Error checking Docker daemon: {e}")
        # Continue anyway, we'll try to start Gentle
    
    # Check if Gentle is already running
    print("Checking if Gentle is already running...")
    try:
        if check_gentle_running():
            print("Gentle is already running.")
            sys.exit(0)
    except Exception as e:
        print(f"Error checking if Gentle is running: {e}")
        # Continue anyway, we'll try to start it
    
    # Start Gentle
    print("Attempting to start Gentle...")
    try:
        if start_gentle():
            print("Gentle started successfully.")
            sys.exit(0)
        else:
            print("Failed to start Gentle.")
            sys.exit(1)
    except Exception as e:
        print(f"Unexpected error starting Gentle: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()