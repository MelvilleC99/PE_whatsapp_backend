"""
Context Manager - Manages conversation context and memory

Responsible for:
- Tracking conversation history
- Summarizing long conversations
- Managing workflow state
"""
from typing import Dict, Any, Optional, List
from loguru import logger


class ContextManager:
    """
    Manages context across conversations.
    
    Works with ConversationStore to provide relevant context
    for LLM calls and workflow execution.
    """
    
    def __init__(self, max_messages: int = 5):
        self.max_messages = max_messages
    
    def build_context(
        self, 
        phone: str, 
        conversation_history: List[Dict],
        current_workflow: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Build context object for LLM/workflow use.
        
        Args:
            phone: User's phone number
            conversation_history: Recent message history
            current_workflow: Currently active workflow if any
            
        Returns:
            Context dictionary
        """
        return {
            'phone': phone,
            'message_count': len(conversation_history),
            'recent_messages': conversation_history[-self.max_messages:],
            'current_workflow': current_workflow,
            'summary': self._summarize_if_needed(conversation_history)
        }
    
    def _summarize_if_needed(
        self, 
        conversation_history: List[Dict]
    ) -> Optional[str]:
        """
        Summarize conversation if it's long.
        
        Args:
            conversation_history: Full conversation history
            
        Returns:
            Summary string or None if not needed
        """
        if len(conversation_history) <= self.max_messages:
            return None
        
        # TODO: Use LLM to summarize older messages
        return None
