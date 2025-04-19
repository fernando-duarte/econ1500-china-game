"""
Standardized error handling for the China Growth Game.

This module provides utilities for consistent error handling across
the application, including custom exceptions, error logging, and
error response formatting.
"""

import logging
import traceback
import sys
from typing import Dict, Any, Optional, List, Union
from enum import Enum
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ErrorCode(Enum):
    """Standardized error codes for the application."""
    # General errors
    UNKNOWN_ERROR = 1000
    VALIDATION_ERROR = 1001
    RESOURCE_NOT_FOUND = 1002
    PERMISSION_DENIED = 1003
    
    # Game state errors
    GAME_NOT_STARTED = 2000
    GAME_ALREADY_STARTED = 2001
    GAME_ENDED = 2002
    ROUND_ALREADY_PROCESSED = 2003
    
    # Team errors
    TEAM_NOT_FOUND = 3000
    TEAM_NAME_TAKEN = 3001
    INVALID_TEAM_NAME = 3002
    
    # Decision errors
    DECISION_ALREADY_SUBMITTED = 4000
    INVALID_DECISION = 4001
    DECISION_DEADLINE_PASSED = 4002
    
    # Persistence errors
    PERSISTENCE_ERROR = 5000
    SAVE_FAILED = 5001
    LOAD_FAILED = 5002
    
    # Event errors
    EVENT_ERROR = 6000
    EVENT_ALREADY_TRIGGERED = 6001
    
    # Prize errors
    PRIZE_ERROR = 7000
    PRIZE_ALREADY_AWARDED = 7001
    
    # Model errors
    MODEL_ERROR = 8000
    CALCULATION_ERROR = 8001
    PARAMETER_ERROR = 8002
    
    # API errors
    API_ERROR = 9000
    RATE_LIMIT_EXCEEDED = 9001
    INVALID_REQUEST = 9002

class GameError(Exception):
    """Base exception class for all game-related errors."""
    
    def __init__(
        self, 
        message: str, 
        error_code: ErrorCode = ErrorCode.UNKNOWN_ERROR,
        details: Optional[Dict[str, Any]] = None,
        http_status_code: int = 500
    ):
        """
        Initialize a GameError.
        
        Args:
            message: Human-readable error message.
            error_code: Standardized error code.
            details: Additional error details.
            http_status_code: HTTP status code to return for this error.
        """
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.http_status_code = http_status_code
        super().__init__(self.message)
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the error to a dictionary for API responses.
        
        Returns:
            Dictionary representation of the error.
        """
        return {
            "error": True,
            "code": self.error_code.value,
            "message": self.message,
            "details": self.details
        }
        
    def log(self, include_traceback: bool = True) -> None:
        """
        Log the error with appropriate severity.
        
        Args:
            include_traceback: Whether to include the traceback in the log.
        """
        error_info = f"Error {self.error_code.name} ({self.error_code.value}): {self.message}"
        
        if self.details:
            try:
                details_str = json.dumps(self.details)
                error_info += f" - Details: {details_str}"
            except (TypeError, ValueError):
                error_info += f" - Details: {str(self.details)}"
                
        if include_traceback:
            logger.error(error_info, exc_info=True)
        else:
            logger.error(error_info)

# Game state errors
class GameNotStartedError(GameError):
    """Raised when an operation requires the game to be started."""
    
    def __init__(self, message: str = "Game has not been started", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.GAME_NOT_STARTED,
            details=details,
            http_status_code=400
        )

class GameAlreadyStartedError(GameError):
    """Raised when trying to start an already started game."""
    
    def __init__(self, message: str = "Game has already been started", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.GAME_ALREADY_STARTED,
            details=details,
            http_status_code=400
        )

class GameEndedError(GameError):
    """Raised when trying to perform operations on an ended game."""
    
    def __init__(self, message: str = "Game has ended", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.GAME_ENDED,
            details=details,
            http_status_code=400
        )

class RoundAlreadyProcessedError(GameError):
    """Raised when trying to process a round that has already been processed."""
    
    def __init__(self, message: str = "Round has already been processed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.ROUND_ALREADY_PROCESSED,
            details=details,
            http_status_code=400
        )

# Team errors
class TeamNotFoundError(GameError):
    """Raised when a team cannot be found."""
    
    def __init__(self, team_id: str, message: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        if message is None:
            message = f"Team with ID {team_id} not found"
            
        if details is None:
            details = {"team_id": team_id}
            
        super().__init__(
            message=message,
            error_code=ErrorCode.TEAM_NOT_FOUND,
            details=details,
            http_status_code=404
        )

class TeamNameTakenError(GameError):
    """Raised when trying to create a team with a name that is already taken."""
    
    def __init__(self, team_name: str, message: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        if message is None:
            message = f"Team name '{team_name}' is already taken"
            
        if details is None:
            details = {"team_name": team_name}
            
        super().__init__(
            message=message,
            error_code=ErrorCode.TEAM_NAME_TAKEN,
            details=details,
            http_status_code=400
        )

class InvalidTeamNameError(GameError):
    """Raised when a team name is invalid."""
    
    def __init__(self, team_name: str, message: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        if message is None:
            message = f"Team name '{team_name}' is invalid"
            
        if details is None:
            details = {"team_name": team_name}
            
        super().__init__(
            message=message,
            error_code=ErrorCode.INVALID_TEAM_NAME,
            details=details,
            http_status_code=400
        )

# Decision errors
class DecisionAlreadySubmittedError(GameError):
    """Raised when a team tries to submit a decision that has already been submitted."""
    
    def __init__(self, team_id: str, round_num: int, message: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        if message is None:
            message = f"Team {team_id} has already submitted a decision for round {round_num}"
            
        if details is None:
            details = {"team_id": team_id, "round": round_num}
            
        super().__init__(
            message=message,
            error_code=ErrorCode.DECISION_ALREADY_SUBMITTED,
            details=details,
            http_status_code=400
        )

class InvalidDecisionError(GameError):
    """Raised when a team submits an invalid decision."""
    
    def __init__(self, team_id: str, message: str, details: Optional[Dict[str, Any]] = None):
        if details is None:
            details = {"team_id": team_id}
            
        super().__init__(
            message=message,
            error_code=ErrorCode.INVALID_DECISION,
            details=details,
            http_status_code=400
        )

# Persistence errors
class PersistenceError(GameError):
    """Base class for persistence-related errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.PERSISTENCE_ERROR,
            details=details,
            http_status_code=500
        )

