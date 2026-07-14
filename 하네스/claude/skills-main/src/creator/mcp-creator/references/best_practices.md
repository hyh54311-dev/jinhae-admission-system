# MCP Server Best Practices

## Quick Reference

### Tool Design
- Names should be action-oriented, self-descriptive
- Descriptions must be clear, concise, simple
- Keep tool operations focused and atomic

### Pagination
- Always respect `limit` parameter
- Return `has_more`, `next_offset`, `total_count`
- Default to 20-50 items

### Transport
- **Streamable HTTP**: For remote servers
- Ignore stdio (Our MCP servers are all remote)
- Avoid SSE (deprecated in favor of streamable HTTP)

---

## Tool Design

### Naming

1. **Use snake_case**: `search_users`, `create_project`, `get_channel_info`
2. **Be action-oriented**: Start with verbs (get, list, search, create, etc.)
3. **Be unique**: Avoid generic names that could conflict with others

### Design

- Keep tool operations focused and atomic
- Process the results in the server as possible
- Sub-server name should follow: `[{namespace}_]{operation}[_{object}]` (e.g., `read`, `note_list`, `pdf_extract_str`)
- Descriptions must narrowly and unambiguously describe functionality
- Descriptions must precisely match actual functionality

### Tool Annotations

Provide annotations to help LLMs understand tool behavior:

| Annotation | Default | Description |
|-----------|---------|-------------|
| `readOnlyHint` | `False` | Tool does not modify its environment |
| `destructiveHint` | `True` | Tool may perform destructive updates |
| `idempotentHint` | `False` | Repeated calls with same args have no additional effect |
| `openWorldHint` | `True` | Tool interacts with external (not target) entities |

**Important**: Annotations are hints, not security guarantees. LLMs should not make security-critical decisions based solely on annotations.

---

## Response and Transport

### JSON Format

- Machine-readable structured data
- Include all available fields and metadata
- Consistent field names and types
- Use for programmatic processing

### Streamable HTTP

- Bidirectional communication over HTTP
- Supports real-time connections
- Can be deployed as a serverless function
- Enables server-to-client notifications

### Error Handling

- Use standard JSON-RPC error codes
- Report tool errors within result objects (not protocol-level errors)
- Provide helpful, specific details with suggested next steps
- Clean up resources properly on errors
- **Do not expose internal errors**

### Pagination

For tools that list huge amount of resources:

- **Always respect the `limit` parameter**
- Implement `offset` or cursor-based pagination (`offset` is simple and typical)
- Return pagination metadata (`has_more`, `next_offset`/`next_cursor`, `total`)
- Default to reasonable limits, typically 20‒50
- **Never load all results into memory**, especially IMPORTANT for large datasets

Example pagination response:
```json
{
  "total": 150,
  "count": 20,
  "offset": 0,
  "items": [...],
  "has_more": true,
  "next_offset": 20
}
```

---

## Security Best Practices

### Input Validation

- Sanitize file paths to prevent directory traversal
- Validate URLs and external identifiers
- Check parameter sizes and ranges
- Prevent command injection in system calls
- Use schema validation (Pydantic) for all inputs

### Error Handling

- Do not expose internal errors; log server-side
- Provide helpful but not revealing messages
- Clean up resources after errors

### Authentication

**External IdP (CIMD)**:
- Store service keys in environs, never in code
- Validate user information before processing requests
- Provide clear error messages when authentication fails

**OAuth 2.1**:
- Use secure OAuth 2.1 with certificates from recognized authorities
- Validate access tokens before processing requests
- Only accept tokens specifically intended for your server

### DNS Rebinding Protection

For streamable HTTP servers running locally:
- Enable DNS rebinding protection
- Validate the `Origin` header on all incoming connections
- Bind to `127.0.0.1` rather than `0.0.0.0`
