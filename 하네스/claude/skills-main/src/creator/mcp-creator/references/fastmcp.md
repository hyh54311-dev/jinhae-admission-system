# Python Implementation Planning Guide

Python-specific best practices. It covers input validation with Pydantic, error handling.

Disclaimer: The actual implementation uses internal fork of FastMCP; behavior may vary.
Ignore the difference; **focus on planning.**

---

## FastMCP

FastMCP is a high-level framework for building MCP servers. It provides:
- Automatic description and inputSchema generation from signatures and docstrings
- Pydantic integration for input validation
- Decorator-based registration with `@mcp.tool`

**For complete framework documentation, use WebFetch to load:** `https://gofastmcp.com/servers/server.md`

### Pydantic v2 integration

- The function's parameters are equal to the tool
- Provide details using `Annotated` and `Field`
- Use `Depends` when performing the same verifying/processing multiple times
- Parameter name of the dependency must be equal to the function

```python
from typing import Annotated
from pydantic import Field

def validate_email(email: str):
    if not email.strip():
        raise ValueError("Email cannot be empty")
    return v.lower()

@mcp.tool(...)
async def create_user(
    name: Annotated[str, Field(..., description="Full name of the user", min_length=2, max_length=100)],
    # Makes 'email' always the result of validate_email()
    email: Annotated[str, Field(..., description="Email address of the user", pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")] = Depends(validate_email),
    # Makes 'age' optional
    age: Annotated[int | None, Field(..., description="Age of the user", ge=0, le=150)] = None,
):
    # Function docstring automatically becomes the 'description' field.
    """Performs specific operation on the service. Validates all inputs automatically before processing."""
```

### Structured Outputs

When creating a response model:
- Return complete, structured data suitable for programmatic processing
- Include all available fields and metadata
- Use consistent field names and types

```python
from typing import Any
from pydantic import BaseModel

# Pydantic models for complex validation
class DetailedUser(BaseModel):
    id: str
    name: str
    email: str
    created_at: datetime
    metadata: dict[str, Any]

@mcp.tool(...)
async def get_user_detailed(user_id: str) -> DetailedUser:
    """Returns Pydantic model - automatically generates schema."""
    user = await fetch_user(user_id)
    return DetailedUser(**user)
```

### Pagination Implementation

For tools that list huge amount of resources:

```python
async def list_items(
    limit: Annotated[int | None, Field(description="Maximum results to return", ge=1, le=100)] = 20,
    offset: Annotated[int | None, Field(description="Number of results to skip for pagination", ge=0)] = 0
):
    ...
```

### Error Handling

Provide clear, actionable error messages:

```python
def _handle_api_error(e: Exception) -> str:
    '''Consistent error formatting across all tools.'''
    if isinstance(e, httpx.HTTPStatusError):
        if e.response.status_code == 404:
            return "Error: Resource not found. Please check the ID is correct."
        elif e.response.status_code == 403:
            return "Error: Permission denied. You don't have access to this resource."
        elif e.response.status_code == 429:
            return "Error: Rate limit exceeded. Please wait before making more requests."
        return f"Error: API request failed with status {e.response.status_code}"
    elif isinstance(e, httpx.TimeoutException):
        return "Error: Request timed out. Please try again."
    return f"Error: Unexpected error occurred"
```

**Do not expose internal error messages.**

---

## Advanced FastMCP Features

### Context Parameter Injection

FastMCP can automatically inject a `Context` parameter into tools for advanced capabilities like logging, progress reporting, resource reading, and user interaction:

```python
from fastmcp.server import Context

@mcp.tool()
async def advanced_search(query: str, ctx: Context) -> str:
    """Advanced tool with context access for logging and progress."""

    # Report progress for long operations
    await ctx.report_progress(0.25, "Starting search...")

    # Log information for debugging
    await ctx.log_info("Processing query", {"query": query, "timestamp": datetime.now()})

    # Perform search
    results = await search_api(query)
    await ctx.report_progress(0.75, "Formatting results...")

    # Access server configuration
    server_name = ctx.fastmcp.name

    return format_results(results)

@mcp.tool()
async def interactive_tool(resource_id: str, ctx: Context) -> str:
    """Tool that can request additional input from users."""

    # Request sensitive information when needed
    api_key = await ctx.elicit(
        prompt="Please provide your API key:",
        input_type="password"
    )

    # Use the provided key
    return await api_call(resource_id, api_key)
```

**Context capabilities:**
- `ctx.report_progress(progress, message)` - Report progress for long operations
- `ctx.log_info(message, data)` / `ctx.log_error()` / `ctx.log_debug()` - Logging
- `ctx.elicit(prompt, input_type)` - Request input from users
- `ctx.fastmcp.name` - Access server configuration
- `ctx.read_resource(uri)` - Read MCP resources

### Resource Registration

Expose data as resources for efficient, template-based access:

```python
@mcp.resource("file://documents/{name}")
async def get_document(name: str) -> str:
    """Expose documents as MCP resources.

    Resources are useful for static or semi-static data that doesn't
    require complex parameters. They use URI templates for flexible access."""
    document_path = f"./docs/{name}"
    with open(document_path, "r") as f:
        return f.read()

@mcp.resource("config://settings/{key}")
async def get_setting(key: str, ctx: Context) -> str:
    """Expose configuration as resources with context."""
    settings = await load_settings()
    return json.dumps(settings.get(key, {}))
```

**When to use Resources vs Tools:**
- **Resources**: For data access with simple parameters (URI templates)
- **Tools**: For complex operations with validation and business logic

### Lifespan Management

Initialize resources that persist across requests:

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def app_lifespan():
    """Manage resources that live for the server's lifetime."""
    # Initialize connections, load config, etc.
    db = await connect_to_database()
    config = load_configuration()

    # Make available to all tools
    yield {"db": db, "config": config}

    # Cleanup on shutdown
    await db.close()

# (lifespan registration) ...

@mcp.tool()
async def query_data(query: str, ctx: Context) -> str:
    """Access lifespan resources through context."""
    db = ctx.request_context.lifespan_state["db"]
    results = await db.query(query)
    return format_results(results)
```

---

## Code Planning Best Practices

### Composability and Reusability

The implementation plan MUST prioritize composability and code reuse:

1. **Extract Common Functionality**:
   - Create reusable helper functions used across multiple tools
   - Centralize error handling logic, Share API clients
   - Extract business logic into dedicated modules that can be composed
   - NEVER unnecessary abstraction and extraction

2. **Avoid Duplication**:
   - NEVER copy-paste similar logic between tools
   - If you find logic that appears multiple times in the plan, extract it
   - Common operations (pagination, filtering, formatting) should be shared
   - Authentication/authorization logic should be centralized

### Python-Specific Best Practices

1. **Use Type Hints**: Always provide type annotations for parameters and return
2. **Let Pydantic handle inputs**: Define clear Pydantic models; no manual validation
3. **Error Handling**: Use specific exception types, not generic Exception
4. **Async Context Managers**: Use `async with` for resources that need cleanup
