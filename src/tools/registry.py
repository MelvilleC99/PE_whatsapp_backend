"""
Tool Registry - Auto-registers and manages tools

Features:
- Auto-registration via __init_subclass__
- Auto-discovery via directory scanning
- Tool lookup by name
- LLM-friendly tool schemas
- LangChain integration (future)
"""
import importlib
import pkgutil
from pathlib import Path
from typing import Dict, List, Optional, Any, Type
from loguru import logger


class ToolParameter:
    """Defines a single parameter for a tool."""
    
    def __init__(
        self,
        name: str,
        type: str,
        description: str,
        required: bool = True,
        default: Any = None,
        enum: List[str] = None
    ):
        self.name = name
        self.type = type  # string, number, boolean, array, object
        self.description = description
        self.required = required
        self.default = default
        self.enum = enum  # Allowed values (optional)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary (for JSON schema)."""
        d = {
            "type": self.type,
            "description": self.description
        }
        if self.enum:
            d["enum"] = self.enum
        if self.default is not None:
            d["default"] = self.default
        return d


class BaseTool:
    """
    Base class for all tools.
    
    Any class that inherits from BaseTool is automatically registered.
    
    Required attributes:
        name: Unique tool identifier
        description: When to use this tool (be specific!)
        
    Optional attributes:
        parameters: List of ToolParameter objects
        examples: Usage examples for the LLM
        output_description: What the tool returns
    """
    
    # Class-level registry (shared across all instances)
    _registry: Dict[str, Type['BaseTool']] = {}
    
    # Tool metadata (override in subclasses)
    name: str = "base_tool"
    description: str = "Base tool - do not use directly"
    
    # Parameters schema (override in subclasses)
    parameters: List[ToolParameter] = []
    
    # Examples of when to use this tool (helps LLM understand)
    examples: List[Dict[str, str]] = []
    
    # Description of what the tool returns
    output_description: str = "Returns a dict with 'status' and result data"
    
    def __init_subclass__(cls, **kwargs):
        """
        Auto-called when any class inherits from BaseTool.
        Registers the tool automatically.
        """
        super().__init_subclass__(**kwargs)
        
        # Don't register the base class itself
        if cls.name != "base_tool":
            BaseTool._registry[cls.name] = cls
            logger.debug(f"Auto-registered tool: {cls.name}")
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the tool with given parameters.
        Override this in subclasses.
        """
        raise NotImplementedError("Subclasses must implement execute()")
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """
        Get the tool schema in a format suitable for LLMs.
        Compatible with OpenAI function calling format.
        """
        # Build properties dict from parameters
        properties = {}
        required = []
        
        for param in cls.parameters:
            properties[param.name] = param.to_dict()
            if param.required:
                required.append(param.name)
        
        return {
            "name": cls.name,
            "description": cls.description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required
            }
        }
    
    @classmethod
    def get_prompt_description(cls) -> str:
        """
        Get a text description suitable for including in a prompt.
        """
        lines = [
            f"**{cls.name}**",
            f"Description: {cls.description}",
        ]
        
        if cls.parameters:
            lines.append("Parameters:")
            for param in cls.parameters:
                req = "(required)" if param.required else "(optional)"
                lines.append(f"  - {param.name} ({param.type}) {req}: {param.description}")
        
        if cls.examples:
            lines.append("Examples:")
            for ex in cls.examples:
                lines.append(f"  - Use when: {ex.get('when', 'N/A')}")
        
        lines.append(f"Returns: {cls.output_description}")
        
        return "\n".join(lines)
    
    def to_langchain_tool(self):
        """Convert to LangChain tool format."""
        # TODO: Implement LangChain conversion
        pass


class ToolRegistry:
    """
    Registry for all available tools.
    
    Usage:
        registry = ToolRegistry()
        
        # Get a tool by name
        tool = registry.get("transcription")
        result = tool.execute(audio_id="abc123")
        
        # List all tools
        print(registry.list_tools())
        
        # Get schemas for LLM
        schemas = registry.get_all_schemas()
    """
    
    _instance = None
    _discovered = False
    
    def __new__(cls):
        """Singleton pattern - only one registry instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize and auto-discover tools."""
        if not ToolRegistry._discovered:
            self._auto_discover_tools()
            ToolRegistry._discovered = True
    
    def _auto_discover_tools(self):
        """
        Scan the tools directory and import all modules.
        This triggers __init_subclass__ for each tool class.
        """
        tools_dir = Path(__file__).parent
        
        logger.info(f"Discovering tools in {tools_dir}")
        
        for module_info in pkgutil.iter_modules([str(tools_dir)]):
            module_name = module_info.name
            
            # Skip registry itself and __pycache__
            if module_name in ('registry', '__init__'):
                continue
            
            try:
                importlib.import_module(f".{module_name}", package="src.tools")
                logger.debug(f"Loaded tool module: {module_name}")
            except Exception as e:
                logger.error(f"Failed to load tool module {module_name}: {e}")
        
        logger.info(f"Discovered {len(BaseTool._registry)} tools: {list(BaseTool._registry.keys())}")
    
    def get(self, name: str) -> Optional[BaseTool]:
        """
        Get a tool instance by name.
        
        Args:
            name: Tool name
            
        Returns:
            Tool instance or None if not found
        """
        tool_class = BaseTool._registry.get(name)
        
        if tool_class:
            return tool_class()
        
        logger.warning(f"Tool not found: {name}")
        return None
    
    def get_class(self, name: str) -> Optional[Type[BaseTool]]:
        """
        Get a tool class (not instance) by name.
        
        Args:
            name: Tool name
            
        Returns:
            Tool class or None
        """
        return BaseTool._registry.get(name)
    
    def list_tools(self) -> List[str]:
        """List all registered tool names."""
        return list(BaseTool._registry.keys())
    
    def get_all(self) -> Dict[str, Type[BaseTool]]:
        """Get all registered tool classes."""
        return BaseTool._registry.copy()
    
    def get_tool_descriptions(self) -> Dict[str, str]:
        """Get all tools with their descriptions."""
        return {
            name: cls.description 
            for name, cls in BaseTool._registry.items()
        }
    
    def get_all_schemas(self) -> List[Dict]:
        """
        Get all tool schemas in LLM-friendly format.
        Compatible with OpenAI function calling.
        """
        return [
            cls.get_schema() 
            for cls in BaseTool._registry.values()
        ]
    
    def get_prompt_descriptions(self) -> str:
        """
        Get all tool descriptions formatted for inclusion in a prompt.
        """
        descriptions = []
        for cls in BaseTool._registry.values():
            descriptions.append(cls.get_prompt_description())
        return "\n\n".join(descriptions)
    
    def get_langchain_tools(self) -> List:
        """
        Get all tools in LangChain format.
        
        Returns:
            List of LangChain tool objects
        """
        # TODO: Convert tools to LangChain format
        return []
