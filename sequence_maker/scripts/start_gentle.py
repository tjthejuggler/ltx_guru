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
import traceback
from datetime import datetime

# Configure logging to flush immediately
def log(message):
    """Log a message with timestamp and flush immediately."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] {message}", flush=True)

log("Script started")

def check_docker_installed():
    """Check if Docker is installed."""
    log("Checking if Docker is installed...")
    try:
        result = subprocess.run(["docker", "--version"], check=True, capture_output=True, text=True)
        log(f"Docker version: {result.stdout.strip()}")
        return True
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        log(f"Docker not installed or not in PATH: {e}")
        return False

def check_gentle_running():
    """Check if Gentle is already running."""
    try:
        log("Checking if Gentle is already running on port 8765...")
        response = requests.get("http://localhost:8765", timeout=5)
        log(f"Gentle is running. Response status: {response.status_code}")
        return response.status_code == 200
    except requests.RequestException as e:
        log(f"Gentle is not running: {e}")
        return False

def start_gentle():
    """Start the Gentle Docker container."""
    # Get the path to the docker-compose.yml file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    docker_dir = os.path.join(os.path.dirname(script_dir), "gentle_docker")
    
    log(f"Docker directory: {docker_dir}")
    
    # Check if docker-compose.yml exists
    docker_compose_path = os.path.join(docker_dir, "docker-compose.yml")
    if not os.path.exists(docker_compose_path):
        log(f"Error: docker-compose.yml not found at {docker_compose_path}")
        return False
    
    log(f"Found docker-compose.yml at: {docker_compose_path}")
    
    # Check if docker daemon is running
    try:
        log("Checking if Docker daemon is running...")
        docker_info = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if docker_info.returncode != 0:
            log(f"Docker daemon is not running. Error: {docker_info.stderr}")
            return False
        log("Docker daemon is running")
    except Exception as e:
        log(f"Error checking Docker daemon: {e}")
        log(traceback.format_exc())
        return False
    
    # Check if docker-compose is installed
    try:
        log("Checking if docker-compose is installed...")
        result = subprocess.run(
            ["docker-compose", "--version"],
            check=True,
            capture_output=True,
            text=True
        )
        log(f"docker-compose version: {result.stdout.strip()}")
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        log(f"docker-compose not installed or not in PATH: {e}")
        return False
    
    # Start the container
    try:
        log("Starting Gentle Docker container...")
        cmd = ["docker-compose", "-f", docker_compose_path, "up", "-d"]
        log(f"Running command: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            cwd=docker_dir
        )
        
        log(f"Command output: {result.stdout}")
        if result.stderr:
            log(f"Command error output: {result.stderr}")
        
        # Check if the container is actually running
        log("Checking if container is running with docker ps...")
        container_check = subprocess.run(
            ["docker", "ps", "--filter", "name=gentle", "--format", "{{.Names}}"],
            check=True,
            capture_output=True,
            text=True
        )
        
        if "gentle" in container_check.stdout:
            log("Gentle container is running according to docker ps")
        else:
            log("Warning: Gentle container not found in docker ps output")
            log(f"docker ps output: {container_check.stdout}")
            
            # Check all containers (including stopped ones)
            log("Checking all containers (including stopped ones)...")
            all_containers = subprocess.run(
                ["docker", "ps", "-a", "--filter", "name=gentle"],
                capture_output=True,
                text=True
            )
            log(f"All containers: {all_containers.stdout}")
        
        # Wait for container to start
        log("Waiting for Gentle API to become available...")
        max_attempts = 15  # Increase timeout to 30 seconds
        for attempt in range(max_attempts):
            log(f"Attempt {attempt+1}/{max_attempts} to connect to Gentle API...")
            if check_gentle_running():
                log("Gentle API is now running!")
                return True
            time.sleep(2)
        
        log("Timed out waiting for Gentle API to start.")
        
        # Check container logs to help diagnose the issue
        log("Checking Gentle container logs:")
        try:
            logs = subprocess.run(
                ["docker", "logs", "gentle_gentle_1"],
                capture_output=True,
                text=True
            )
            log(f"Container logs: {logs.stdout}")
            if logs.stderr:
                log(f"Container logs error: {logs.stderr}")
        except Exception as e:
            log(f"Error getting container logs: {e}")
            
        # Try alternative container name
        try:
            log("Trying alternative container name...")
            logs = subprocess.run(
                ["docker", "logs", "gentle-gentle-1"],
                capture_output=True,
                text=True
            )
            log(f"Container logs (alternative name): {logs.stdout}")
        except Exception as e:
            log(f"Error getting container logs with alternative name: {e}")
            
        return False
    
    except subprocess.SubprocessError as e:
        log(f"Error starting Gentle: {e}")
        log(traceback.format_exc())
        return False
    except Exception as e:
        log(f"Unexpected error starting Gentle: {e}")
        log(traceback.format_exc())
        return False

def main():
    """Main function."""
    log("Sequence Maker - Starting Gentle Docker Container")
    log("===============================================")
    
    # Print system information
    log(f"Python version: {sys.version}")
    log(f"Current working directory: {os.getcwd()}")
    log(f"Script location: {os.path.abspath(__file__)}")
    
    # Check environment variables
    log("Environment variables:")
    for key, value in os.environ.items():
        if key.startswith("DOCKER") or key.startswith("PATH"):
            log(f"  {key}={value}")
    
    # Check if Docker is installed
    if not check_docker_installed():
        log("Error: Docker is not installed or not in PATH.")
        log("Please install Docker and try again.")
        sys.exit(1)
    
    # Check if Docker daemon is running
    try:
        docker_info = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if docker_info.returncode != 0:
            log("Docker daemon is not running.")
            log(f"Docker info error: {docker_info.stderr}")
            sys.exit(1)
        else:
            log("Docker daemon is running.")
    except Exception as e:
        log(f"Error checking Docker daemon: {e}")
        log(traceback.format_exc())
        # Continue anyway, we'll try to start Gentle
    
    # Check if Gentle is already running
    try:
        if check_gentle_running():
            log("Gentle is already running.")
            sys.exit(0)
    except Exception as e:
        log(f"Error checking if Gentle is running: {e}")
        log(traceback.format_exc())
        # Continue anyway, we'll try to start it
    
    # Start Gentle
    log("Attempting to start Gentle...")
    try:
        if start_gentle():
            log("Gentle started successfully.")
            sys.exit(0)
        else:
            log("Failed to start Gentle.")
            sys.exit(1)
    except Exception as e:
        log(f"Unexpected error starting Gentle: {e}")
        log(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()