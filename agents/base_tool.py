"""
Base Tool Classes for Cosmetic SEO Project

This module provides base classes for all tools in the system,
implementing common functionality for error handling, validation,
and result formatting.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
import logging
from functools import wraps

logger = logging.getLogger(__name__)


def tool_error_handler(func):
    """Decorator for consistent error handling across all tool methods."""
    @wraps(func)
    async def async_wrapper(self, *args, **kwargs):
        try:
            # Log tool execution start
            self.logger.info(f"Executing {self.__class__.__name__} with args: {args[:2] if args else 'None'}")
            
            start_time = datetime.utcnow()
            result = await func(self, *args, **kwargs)
            end_time = datetime.utcnow()
            
            # Add execution metadata to successful results
            if isinstance(result, dict):
                result["execution_metadata"] = {
                    "tool_name": self.__class__.__name__,
                    "execution_time": (end_time - start_time).total_seconds(),
                    "timestamp": end_time.isoformat(),
                    "success": result.get("success", True)
                }
            
            return result
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "tool_name": self.__class__.__name__,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.logger.error(
                f"[{self.__class__.__name__}] Error in {func.__name__}: {str(e)}", 
                exc_info=True
            )
            
            return error_result
    
    @wraps(func)
    def sync_wrapper(self, *args, **kwargs):
        try:
            # Log tool execution start
            self.logger.info(f"Executing {self.__class__.__name__} with args: {args[:2] if args else 'None'}")
            
            start_time = datetime.utcnow()
            result = func(self, *args, **kwargs)
            end_time = datetime.utcnow()
            
            # Add execution metadata to successful results
            if isinstance(result, dict):
                result["execution_metadata"] = {
                    "tool_name": self.__class__.__name__,
                    "execution_time": (end_time - start_time).total_seconds(),
                    "timestamp": end_time.isoformat(),
                    "success": result.get("success", True)
                }
            
            return result
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "tool_name": self.__class__.__name__,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.logger.error(
                f"[{self.__class__.__name__}] Error in {func.__name__}: {str(e)}", 
                exc_info=True
            )
            
            return error_result
    
    # Return appropriate wrapper based on function type
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


class BaseTool(ABC):
    """Base class for all tools in the cosmetic SEO system."""
    
    def __init__(self, name: Optional[str] = None):
        self.name = name or self.__class__.__name__
        self.logger = logging.getLogger(f"{__name__}.{self.name}")
        self._setup_logging()
    
    def _setup_logging(self):
        """Configure logging for the tool."""
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                f'%(asctime)s - [{self.name}] - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """
        Get the tool schema for ADK registration.
        Must be implemented by subclasses.
        
        Returns:
            Dict containing tool schema with parameters and description
        """
        pass
    
    @abstractmethod
    async def validate_input(self, **kwargs) -> Dict[str, Any]:
        """
        Validate input parameters.
        Must be implemented by subclasses.
        
        Returns:
            Dict with keys:
            - is_valid: bool
            - error: Optional[str]
            - details: Optional[List[str]]
        """
        pass
    
    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the tool's main functionality.
        Must be implemented by subclasses.
        """
        pass
    
    @tool_error_handler
    async def __call__(self, **kwargs) -> Dict[str, Any]:
        """
        Main entry point for tool execution.
        Validates input and delegates to execute method.
        """
        # Input validation
        validation_result = await self.validate_input(**kwargs)
        if not validation_result["is_valid"]:
            return {
                "success": False,
                "error": validation_result["error"],
                "validation_errors": validation_result.get("details", [])
            }
        
        # Execute the tool
        result = await self.execute(**kwargs)
        
        # Ensure result has success field
        if isinstance(result, dict) and "success" not in result:
            result["success"] = True
        
        return result
    
    def format_success_result(self, data: Any, message: Optional[str] = None) -> Dict[str, Any]:
        """Format a successful result."""
        result = {
            "success": True,
            "data": data
        }
        
        if message:
            result["message"] = message
        
        return result
    
    def format_error_result(self, error: str, details: Optional[List[str]] = None) -> Dict[str, Any]:
        """Format an error result."""
        result = {
            "success": False,
            "error": error
        }
        
        if details:
            result["details"] = details
        
        return result


