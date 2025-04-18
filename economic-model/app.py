"""
Wrapper for the canonical economic model API.
This file redirects to the canonical implementation in china-growth-game/economic-model/app.py.
"""
import sys
import os
import logging
import importlib.util
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Path to the canonical implementation
canonical_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             'china-growth-game', 'economic-model')

# Add the canonical path to sys.path if it's not already there
if canonical_path not in sys.path:
    sys.path.insert(0, canonical_path)
    logger.info(f"Added canonical path to sys.path: {canonical_path}")

# Import the app from the canonical implementation
try:
    # Check if the canonical implementation exists
    if not os.path.exists(os.path.join(canonical_path, 'app.py')):
        raise ImportError(f"Canonical implementation not found at {canonical_path}")

    # Import the app from the canonical implementation
    spec = importlib.util.spec_from_file_location("canonical_app",
                                                 os.path.join(canonical_path, 'app.py'))
    canonical_app = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(canonical_app)

    # Get the FastAPI app from the canonical implementation
    app = canonical_app.app
    logger.info("Successfully imported canonical implementation")
except Exception as e:
    logger.error(f"Error importing canonical implementation: {str(e)}")
    # Fallback to a minimal implementation
    from fastapi import FastAPI
    app = FastAPI(title="China's Growth Game Economic Model API (Fallback)")

    @app.get("/")
    def read_root():
        return {"message": "Fallback API - Canonical implementation not available"}

    @app.get("/health")
    def health_check():
        return {"status": "warning",
                "message": "Fallback API running - Canonical implementation not available",
                "error": str(e)}

# Add a main block to start the server when run directly
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting server on port {port}")
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)