class SaveFailedError(PersistenceError):
    """Raised when saving data fails."""
    
    def __init__(self, message: str = "Failed to save data", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            details=details
        )
        self.error_code = ErrorCode.SAVE_FAILED

class LoadFailedError(PersistenceError):
    """Raised when loading data fails."""
    
    def __init__(self, message: str = "Failed to load data", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            details=details
        )
        self.error_code = ErrorCode.LOAD_FAILED

# Model errors
class ModelError(GameError):
    """Base class for economic model-related errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.MODEL_ERROR,
            details=details,
            http_status_code=500
        )

class CalculationError(ModelError):
    """Raised when a calculation in the economic model fails."""
    
    def __init__(self, message: str = "Calculation error in economic model", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            details=details
        )
        self.error_code = ErrorCode.CALCULATION_ERROR

class ParameterError(ModelError):
    """Raised when invalid parameters are provided to the economic model."""
    
    def __init__(self, message: str = "Invalid parameters for economic model", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            details=details
        )
        self.error_code = ErrorCode.PARAMETER_ERROR
        self.http_status_code = 400  # This is a client error, not a server error

def handle_exception(e: Exception) -> Dict[str, Any]:
    """
    Handle an exception and return a standardized error response.
    
    Args:
        e: The exception to handle.
        
    Returns:
        Standardized error response dictionary.
    """
    # If it's already a GameError, use its built-in formatting
    if isinstance(e, GameError):
        e.log()
        return e.to_dict()
        
    # Otherwise, convert to a GameError
    error_message = str(e)
    error_code = ErrorCode.UNKNOWN_ERROR
    http_status_code = 500
    
    # Map common exceptions to appropriate error codes
    if isinstance(e, ValueError):
        error_code = ErrorCode.VALIDATION_ERROR
        http_status_code = 400
    elif isinstance(e, KeyError) or isinstance(e, IndexError):
        error_code = ErrorCode.RESOURCE_NOT_FOUND
        http_status_code = 404
    elif isinstance(e, PermissionError):
        error_code = ErrorCode.PERMISSION_DENIED
        http_status_code = 403
        
    # Create a GameError and log it
    game_error = GameError(
        message=error_message,
        error_code=error_code,
        details={"exception_type": e.__class__.__name__},
        http_status_code=http_status_code
    )
    game_error.log()
    
    return game_error.to_dict()

def log_error(
    message: str, 
    error_code: ErrorCode = ErrorCode.UNKNOWN_ERROR,
    details: Optional[Dict[str, Any]] = None,
    include_traceback: bool = True
) -> None:
    """
    Log an error with standardized formatting.
    
    Args:
        message: Error message.
        error_code: Error code.
        details: Additional error details.
        include_traceback: Whether to include the traceback in the log.
    """
    error = GameError(message=message, error_code=error_code, details=details)
    error.log(include_traceback=include_traceback)

def format_validation_errors(errors: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Format validation errors from Pydantic or other validation libraries.
    
    Args:
        errors: List of validation errors.
        
    Returns:
        Standardized error response dictionary.
    """
    return {
        "error": True,
        "code": ErrorCode.VALIDATION_ERROR.value,
        "message": "Validation error",
        "details": {
            "validation_errors": errors
        }
    }
