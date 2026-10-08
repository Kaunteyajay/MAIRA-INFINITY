"""
Permission Gate

Controls access to tools based on user permissions and risk levels.
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from enum import Enum

from maira.tools.base import Tool, RiskLevel, ToolContext
from maira.core.event_bus import EventBus, PermissionRequestEvent, PermissionResponseEvent
from maira.infra.db import DatabaseManager

logger = logging.getLogger(__name__)

class PermissionTier(Enum):
    """Permission levels for tools."""
    OFF = "off"
    ASK = "ask" 
    ALLOW = "allow"

class PermissionGate:
    """Controls access to tools based on permissions."""
    
    def __init__(self, event_bus: EventBus, db: DatabaseManager):
        self.event_bus = event_bus
        self.db = db
        
        # Cache permissions
        self._permission_cache: Dict[str, PermissionTier] = {}
        self._pending_requests: Dict[str, asyncio.Future] = {}
        
        # Default permissions for capabilities
        self._default_permissions = {
            "web_search": PermissionTier.ALLOW,
            "code_execution": PermissionTier.ASK,
            "file_access": PermissionTier.OFF,
            "system_control": PermissionTier.OFF,
            "internet_control": PermissionTier.ASK,
            "learning_mode": PermissionTier.ALLOW
        }
    
    async def start(self) -> None:
        """Initialize permission gate."""
        # Subscribe to permission responses
        await self.event_bus.subscribe(PermissionResponseEvent, self._handle_permission_response)
        
        # Load permissions from database
        await self._load_permissions()
    
    async def check_permission(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        tool_instance: Tool,
        context: Optional[ToolContext] = None
    ) -> bool:
        """Check if tool execution is permitted."""
        capability = tool_instance.required_capability
        
        # Get permission tier
        permission_key = f"{capability}:{tool_name}"
        tier = self._permission_cache.get(
            permission_key,
            self._default_permissions.get(capability, PermissionTier.ASK)
        )
        
        logger.debug(f"Permission check: {tool_name} -> {tier}")
        
        # Handle based on tier
        if tier == PermissionTier.OFF:
            logger.info(f"Tool {tool_name} denied (capability disabled)")
            return False
        
        elif tier == PermissionTier.ALLOW:
            # Still check for high-risk actions
            if tool_instance.risk_level == RiskLevel.HIGH:
                return await self._request_user_permission(tool_name, arguments, tool_instance)
            return True
        
        elif tier == PermissionTier.ASK:
            return await self._request_user_permission(tool_name, arguments, tool_instance)
        
        return False
    
    async def _request_user_permission(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        tool_instance: Tool
    ) -> bool:
        """Request permission from user."""
        request_id = f"perm_{hash((tool_name, str(arguments))) % 10000}"
        
        # Check if already pending
        if request_id in self._pending_requests:
            return await self._pending_requests[request_id]
        
        # Create future for response
        response_future = asyncio.Future()
        self._pending_requests[request_id] = response_future
        
        try:
            # Create permission description
            description = self._describe_action(tool_name, arguments, tool_instance)
            
            # Publish permission request
            await self.event_bus.publish(PermissionRequestEvent(
                tool_name=tool_name,
                scope=self._get_scope(arguments),
                risk_level=tool_instance.risk_level.value,
                description=description,
                request_id=request_id
            ))
            
            logger.info(f"Permission requested: {tool_name} (id: {request_id})")
            
            # Wait for response (with timeout)
            try:
                granted = await asyncio.wait_for(response_future, timeout=30.0)
                return granted
            except asyncio.TimeoutError:
                logger.warning(f"Permission request timeout: {request_id}")
                return False
            
        finally:
            self._pending_requests.pop(request_id, None)
    
    async def _handle_permission_response(self, event: PermissionResponseEvent) -> None:
        """Handle user permission response."""
        request_id = event.request_id
        
        if request_id in self._pending_requests:
            future = self._pending_requests[request_id]
            if not future.done():
                future.set_result(event.granted)
            
            logger.info(f"Permission response: {request_id} -> {event.granted}")
            
            # Save to database if remember is requested
            if event.remember and event.granted:
                # TODO: Store permission preference
                pass
    
    def _describe_action(self, tool_name: str, arguments: Dict[str, Any], tool: Tool) -> str:
        """Create human-readable description of the action."""
        if tool_name == "web_search":
            query = arguments.get("query", "unknown")
            return f"Search the web for: '{query}'"
        
        elif tool_name == "run_python":
            code = arguments.get("code", "")[:100]
            return f"Execute Python code: {code}{'...' if len(code) > 100 else ''}"
        
        elif tool_name == "read_file":
            path = arguments.get("path", "unknown")
            return f"Read file: {path}"
        
        elif tool_name == "write_file":
            path = arguments.get("path", "unknown")
            return f"Write to file: {path}"
        
        else:
            return f"Execute {tool_name} with parameters: {arguments}"
    
    def _get_scope(self, arguments: Dict[str, Any]) -> str:
        """Extract scope from arguments (e.g., file path, URL)."""
        # Look for common scope indicators
        for key in ["path", "file", "url", "directory", "command"]:
            if key in arguments:
                return str(arguments[key])
        
        return "general"
    
    async def _load_permissions(self) -> None:
        """Load permissions from database."""
        try:
            cursor = await self.db.connection.execute(
                "SELECT tool_name, scope, tier FROM permissions"
            )
            
            async for row in cursor:
                key = f"{row[1]}:{row[0]}" if row[1] != "general" else row[0]
                self._permission_cache[key] = PermissionTier(row[2])
            
            logger.info(f"Loaded {len(self._permission_cache)} permissions from database")
            
        except Exception as e:
            logger.error(f"Error loading permissions: {e}")
    
    async def set_permission(self, tool_name: str, scope: str, tier: PermissionTier) -> None:
        """Set permission for a tool."""
        key = f"{scope}:{tool_name}" if scope != "general" else tool_name
        self._permission_cache[key] = tier
        
        try:
            await self.db.connection.execute(
                """
                INSERT OR REPLACE INTO permissions (tool_name, scope, tier, granted_at)
                VALUES (?, ?, ?, datetime('now'))
                """,
                (tool_name, scope, tier.value)
            )
            await self.db.connection.commit()
            logger.info(f"Permission set: {tool_name} ({scope}) -> {tier.value}")
        except Exception as e:
            logger.error(f"Error saving permission: {e}")