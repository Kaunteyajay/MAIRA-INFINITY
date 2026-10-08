"""
Tool Registry

Manages available tools and their capabilities.
"""

import logging
from typing import Dict, List, Optional, Any

from maira.tools.base import Tool, RiskLevel

logger = logging.getLogger(__name__)

class ToolRegistry:
    """Registry for managing available tools."""
    
    def __init__(self):
        self._tools: Dict[str, Tool] = {}
        self._capabilities: Dict[str, bool] = {
            "web_search": True,
            "code_execution": True,
            "file_access": False,
            "system_control": False,
            "internet_control": False,
            "learning_mode": True
        }
    
    def register_tool(self, tool: Tool) -> None:
        """Register a tool."""
        self._tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name} (risk: {tool.risk_level.value})")
    
    def get_tool(self, name: str) -> Optional[Tool]:
        """Get a tool by name."""
        return self._tools.get(name)
    
    def get_available_tools(self) -> List[Tool]:
        """Get all available tools based on enabled capabilities."""
        available = []
        
        for tool in self._tools.values():
            if self._capabilities.get(tool.required_capability, False):
                available.append(tool)
        
        return available
    
    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """Get OpenAI-compatible schemas for available tools."""
        return [tool.get_schema() for tool in self.get_available_tools()]
    
    def set_capability(self, capability: str, enabled: bool) -> None:
        """Enable or disable a capability."""
        if capability in self._capabilities:
            self._capabilities[capability] = enabled
            logger.info(f"Capability {capability} set to {enabled}")
        else:
            logger.warning(f"Unknown capability: {capability}")
    
    def get_capabilities(self) -> Dict[str, bool]:
        """Get current capability status."""
        return self._capabilities.copy()
    
    def get_tools_by_risk(self, max_risk: RiskLevel) -> List[Tool]:
        """Get tools up to a certain risk level."""
        risk_order = {RiskLevel.LOW: 1, RiskLevel.MEDIUM: 2, RiskLevel.HIGH: 3}
        max_risk_value = risk_order[max_risk]
        
        return [
            tool for tool in self.get_available_tools()
            if risk_order[tool.risk_level] <= max_risk_value
        ]