"""
Error handling middleware for FastAPI.

This module provides middleware for consistent error handling in FastAPI.
"""

import logging
import traceback
import json
from typing import Callable, Dict, Any

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from economic_model_py.economic_model.utils.error_handling import (
    GameError, 
    ErrorCode, 
    handle_exception,
    format_validation_errors
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for handling errors in FastAPI."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process a request and handle any errors.
        
        Args:
            request: The incoming request.
            call_next: The next middleware or route handler.
            
        Returns:
            The response.
        """
        try:
            # Process the request
            return await call_next(request)
        except Exception as e:
            # Handle the exception
            error_response = handle_exception(e)
            
            # Determine the status code
            status_code = 500
            if isinstance(e, GameError):
                status_code = e.http_status_code
            elif isinstance(e, HTTPException):
                status_code = e.status_code
                
            # Return a JSON response with the error
            return JSONResponse(
                status_code=status_code,
                content=error_response
            )

def add_error_handlers(app: FastAPI) -> None:
    """
    Add error handlers to a FastAPI application.
    
    Args:
        app: The FastAPI application.
    """
    # Add middleware for handling uncaught exceptions
    app.add_middleware(ErrorHandlingMiddleware)
    
    # Handle validation errors
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """
        Handle validation errors from FastAPI.
        
        Args:
            request: The incoming request.
            exc: The validation exception.
            
        Returns:
            JSON response with validation errors.
        """
        # Log the error
        logger.error(f"Validation error: {exc.errors()}")
        
        # Format the validation errors
        error_response = format_validation_errors(exc.errors())
        
        # Return a JSON response
        return JSONResponse(
            status_code=400,
            content=error_response
        )
    
    # Handle HTTP exceptions
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        """
        Handle HTTP exceptions from FastAPI.
        
        Args:
            request: The incoming request.
            exc: The HTTP exception.
            
        Returns:
            JSON response with error details.
        """
        # Log the error
        logger.error(f"HTTP error {exc.status_code}: {exc.detail}")
        
        # Create an error response
        error_response = {
            "error": True,
            "code": exc.status_code,
            "message": str(exc.detail)
        }
        
        # Return a JSON response
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response
        )
    
    # Handle GameErrors
    @app.exception_handler(GameError)
    async def game_error_handler(request: Request, exc: GameError) -> JSONResponse:
        """
        Handle GameErrors.
        
        Args:
            request: The incoming request.
            exc: The GameError.
            
        Returns:
            JSON response with error details.
        """
        # Log the error
        exc.log()
        
        # Return a JSON response
        return JSONResponse(
            status_code=exc.http_status_code,
            content=exc.to_dict()
        )
