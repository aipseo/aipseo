"""Mock MCP implementation for testing purposes."""

class FastMCP:
    """Mock FastMCP implementation for testing."""
    
    def __init__(self, name: str):
        self.name = name
        self._tools = []
    
    def tool(self):
        """Decorator to register a tool."""
        def decorator(func):
            self._tools.append({
                "name": func.__name__,
                "func": func
            })
            return func
        return decorator
    
    async def list_tools(self):
        """Return list of registered tools."""
        return [{"name": tool["name"]} for tool in self._tools]
    
    def run(self, host: str = "0.0.0.0", port: int = 8000):
        """Mock run method."""
        pass 