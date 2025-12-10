"""
Tools module - Individual capabilities for the agent

Tools are auto-registered when they inherit from BaseTool.
Just create a new file in this directory with a class that:
  1. Inherits from BaseTool
  2. Has a unique 'name' attribute
  3. Implements execute()

Example:
    from src.tools.registry import BaseTool
    
    class MyNewTool(BaseTool):
        name = "my_new_tool"
        description = "Does something useful"
        
        def execute(self, **kwargs):
            return {'status': 'success', 'result': ...}
"""
from .registry import BaseTool, ToolRegistry

# Initialize registry (triggers auto-discovery)
registry = ToolRegistry()

__all__ = [
    'BaseTool',
    'ToolRegistry', 
    'registry'
]