class BaseDataValidationTool(BaseTool):
    """Base class for data validation tools."""
    
    def __init__(self, required_fields: Optional[List[str]] = None, **kwargs):
        super().__init__(**kwargs)
        self.required_fields = required_fields or []
    
    async def validate_input(self, data: Any = None, **kwargs) -> Dict[str, Any]:
        """Validate input data has required structure."""
        errors = []
        
        if data is None:
            errors.append("Data parameter is required")
        elif not isinstance(data, dict):
            errors.append("Data must be a dictionary")
        else:
            # Check required fields
            for field in self.required_fields:
                if field not in data:
                    errors.append(f"Required field '{field}' is missing")
        
        return {
            "is_valid": len(errors) == 0,
            "error": "; ".join(errors) if errors else None,
            "details": errors
        }
    
    @abstractmethod
    async def validate_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the data content. Must be implemented by subclasses."""
        pass
    
    async def execute(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Execute data validation."""
        return await self.validate_data(data)


class BaseAnalysisTool(BaseTool):
    """Base class for data analysis tools."""
    
    def __init__(self, supported_languages: Optional[List[str]] = None, **kwargs):
        super().__init__(**kwargs)
        self.supported_languages = supported_languages or ["tr", "en"]
    
    async def validate_input(self, text: str = None, **kwargs) -> Dict[str, Any]:
        """Validate input text."""
        errors = []
        
        if not text:
            errors.append("Text parameter is required")
        elif not isinstance(text, str):
            errors.append("Text must be a string")
        elif len(text.strip()) == 0:
            errors.append("Text cannot be empty")
        
        return {
            "is_valid": len(errors) == 0,
            "error": "; ".join(errors) if errors else None,
            "details": errors
        }
    
    @abstractmethod
    async def analyze_text(self, text: str, **kwargs) -> Dict[str, Any]:
        """Analyze text content. Must be implemented by subclasses."""
        pass
    
    async def execute(self, text: str, **kwargs) -> Dict[str, Any]:
        """Execute text analysis."""
        return await self.analyze_text(text, **kwargs)


class BaseScrapingTool(BaseTool):
    """Base class for web scraping tools."""
    
    def __init__(self, max_retries: int = 3, timeout: int = 30, **kwargs):
        super().__init__(**kwargs)
        self.max_retries = max_retries
        self.timeout = timeout
    
    async def validate_input(self, url: str = None, **kwargs) -> Dict[str, Any]:
        """Validate scraping input."""
        errors = []
        
        if not url:
            errors.append("URL parameter is required")
        elif not isinstance(url, str):
            errors.append("URL must be a string")
        else:
            # Basic URL validation
            from urllib.parse import urlparse
            try:
                result = urlparse(url)
                if not all([result.scheme, result.netloc]):
                    errors.append("Invalid URL format")
            except Exception:
                errors.append("Invalid URL format")
        
        return {
            "is_valid": len(errors) == 0,
            "error": "; ".join(errors) if errors else None,
            "details": errors
        }
    
    @abstractmethod
    async def scrape_data(self, url: str, **kwargs) -> Dict[str, Any]:
        """Scrape data from URL. Must be implemented by subclasses."""
        pass
    
    async def execute(self, url: str, **kwargs) -> Dict[str, Any]:
        """Execute scraping with retry logic."""
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                result = await self.scrape_data(url, **kwargs)
                if result.get("success", True):
                    if attempt > 0:
                        self.logger.info(f"Scraping succeeded after {attempt + 1} attempts")
                    return result
                else:
                    last_error = result.get("error", "Unknown error")
            except Exception as e:
                last_error = str(e)
                if attempt < self.max_retries - 1:
                    self.logger.warning(f"Attempt {attempt + 1} failed: {last_error}. Retrying...")
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        return self.format_error_result(f"Scraping failed after {self.max_retries} attempts: {last_error}")


