#!/usr/bin/env python3
"""
China Growth Game Server Launcher

This script ensures the economic model FastAPI server starts correctly
regardless of the current working directory.
"""
import os
import sys
import subprocess
import argparse

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Launch China Growth Game server')
    parser.add_argument('--port', type=int, default=8001, help='Port to run the server on')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Host to bind the server to')
    parser.add_argument('--reload', action='store_true', help='Enable auto-reload for development')
    parser.add_argument('--log-level', type=str, default='info', help='Logging level')
    args = parser.parse_args()

    # Get the directory containing this script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Path to the economic model app directory
    model_dir = os.path.join(os.path.dirname(script_dir), 'china_growth_game', 'economic_model', 'app')

    # Ensure the economic model app directory exists
    if not os.path.exists(model_dir):
        print(f"ERROR: Economic model app directory not found at {model_dir}", file=sys.stderr)
        return 1

    # Change to the economic model app directory
    os.chdir(model_dir)
    print(f"Working directory set to: {model_dir}")

    # Build command arguments
    cmd = [
        sys.executable, "-m", "uvicorn", "app:app",
        "--host", args.host,
        "--port", str(args.port),
        "--log-level", args.log_level
    ]

    if args.reload:
        cmd.append("--reload")

    # Print the command we're about to run
    print(f"Starting server with command: {' '.join(cmd)}")

    # Run the server
    try:
        subprocess.run(cmd)
        return 0
    except KeyboardInterrupt:
        print("\nServer stopped by user")
        return 0
    except Exception as e:
        print(f"ERROR: Failed to start server: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())