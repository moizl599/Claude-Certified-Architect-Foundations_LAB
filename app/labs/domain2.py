"""Domain 2: Tool Design & MCP Integration (18%) — Labs 2.1–2.2"""

LABS = [
    # ══════════════════════════════════════════════════════════════
    # LAB 2.1 — Build an MCP Server
    # ══════════════════════════════════════════════════════════════
    {
        "id": "2.1",
        "domain": 2,
        "domain_name": "Tool Design & MCP Integration",
        "title": "Build an MCP Server",
        "description": "Create a Model Context Protocol server from scratch with tools, resources, and prompts — the exact pattern tested in exam Scenario 4.",
        "difficulty": "intermediate",
        "estimated_time": "35 min",
        "task_statements": ["2.1", "2.2", "2.3"],
        "steps": [
            {
                "id": 1,
                "title": "MCP Server Basics",
                "language": "python",
                "instruction": """## MCP Server Basics

The **Model Context Protocol (MCP)** is a standard for connecting AI models to external tools and data. Think of it as USB-C for AI — a universal plug.

An MCP server exposes:
- **Tools** — functions the model can call (like API endpoints)
- **Resources** — data the model can read (like files or databases)
- **Prompts** — reusable prompt templates

The exam tests whether you know the `FastMCP` API. Here's the minimal structure:

```python
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("server-name")

@mcp.tool()
def my_tool(param: str) -> str:
    return "result"
```

**Note:** This lab shows you the code patterns. To actually run an MCP server, you'd need the `mcp` package installed locally. In this environment, we'll study the code structure.""",
                "starter_code": """# MCP Server — note_manager.py
# This is the code you'd save as a file and run with: python note_manager.py

from mcp.server.fastmcp import FastMCP

# Create the server
mcp = FastMCP("note-manager")

# In-memory storage
notes = {}

# ── Tool: Add a note ──
@mcp.tool()
def add_note(title: str, content: str) -> str:
    \"\"\"Add a new note with a title and content.\"\"\"
    notes[title] = content
    return f"Note '{title}' saved successfully."

# ── Tool: Get a note ──
@mcp.tool()
def get_note(title: str) -> str:
    \"\"\"Retrieve a note by its title.\"\"\"
    if title in notes:
        return notes[title]
    return f"Note '{title}' not found."

# ── Tool: List all notes ──
@mcp.tool()
def list_notes() -> str:
    \"\"\"List all saved note titles.\"\"\"
    if not notes:
        return "No notes saved yet."
    return "\\n".join(f"- {title}" for title in notes)

# ── Resource: Expose notes as readable data ──
@mcp.resource("notes://all")
def all_notes_resource() -> str:
    \"\"\"All notes as a formatted document.\"\"\"
    if not notes:
        return "No notes yet."
    return "\\n\\n".join(f"## {t}\\n{c}" for t, c in notes.items())

# Show what we built (for learning purposes)
print("MCP Server: note-manager")
print(f"Tools defined: add_note, get_note, list_notes")
print(f"Resources defined: notes://all")
print()
print("Tool schemas:")
print("  add_note(title: str, content: str) -> str")
print("  get_note(title: str) -> str")
print("  list_notes() -> str")
print()
print("In production, you'd start this with:")
print("  python note_manager.py")
print("  # or: mcp run note_manager.py")
""",
                "solution_code": """# Same as starter
""",
                "dry_run_output": """MCP Server: note-manager
Tools defined: add_note, get_note, list_notes
Resources defined: notes://all

Tool schemas:
  add_note(title: str, content: str) -> str
  get_note(title: str) -> str
  list_notes() -> str

In production, you'd start this with:
  python note_manager.py
  # or: mcp run note_manager.py""",
                "exam_tips": [
                    "MCP tools use Python type hints for the input schema — `def my_tool(name: str, count: int)` auto-generates the JSON schema. The exam tests this.",
                    "The `@mcp.tool()` decorator is the correct way to define tools. The exam may show manual schema definition as a distractor.",
                    "`FastMCP` is the high-level API. The exam won't test the low-level protocol details."
                ],
                "hints": ["The docstring on each tool becomes the tool's description that Claude sees."]
            },
            {
                "id": 2,
                "title": "Tool Input Validation",
                "language": "python",
                "instruction": """## Tool Input Validation

Good MCP tools validate their inputs and return clear error messages. The exam specifically tests:
- Type annotations for auto-generated schemas
- Using `Annotated` types for descriptions and constraints
- Returning structured errors vs. raising exceptions

Key rule: **MCP tools should return error strings, not raise exceptions.** The model needs to see the error message to try again.""",
                "starter_code": """from typing import Annotated

# Simulating MCP tool definitions — these patterns are what the exam tests

def create_user(
    name: Annotated[str, "The user's full name"],
    email: Annotated[str, "Valid email address"],
    age: Annotated[int, "Age in years, must be 0-150"],
) -> str:
    \"\"\"Create a new user account with validation.\"\"\"

    # Validate inputs (MCP tools should validate, not assume)
    errors = []
    if not name or len(name.strip()) < 2:
        errors.append("Name must be at least 2 characters")
    if "@" not in email or "." not in email:
        errors.append(f"Invalid email: {email}")
    if not (0 <= age <= 150):
        errors.append(f"Age must be 0-150, got {age}")

    if errors:
        # Return error string — do NOT raise an exception
        return f"Validation failed: {'; '.join(errors)}"

    # Success
    return f"User created: {name} ({email}), age {age}"


# Test with valid input
print("Test 1 (valid):")
print(f"  {create_user('Alice Smith', 'alice@example.com', 30)}")
print()

# Test with invalid input
print("Test 2 (invalid email):")
print(f"  {create_user('Bob', 'not-an-email', 25)}")
print()

print("Test 3 (invalid age):")
print(f"  {create_user('Charlie', 'charlie@test.com', -5)}")
print()

# Show the auto-generated schema concept
print("Schema auto-generated from type hints:")
print("  name: string ('The user\\'s full name')")
print("  email: string ('Valid email address')")
print("  age: integer ('Age in years, must be 0-150')")
print()
print("Key exam point: Annotated[type, description] provides")
print("BOTH the type and the description for the JSON schema.")
""",
                "solution_code": """# Same as starter
""",
                "dry_run_output": """Test 1 (valid):
  User created: Alice Smith (alice@example.com), age 30

Test 2 (invalid email):
  Validation failed: Invalid email: not-an-email

Test 3 (invalid age):
  Validation failed: Age must be 0-150, got -5

Schema auto-generated from type hints:
  name: string ('The user\\'s full name')
  email: string ('Valid email address')
  age: integer ('Age in years, must be 0-150')

Key exam point: Annotated[type, description] provides
BOTH the type and the description for the JSON schema.""",
                "exam_tips": [
                    "MCP tools should RETURN error strings, not RAISE exceptions. The model sees return values — it can't catch your exceptions.",
                    "`Annotated[str, 'description']` is the correct way to add descriptions to MCP tool parameters. The exam tests this pattern.",
                    "Input validation belongs in the tool function, not in a prompt instruction telling Claude to 'validate before calling'."
                ],
                "hints": []
            },
            {
                "id": 3,
                "title": "MCP Resources & Prompts",
                "language": "python",
                "instruction": """## MCP Resources & Prompts

Beyond tools, MCP servers expose two other primitives:

**Resources** — Read-only data the model can access. Think of them as GET endpoints.
- Static: `@mcp.resource("config://app")` — fixed URI
- Dynamic: `@mcp.resource("users://{user_id}")` — templated URI

**Prompts** — Reusable prompt templates the client can request.
- `@mcp.prompt()` — returns a list of messages

The exam tests whether you know when to use each:
- **Tool** → action with side effects (create, update, delete)
- **Resource** → read-only data retrieval
- **Prompt** → reusable prompt template""",
                "starter_code": """# MCP Resources & Prompts — exam-relevant patterns

# ── Resources: Read-only data ──
# Static resource — fixed content
# @mcp.resource("config://database")
def database_config():
    \"\"\"Database connection configuration.\"\"\"
    return \"\"\"
    host: db.example.com
    port: 5432
    database: production
    ssl: true
    \"\"\"

# Dynamic resource — URI with parameters
# @mcp.resource("users://{user_id}/profile")
def user_profile(user_id: str):
    \"\"\"Fetch a user's profile by ID.\"\"\"
    profiles = {
        "u001": {"name": "Alice", "role": "admin"},
        "u002": {"name": "Bob", "role": "viewer"},
    }
    import json
    return json.dumps(profiles.get(user_id, {"error": "Not found"}))


# ── Prompts: Reusable templates ──
# @mcp.prompt()
def code_review(language: str, code: str):
    \"\"\"Generate a code review prompt.\"\"\"
    return [
        {
            "role": "user",
            "content": f"Review this {language} code for bugs, security issues, and style:\\n\\n```{language}\\n{code}\\n```"
        }
    ]


# Demo
print("=== MCP Primitives ===\\n")

print("1. RESOURCES (read-only data):")
print(f"   Static:  config://database")
print(f"   Content: {database_config().strip()[:50]}...")
print(f"   Dynamic: users://u001/profile")
print(f"   Content: {user_profile('u001')}")
print()

print("2. PROMPTS (reusable templates):")
review = code_review("python", "x = eval(input())")
print(f"   Template: code_review(language, code)")
print(f"   Output:   {review[0]['content'][:60]}...")
print()

print("3. When to use each (EXAM KEY):")
print("   Tool     → has side effects (create, update, delete)")
print("   Resource → read-only data retrieval")
print("   Prompt   → reusable prompt template")
""",
                "solution_code": """# Same as starter
""",
                "dry_run_output": """=== MCP Primitives ===

1. RESOURCES (read-only data):
   Static:  config://database
   Content:     host: db.example.com
    port: 5432...
   Dynamic: users://u001/profile
   Content: {"name": "Alice", "role": "admin"}

2. PROMPTS (reusable templates):
   Template: code_review(language, code)
   Output:   Review this python code for bugs, security issues, and...

3. When to use each (EXAM KEY):
   Tool     → has side effects (create, update, delete)
   Resource → read-only data retrieval
   Prompt   → reusable prompt template""",
                "exam_tips": [
                    "⚠️ KEY DISTINCTION: If it CHANGES data → Tool. If it only READS data → Resource. The exam will try to trick you into using a tool for read-only operations.",
                    "Resources use URI templates like `users://{id}`. The exam will show both static and dynamic resource URIs.",
                    "Prompts return a list of message dicts, NOT a plain string. Each message has `role` and `content`."
                ],
                "hints": []
            },
        ],
        "challenge": {
            "title": "Build a Database MCP Server",
            "description": "Create an MCP server for a SQLite database with: a tool to run queries, a resource for the schema, and a prompt for query generation.",
            "requirements": [
                "Tool: execute_query(sql: str) — runs a SQL query",
                "Resource: schema://tables — returns table schemas",
                "Prompt: generate_query(question: str) — creates a SQL prompt",
                "Include input validation on the SQL tool"
            ]
        },
    },

    # ══════════════════════════════════════════════════════════════
    # LAB 2.2 — MCP Client & Tool Discovery
    # ══════════════════════════════════════════════════════════════
    {
        "id": "2.2",
        "domain": 2,
        "domain_name": "Tool Design & MCP Integration",
        "title": "MCP Client & Tool Discovery",
        "description": "Build a client that connects to MCP servers, discovers their tools, and converts them to Claude API tool schemas.",
        "difficulty": "intermediate",
        "estimated_time": "30 min",
        "task_statements": ["2.4", "2.5"],
        "steps": [
            {
                "id": 1,
                "title": "MCP to Claude Tool Conversion",
                "language": "python",
                "instruction": """## MCP to Claude Tool Conversion

When an MCP client connects to a server, it discovers the server's tools. Each MCP tool has:
- `name` — the function name
- `description` — what it does
- `inputSchema` — JSON Schema for parameters

These map directly to Claude's tool format. The exam tests whether you can convert between them.

MCP format → Claude API format:
```
MCP:    {"name": "x", "description": "y", "inputSchema": {...}}
Claude: {"name": "x", "description": "y", "input_schema": {...}}
```

Notice: `inputSchema` (camelCase) → `input_schema` (snake_case).""",
                "starter_code": """import json

# Simulated MCP tool discovery response
# This is what you get when you call client.list_tools()
mcp_tools = [
    {
        "name": "search_files",
        "description": "Search for files matching a pattern.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "Glob pattern"},
                "directory": {"type": "string", "description": "Root directory"}
            },
            "required": ["pattern"]
        }
    },
    {
        "name": "read_file",
        "description": "Read the contents of a file.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path to read"}
            },
            "required": ["path"]
        }
    },
    {
        "name": "write_file",
        "description": "Write content to a file.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path"},
                "content": {"type": "string", "description": "Content to write"}
            },
            "required": ["path", "content"]
        }
    }
]

def mcp_to_claude_tools(mcp_tools: list) -> list:
    \"\"\"Convert MCP tool definitions to Claude API format.\"\"\"
    claude_tools = []
    for tool in mcp_tools:
        claude_tools.append({
            "name": tool["name"],
            "description": tool["description"],
            # Key conversion: inputSchema → input_schema
            "input_schema": tool["inputSchema"],
        })
    return claude_tools

# Convert
claude_tools = mcp_to_claude_tools(mcp_tools)

print("=== MCP Tools Discovered ===")
for t in mcp_tools:
    params = list(t["inputSchema"]["properties"].keys())
    print(f"  {t['name']}({', '.join(params)})")

print()
print("=== Converted to Claude Format ===")
print(json.dumps(claude_tools, indent=2))
print()
print("Key difference: inputSchema (MCP) → input_schema (Claude)")
""",
                "solution_code": """# Same as starter
""",
                "dry_run_output": """=== MCP Tools Discovered ===
  search_files(pattern, directory)
  read_file(path)
  write_file(path, content)

=== Converted to Claude Format ===
[
  {
    "name": "search_files",
    "description": "Search for files matching a pattern.",
    "input_schema": {
      "type": "object",
      "properties": {
        "pattern": {"type": "string", "description": "Glob pattern"},
        "directory": {"type": "string", "description": "Root directory"}
      },
      "required": ["pattern"]
    }
  },
  ...
]

Key difference: inputSchema (MCP) → input_schema (Claude)""",
                "exam_tips": [
                    "⚠️ COMMON TRAP: MCP uses `inputSchema` (camelCase), Claude API uses `input_schema` (snake_case). The exam shows answers that forget to convert — those are wrong.",
                    "MCP tool discovery is dynamic — the client doesn't hardcode which tools exist. It calls `list_tools()` at connection time.",
                    "The conversion is 1:1 except for the key name. Don't add or remove properties during conversion."
                ],
                "hints": []
            },
            {
                "id": 2,
                "title": "Claude Code MCP Configuration",
                "language": "json",
                "instruction": """## Claude Code MCP Configuration

Claude Code connects to MCP servers via a configuration file. The exam tests whether you know the correct format.

MCP servers are configured in `.claude/settings.json` or project-level settings. The two transport types:
- **stdio** — local process, communicates via stdin/stdout
- **sse** — remote server, communicates via HTTP Server-Sent Events

This step shows the configuration patterns the exam asks about.""",
                "starter_code": """{
  "mcpServers": {
    "note-manager": {
      "command": "python",
      "args": ["./mcp_servers/note_manager.py"],
      "env": {
        "DATABASE_URL": "sqlite:///notes.db"
      }
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "remote-api": {
      "url": "https://api.example.com/mcp",
      "headers": {
        "Authorization": "Bearer ${API_KEY}"
      }
    }
  }
}
""",
                "solution_code": """// Same as starter — this is the reference configuration
""",
                "dry_run_output": """MCP Server Configuration Reference:

STDIO transport (local process):
  "server-name": {
    "command": "python",          // executable
    "args": ["./server.py"],      // arguments
    "env": { "KEY": "value" }     // environment variables
  }

SSE transport (remote server):
  "server-name": {
    "url": "https://...",         // server URL
    "headers": { ... }           // auth headers
  }

Key exam points:
  ✓ stdio = local process (command + args)
  ✓ sse = remote HTTP (url + headers)
  ✓ env vars use ${VAR_NAME} syntax
  ✓ Config lives in .claude/settings.json""",
                "exam_tips": [
                    "stdio transport uses `command` + `args`. SSE transport uses `url`. The exam will mix these up in wrong answers.",
                    "Environment variables in MCP config use `${VAR_NAME}` syntax — not `$VAR_NAME` or `%VAR_NAME%`.",
                    "MCP servers configured at project level are available only in that project. User-level config applies everywhere."
                ],
                "hints": []
            },
        ],
        "challenge": None,
    },
]
