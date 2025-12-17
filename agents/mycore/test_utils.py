# agents/mycore/test_utils.py
from agents.mycore.error_formatter import format_error_path

def test_wrapper(test_func):
    """Wrapper for test functions to handle errors gracefully"""
    def wrapped(*args, **kwargs):
        try:
            result = test_func(*args, **kwargs)
            print("✓ Test passed!")
            return result
        except Exception as e:
            formatted_error = format_error_path(str(e))
            print("✗ Test failed!")
            print(formatted_error)
    return wrapped