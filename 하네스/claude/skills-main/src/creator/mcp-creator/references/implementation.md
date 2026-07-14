# MCP Server Implementation Guide

Python-specific best practices and checklists for implementing MCP servers. Covers code-level patterns for writing FastMCP servers.

Disclaimer: The actual implementation uses internal fork of FastMCP; behavior may vary.

# Process

Do not start until the plan is complete and approved. The plan should be detailed enough to guide implementation w/o ambiguity.

## 1. Understand the Structure

Working project must be set up. Read `CLAUDE.md` and understand the project and the plan.

---

## 2. Implement

For each tool:
- **Input Schema:** Validate input w/ Pydantic. Provide field description.
- **Tool Description:** Concise functionality summary.
- **Implementation:** Use async. Raise error w/ actionable details.


### Server Setup

```python
from fastmcp import FastMCP

mcp = FastMCP("service", instructions="...")

if __debug__ and __name__ == "__main__":
    import uvicorn
    uvicorn.run(mcp.http_app("/mcp"), ...)
```

Server name is `{service}` — no suffix.


### Tool Registration

```python
from typing import Annotated
from pydantic import Field
from fastmcp import FastMCP

mcp = FastMCP("example")

@mcp.tool("Get User", "1.0.0", {"readOnly"})
async def get_user(
    user_id: Annotated[str, Field(
        min_length=1,
        description="User ID (e.g. 'U123456')"
    )],
) -> UserDetail:
    """Get a user by ID. Returns full profile. Use when you have a user ID and need details.
    Do not use for search — use search_users instead.
    """
    ...
```

Docstring = tool description only. Do not add Args/Returns/Examples.

#### Annotations

| Key | Meaning |
|-----|---------|
| `readOnlyHint` | No state mutation |
| `destructiveHint` | May delete/overwrite |
| `idempotentHint` | Repeated calls are safe |
| `openWorldHint` | Accesses external services |

Every annotations are default to `False`.


### Input Validation

Use `Annotated` + `Field` on parameters. Use `Depends` for shared validation.

```python
from fastmcp.server.dependencies import Depends

def normalize_query(query: str) -> str:
    if not query.strip():
        raise ValueError("Query cannot be empty")
    return query.strip().lower()

@mcp.tool(...)
async def search_users(
    query: Annotated[str, Field(description="Search string", min_length=2, max_length=200)] = Depends(normalize_query),
    limit: Annotated[int, Field(description="Max results (1–100)", ge=1, le=100)] = 20,
):
    ...
```

Let Pydantic handle validation — do not write manual `if` checks.


### Structured Outputs

Return Pydantic models. FastMCP generates output schema automatically.

```python
from pydantic import BaseModel
from datetime import datetime

class UserDetail(BaseModel):
    id: str
    name: str
    email: str
    created_at: datetime

@mcp.tool(...)
async def get_user(user_id: str) -> UserDetail:
    return UserDetail(**raw)
```


### Error Handling

Centralize error formatting. Provide actionable messages; do not expose internals.

```python
def _handle_error(e: Exception, /) -> str:
    if isinstance(e, httpx.HTTPStatusError):
        match e.response.status_code:
            case 404: return "Error: Not found. Check the ID."
            case 403: return "Error: Permission denied."
            case 429: return "Error: Rate limited. Retry later."
            case _:   return f"Error: HTTP {e.response.status_code}."
    if isinstance(e, httpx.TimeoutException):
        return "Error: Request timed out."
    return "Error: Unexpected failure."
```

Use in tools:

```python
try:
    data = await _request("GET", f"users/{user_id}")
    return UserDetail(**data)
except Exception as e:
    return _handle_error(e)
```

---

## 3. Review Quality

Review for:
- No duplicate code (DRY principle)
- Consistent error handling
- Clear tool descriptions

### Quality Checklist

**Tools**
- [ ] Docstring covers purpose, when to use, when not to use — nothing else
- [ ] All parameters use `Annotated` + `Field` w/ description & constraints
- [ ] `annotations` set correctly on `@mcp.tool`

**Code Quality**
- [ ] No manual Pydantic validation — use `Field` constraints or `Depends`
- [ ] No copy-paste logic — extract into shared functions
