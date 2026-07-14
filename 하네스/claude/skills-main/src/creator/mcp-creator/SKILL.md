---
name: mcp-creator
description: Guide for planning MCP servers that enable LLMs to interact with external services through tools.
license: Complete terms in LICENSE.md
metadata:
  version: v1.1.0
  when_to_use: Use when planning MCP servers to integrate external services in Python (FastMCP).
  disable-model-invocation: true
---

# MCP Server Planning Guide

Guide for planning Remote MCP (Model Context Protocol) servers. Quality of a MCP server is measured by how well it enables LLMs to accomplish real-world tasks.


## Process

Planning a Remote MCP server involves four main phases:

### 1. Understand the Concept

**Balance endpoints and workflows.**
- Endpoint tools are comprehensive, and workflows are specialized.
- Workflow tools are more convenient for *specific* tasks, while endpoints offer flexibility.
- Performance is cilent-by-client; when uncertain, prioritize workflow tools.

**Clarify the purpose of the tool.**
- Use action-oriented, self-descriptive naming. (e.g., `create_issue`, `list_repos`)
- Provide a clear, concise description in English — state when to use.
- One word per concept; use the most specific term available like specifications.

**One Tool, One Focused Result.**
- Design tools that return focused, relevant data.
- If results are huge, benefit LLMs with the ability to filter/paginate results.
- If cross-tool utilization is required, complete the plan, then suggest skill creation.


### 2. Study Specifications and Documentations

**Study the MCP specification.**
1. Start with the sitemap to find relevant pages: `https://modelcontextprotocol.io/sitemap.xml`
2. Fetch specific pages with `.md` suffix to read properly. (e.g., `https://modelcontextprotocol.io/specification/draft.md`).

Key pages to review:
- Specification overview and architecture
- Tool, resource, and prompt definitions
- Streamable HTTP transport mechanisms (ignore stdio and SSE; we'll not use them)


**Load framework documentation.**
- [MCP Best Practices](./references/best_practices.md) — Core guidelines.
- [Python Implementation Guide](./references/fastmcp.md) — Python patterns and examples.


### 3. Identify the Target

The plan is divided by target: External or Self-hosted.

#### External API

**Understand the target service.**
- Review the service's API documentation.
- Identify key endpoints and data models.
- Use web search and WebFetch as needed.

#### Self-hosted API

**Make a brief plan for the API.**
- a REST API written in Python (FastAPI); use `StreamingResponse` (jsonl) for the response.
- API is hosted in a different location; accessed via Cloudflare Tunnel.
- Utilize playwright, filesystem, session-based CLI tools.

### 4. Plan the Implementation

- List the tools to implement — filter endpoints by need and non-need.
- If the usage flow is same, process results on the MCP server.
- Now, start with the most common operations.


## Implementing

**Ignore this unless requested for actual implementation.**

Load if you were asked to implement actual code:
- [Implementation Guide](./references/implementation.md)


## References

Load these resources as needed during planning:

### MCP Specification
- **MCP Protocol**: Start with sitemap at `https://modelcontextprotocol.io/sitemap.xml`, fetch specific pages with `.md` suffix
- [MCP Best Practices](./references/best_practices.md) - Universal MCP guidelines including:
  - Tool design conventions
  - Pagination best practices

### SDK Documentation
- [Python Implementation Guide](./references/fastmcp.md) - Brief Python/FastMCP guide with:
  - Tool registration patterns
  - Pydantic model examples
- **FastMCP Documentation**: Fetch from `https://gofastmcp.com/servers/server.md`