class BaseStorageTool(BaseTool):
    """Base class for data storage tools."""
    
    def __init__(self, storage_format: str = "json", **kwargs):
        super().__init__(**kwargs)
        self.storage_format = storage_format
        self.supported_formats = ["json", "csv", "postgresql"]
    
    async def validate_input(
        self, 
        data: Union[Dict, List] = None, 
        filepath: str = None, 
        **kwargs
    ) -> Dict[str, Any]:
        """Validate storage input."""
        errors = []
        
        if data is None:
            errors.append("Data parameter is required")
        elif not isinstance(data, (dict, list)):
            errors.append("Data must be a dictionary or list")
        
        if self.storage_format in ["json", "csv"] and not filepath:
            errors.append("Filepath is required for file-based storage")
        
        if self.storage_format not in self.supported_formats:
            errors.append(f"Unsupported storage format: {self.storage_format}")
        
        return {
            "is_valid": len(errors) == 0,
            "error": "; ".join(errors) if errors else None,
            "details": errors
        }
    
    @abstractmethod
    async def store_data(self, data: Union[Dict, List], **kwargs) -> Dict[str, Any]:
        """Store data. Must be implemented by subclasses."""
        pass
    
    async def execute(self, data: Union[Dict, List], **kwargs) -> Dict[str, Any]:
        """Execute data storage."""
        return await self.store_data(data, **kwargs)


class BaseTransformTool(BaseTool):
    """Base class for data transformation tools."""
    
    def __init__(self, input_format: str = "dict", output_format: str = "dict", **kwargs):
        super().__init__(**kwargs)
        self.input_format = input_format
        self.output_format = output_format
    
    async def validate_input(self, data: Any = None, **kwargs) -> Dict[str, Any]:
        """Validate transformation input."""
        errors = []
        
        if data is None:
            errors.append("Data parameter is required")
        
        # Format-specific validation
        if self.input_format == "dict" and not isinstance(data, dict):
            errors.append("Data must be a dictionary for dict input format")
        elif self.input_format == "list" and not isinstance(data, list):
            errors.append("Data must be a list for list input format")
        
        return {
            "is_valid": len(errors) == 0,
            "error": "; ".join(errors) if errors else None,
            "details": errors
        }
    
    @abstractmethod
    async def transform_data(self, data: Any, **kwargs) -> Dict[str, Any]:
        """Transform data. Must be implemented by subclasses."""
        pass
    
    async def execute(self, data: Any, **kwargs) -> Dict[str, Any]:
        """Execute data transformation."""
        return await self.transform_data(data, **kwargs)


# Direct tool function creator for backward compatibility
def create_direct_tool_function(tool_class, function_name: str):
    """
    Create a direct tool function for backward compatibility.
    
    Args:
        tool_class: The tool class to instantiate
        function_name: Name of the function to create
    
    Returns:
        Async function that can be called directly
    """
    async def direct_function(**kwargs) -> Dict[str, Any]:
        try:
            tool = tool_class()
            result = await tool(**kwargs)
            return result
        except Exception as e:
            logger.error(f"Direct {function_name} error: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "function_name": function_name
            }
    
    direct_function.__name__ = function_name
    direct_function.__doc__ = f"Direct function wrapper for {tool_class.__name__}"
    
    return direct_function


class ToolRegistry:
    """Registry for managing all tools in the system."""
    
    def __init__(self):
        self._tools = {}
        self._tool_schemas = {}
    
    def register_tool(self, tool_class, name: Optional[str] = None):
        """Register a tool class."""
        tool_name = name or tool_class.__name__
        self._tools[tool_name] = tool_class
        
        # Create instance to get schema
        tool_instance = tool_class()
        self._tool_schemas[tool_name] = tool_instance.get_schema()
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get a tool instance by name."""
        tool_class = self._tools.get(name)
        return tool_class() if tool_class else None
    
    def get_all_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Get schemas for all registered tools."""
        return self._tool_schemas.copy()
    
    def list_tools(self) -> List[str]:
        """List all registered tool names."""
        return list(self._tools.keys())
    
    def create_direct_functions(self) -> Dict[str, callable]:
        """Create direct functions for all registered tools."""
        direct_functions = {}
        
        for name, tool_class in self._tools.items():
            function_name = f"{name.lower().replace('tool', '')}_direct"
            direct_functions[function_name] = create_direct_tool_function(tool_class, function_name)
        
        return direct_functions


# Global tool registry instance
tool_registry = ToolRegistry()