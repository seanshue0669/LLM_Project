# agents/mycore/base_tool.py

def auto_wrap_error(method):
    """
    Decorator that automatically wraps exceptions with method context.
    
    When an exception occurs in a decorated method, it will be re-raised
    with the class name and method name prepended to the error message.
    
    Usage:
        @auto_wrap_error
        def some_method(self, ...):
            # your logic here
    
    Args:
        method: The method to be wrapped
        
    Returns:
        wrapped: The wrapped method with error handling
    """
    def wrapped(self, *args, **kwargs):
        try:
            # Call the original method and return its result
            result = method(self,*args,**kwargs)
            return result
        except Exception as e:
            # Get class name and method name
            class_name = self.__class__.__name__   
            method_name = method.__name__
            # Raise new exception with formatted message "[ClassName.method_name] original_error"
            raise Exception(f"[{class_name}.{method_name}] {e}")
    return wrapped


class BaseTool:
    """
    Base class for all tools in the agent system.
    
    Provides common infrastructure for tool implementations.
    Subclasses should use @auto_wrap_error decorator on methods
    that need automatic error tracking.
    """
    
    def __init__(self):
        """
        Initialize the base tool.
        
        Subclasses should call super().__init__() and then
        initialize their own specific attributes.
        """
        pass