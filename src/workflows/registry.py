"""
Workflow Registry - Register and manage workflows
"""
from typing import Dict, Optional, TYPE_CHECKING
from loguru import logger

if TYPE_CHECKING:
    from .insights.flow import InsightsWorkflow
    from .listing_intake.flow import ListingIntakeWorkflow


class BaseWorkflow:
    """Base class for all workflows."""
    
    name: str = "base_workflow"
    description: str = "Base workflow"
    
    def execute(self, **kwargs) -> None:
        """Execute the workflow."""
        raise NotImplementedError("Subclasses must implement execute()")


class WorkflowRegistry:
    """
    Registry for all available workflows.
    
    Provides:
    - Registration of workflows
    - Lookup by name/intent
    - Workflow execution
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._workflows = {}
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._register_default_workflows()
            self._initialized = True
    
    def _register_default_workflows(self):
        """Register all default workflows."""
        # Import here to avoid circular imports
        from .insights.flow import InsightsWorkflow
        from .listing_intake.flow import ListingIntakeWorkflow
        from .registration.flow import RegistrationWorkflow
        
        self.register(InsightsWorkflow())
        self.register(ListingIntakeWorkflow())
        self.register(RegistrationWorkflow())
        
        logger.info(f"Registered {len(self._workflows)} workflows")
    
    def register(self, workflow: BaseWorkflow) -> None:
        """Register a workflow."""
        self._workflows[workflow.name] = workflow
        logger.info(f"Registered workflow: {workflow.name}")
    
    def get_workflow(self, name: str) -> Optional[BaseWorkflow]:
        """Get a workflow by name."""
        return self._workflows.get(name)
    
    def list_workflows(self) -> Dict[str, str]:
        """List all registered workflows with descriptions."""
        return {
            name: wf.description 
            for name, wf in self._workflows.items()
        }
