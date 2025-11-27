# agents/mycore/error_formatter.py
import re
def format_error_path(error_message: str) -> str:
    """
    Format error message into a readable path structure.
    
    Input format:
        "[GraphA: nodeX] [GraphB: nodeY] [Tool.method] [LLMClient.invoke] Error reason"
    
    Output format:
        Error Path:
          → GraphA: nodeX
          → GraphB: nodeY
          → Tool.method
          → LLMClient.invoke
        Final Error: Error reason
    
    Args:
        error_message: Raw error string with bracketed path
        
    Returns:
        Formatted multi-line error message
    """
    path_parts = re.findall(r'\[([^\]]+)\]', error_message)
    final_error = re.sub(r'\[([^\]]+)\]\s*', '', error_message).strip()
    
    if not path_parts:
        return error_message
    
    formatted = "Error Path:\n"
    for part in path_parts:
        formatted += f"  → {part}\n"
    
    if final_error:
        formatted += f"Final Error: {final_error}"
    
    return formatted
    pass