"""Domain 1: Agentic Architecture & Orchestration (27%) — Labs 1.1–1.3"""

LABS = [
    # ══════════════════════════════════════════════════════════════
    # LAB 1.1 — Basic Tool-Use Loop
    # ══════════════════════════════════════════════════════════════
    {
        "id": "1.1",
        "domain": 1,
        "domain_name": "Agentic Architecture & Orchestration",
        "title": "Building a Basic Tool-Use Loop",
        "description": "Learn the core agentic pattern: send a message, check stop_reason, call a tool, feed the result back, and loop until Claude says it's done.",
        "difficulty": "beginner",
        "estimated_time": "30 min",
        "task_statements": ["1.1", "1.2", "1.3"],
        "steps": [
            {
                "id": 1,
                "title": "Your First API Call",
                "language": "python",
                "instruction": """## Your First API Call

We'll start at the foundation: sending a single message to Claude via the API and inspecting what comes back.

The response object has a specific structure that the exam tests heavily. Pay attention to:
- `response.content` — a **list** of content blocks (not a string)
- `response.stop_reason` — tells you **why** Claude stopped generating
- `response.model` — the model that served the request
- `response.usage` — input and output token counts

Run this code and study the output. Notice that `content` is a list with one `TextBlock` inside it.""",
                "starter_code": """import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=256,
    messages=[
        {"role": "user", "content": "What is the capital of France? Answer in one sentence."}
    ]
)

print("=== Full Response ===")
print(f"Model:       {response.model}")
print(f"Stop reason: {response.stop_reason}")
print(f"Usage:       {response.usage.input_tokens} in / {response.usage.output_tokens} out")
print()
print("=== Content Blocks ===")
for i, block in enumerate(response.content):
    print(f"  [{i}] type={block.type}")
    if block.type == "text":
        print(f"      text={block.text}")
""",
                "solution_code": """import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=256,
    messages=[
        {"role": "user", "content": "What is the capital of France? Answer in one sentence."}
    ]
)

print("=== Full Response ===")
print(f"Model:       {response.model}")
print(f"Stop reason: {response.stop_reason}")
print(f"Usage:       {response.usage.input_tokens} in / {response.usage.output_tokens} out")
print()
print("=== Content Blocks ===")
for i, block in enumerate(response.content):
    print(f"  [{i}] type={block.type}")
    if block.type == "text":
        print(f"      text={block.text}")
""",
                "dry_run_output": """=== Full Response ===
Model:       claude-haiku-4-5-20251001
Stop reason: end_turn
Usage:       18 in / 15 out

=== Content Blocks ===
  [0] type=text
      text=The capital of France is Paris, located along the Seine River in the north-central part of the country.""",
                "exam_tips": [
                    "The exam will ask what `stop_reason` is when Claude finishes normally — the answer is `end_turn`, not `stop` or `complete`.",
                    "`response.content` is always a LIST of blocks, never a plain string. Forgetting this causes AttributeError in real code."
                ],
                "hints": ["Make sure your ANTHROPIC_API_KEY is set in the .env file. In dry-run mode, you'll see simulated output."]
            },
            {
                "id": 2,
                "title": "Defining Tools",
                "language": "python",
                "instruction": """## Defining Tools

Now we give Claude a **tool** it can call. Tools are defined as JSON schemas passed in the `tools` parameter.

When Claude decides it needs to use a tool, something changes in the response:
- `stop_reason` becomes `"tool_use"` instead of `"end_turn"`
- `content` contains a `ToolUseBlock` with the tool name and input

Your job in this step: define a `get_weather` tool and ask Claude a question that will make it want to call that tool.

Study the response carefully — notice how `stop_reason` changed and a new block type appeared.""",
                "starter_code": """import anthropic
import json

client = anthropic.Anthropic()

# Define a tool that Claude can call
tools = [
    {
        "name": "get_weather",
        "description": "Get the current weather for a given city.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The city name, e.g. 'London'"
                }
            },
            "required": ["city"]
        }
    }
]

response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=1024,
    tools=tools,
    messages=[
        {"role": "user", "content": "What's the weather like in Tokyo right now?"}
    ]
)

print(f"Stop reason: {response.stop_reason}")
print()
for i, block in enumerate(response.content):
    print(f"Block [{i}]: type={block.type}")
    if block.type == "text":
        print(f"  text: {block.text}")
    elif block.type == "tool_use":
        print(f"  tool:  {block.name}")
        print(f"  id:    {block.id}")
        print(f"  input: {json.dumps(block.input, indent=2)}")
""",
                "solution_code": """import anthropic
import json

client = anthropic.Anthropic()

tools = [
    {
        "name": "get_weather",
        "description": "Get the current weather for a given city.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The city name, e.g. 'London'"
                }
            },
            "required": ["city"]
        }
    }
]

response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=1024,
    tools=tools,
    messages=[
        {"role": "user", "content": "What's the weather like in Tokyo right now?"}
    ]
)

print(f"Stop reason: {response.stop_reason}")
print()
for i, block in enumerate(response.content):
    print(f"Block [{i}]: type={block.type}")
    if block.type == "text":
        print(f"  text: {block.text}")
    elif block.type == "tool_use":
        print(f"  tool:  {block.name}")
        print(f"  id:    {block.id}")
        print(f"  input: {json.dumps(block.input, indent=2)}")
""",
                "dry_run_output": """Stop reason: tool_use

Block [0]: type=text
  text: I'll check the current weather in Tokyo for you.
Block [1]: type=tool_use
  tool:  get_weather
  id:    toolu_01A2B3C4D5E6F7
  input: {
    "city": "Tokyo"
  }""",
                "exam_tips": [
                    "When Claude wants to call a tool, `stop_reason` is `tool_use` — NOT `tool_call` or `function_call` (those are OpenAI terms).",
                    "Each tool-use block has a unique `id` — you MUST send this back in the tool result. Forgetting the id is a common exam trap.",
                    "The `input_schema` must be a valid JSON Schema object. The exam may show malformed schemas as wrong answers."
                ],
                "hints": ["Notice that content may have BOTH a TextBlock and a ToolUseBlock — Claude can think out loud before calling a tool."]
            },
            {
                "id": 3,
                "title": "Feeding Tool Results Back",
                "language": "python",
                "instruction": """## Feeding Tool Results Back

Claude asked to call `get_weather` — now you need to:
1. Extract the tool name, input, and `id` from the response
2. Execute the tool yourself (simulate it for now)
3. Send the result back as a `tool_result` content block
4. Let Claude use the result to answer the original question

The key structure: you send a message with `role: "user"` containing a `tool_result` block that references the original tool-use `id`.

**This is the pattern the exam tests more than any other.**""",
                "starter_code": """import anthropic
import json

client = anthropic.Anthropic()

tools = [
    {
        "name": "get_weather",
        "description": "Get the current weather for a given city.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name"}
            },
            "required": ["city"]
        }
    }
]

# Step 1: Initial request
messages = [{"role": "user", "content": "What's the weather in Tokyo?"}]

response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=1024,
    tools=tools,
    messages=messages,
)

print("── Step 1: Claude wants to call a tool ──")
print(f"Stop reason: {response.stop_reason}")

# Step 2: Extract the tool call
tool_block = None
for block in response.content:
    if block.type == "tool_use":
        tool_block = block
        break

print(f"Tool: {tool_block.name}({tool_block.input})")
print(f"ID:   {tool_block.id}")

# Step 3: Simulate executing the tool
def get_weather(city: str) -> str:
    # In a real app, this calls a weather API
    return json.dumps({"city": city, "temp": "22°C", "condition": "Partly cloudy"})

tool_result = get_weather(tool_block.input["city"])
print(f"\\n── Step 2: Tool returned ──")
print(f"Result: {tool_result}")

# Step 4: Send the result back to Claude
# TODO: Add the assistant's response and the tool result to messages,
#       then make another API call.
#
# Hint: You need TWO new messages:
#   1. {"role": "assistant", "content": response.content}
#   2. {"role": "user", "content": [{"type": "tool_result", ...}]}

messages.append({"role": "assistant", "content": response.content})
messages.append({
    "role": "user",
    "content": [
        {
            "type": "tool_result",
            "tool_use_id": tool_block.id,    # Must match!
            "content": tool_result,
        }
    ],
})

final = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=1024,
    tools=tools,
    messages=messages,
)

print(f"\\n── Step 3: Claude's final answer ──")
print(f"Stop reason: {final.stop_reason}")
for block in final.content:
    if block.type == "text":
        print(block.text)
""",
                "solution_code": """import anthropic
import json

client = anthropic.Anthropic()

tools = [
    {
        "name": "get_weather",
        "description": "Get the current weather for a given city.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name"}
            },
            "required": ["city"]
        }
    }
]

messages = [{"role": "user", "content": "What's the weather in Tokyo?"}]

response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=1024,
    tools=tools,
    messages=messages,
)

print("── Step 1: Claude wants to call a tool ──")
print(f"Stop reason: {response.stop_reason}")

tool_block = None
for block in response.content:
    if block.type == "tool_use":
        tool_block = block
        break

print(f"Tool: {tool_block.name}({tool_block.input})")
print(f"ID:   {tool_block.id}")

def get_weather(city: str) -> str:
    return json.dumps({"city": city, "temp": "22°C", "condition": "Partly cloudy"})

tool_result = get_weather(tool_block.input["city"])
print(f"\\n── Step 2: Tool returned ──")
print(f"Result: {tool_result}")

messages.append({"role": "assistant", "content": response.content})
messages.append({
    "role": "user",
    "content": [
        {
            "type": "tool_result",
            "tool_use_id": tool_block.id,
            "content": tool_result,
        }
    ],
})

final = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=1024,
    tools=tools,
    messages=messages,
)

print(f"\\n── Step 3: Claude's final answer ──")
print(f"Stop reason: {final.stop_reason}")
for block in final.content:
    if block.type == "text":
        print(block.text)
""",
                "dry_run_output": """── Step 1: Claude wants to call a tool ──
Stop reason: tool_use
Tool: get_weather({'city': 'Tokyo'})
ID:   toolu_01A2B3C4D5E6F7

── Step 2: Tool returned ──
Result: {"city": "Tokyo", "temp": "22\\u00b0C", "condition": "Partly cloudy"}

── Step 3: Claude's final answer ──
Stop reason: end_turn
The weather in Tokyo is currently 22°C and partly cloudy. It's a pleasant day — you might want a light jacket if you're heading out in the evening.""",
                "exam_tips": [
                    "The `tool_use_id` in the tool_result MUST match the `id` from the tool_use block. The exam will show answers that forget this — those are always wrong.",
                    "The assistant's full response (including the tool_use block) must be added to messages before the tool_result. Skipping this breaks the conversation history.",
                    "After getting the tool result, Claude's stop_reason should be `end_turn` — if it's still `tool_use`, Claude wants to call another tool."
                ],
                "hints": []
            },
            {
                "id": 4,
                "title": "The Complete Agentic Loop",
                "language": "python",
                "instruction": """## The Complete Agentic Loop

Now we put it all together into a **while loop** that keeps running until Claude is done. This is the pattern every agent uses:

```
while stop_reason == "tool_use":
    1. Extract tool call(s) from response
    2. Execute each tool
    3. Send results back
    4. Get next response
```

This step gives Claude **multiple tools** and asks a question that requires calling more than one. Your loop must handle multiple rounds of tool calls.

**This is THE core exam pattern. If you remember one thing, remember this loop.**""",
                "starter_code": """import anthropic
import json

client = anthropic.Anthropic()

# Two tools this time
tools = [
    {
        "name": "get_weather",
        "description": "Get the current weather for a city.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name"}
            },
            "required": ["city"]
        }
    },
    {
        "name": "get_time",
        "description": "Get the current local time in a city.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name"}
            },
            "required": ["city"]
        }
    }
]

# Simulated tool implementations
def execute_tool(name: str, input_data: dict) -> str:
    if name == "get_weather":
        return json.dumps({"city": input_data["city"], "temp": "22°C", "condition": "Sunny"})
    elif name == "get_time":
        return json.dumps({"city": input_data["city"], "time": "14:30 JST"})
    return json.dumps({"error": f"Unknown tool: {name}"})

# ── The Agentic Loop ──
messages = [
    {"role": "user", "content": "What's the weather AND the current time in Tokyo?"}
]

print("🔄 Starting agentic loop...\\n")
iteration = 0

response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=1024,
    tools=tools,
    messages=messages,
)

while response.stop_reason == "tool_use":
    iteration += 1
    print(f"── Iteration {iteration} ──")

    # Collect ALL tool calls from this response
    tool_results = []
    for block in response.content:
        if block.type == "tool_use":
            print(f"  📞 Calling {block.name}({block.input})")
            result = execute_tool(block.name, block.input)
            print(f"  ✅ Result: {result}")
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": result,
            })

    # Add assistant response + all tool results
    messages.append({"role": "assistant", "content": response.content})
    messages.append({"role": "user", "content": tool_results})

    # Next round
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        tools=tools,
        messages=messages,
    )

print(f"\\n── Done (stop_reason={response.stop_reason}) ──")
for block in response.content:
    if block.type == "text":
        print(block.text)
""",
                "solution_code": """import anthropic
import json

client = anthropic.Anthropic()

tools = [
    {
        "name": "get_weather",
        "description": "Get the current weather for a city.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name"}
            },
            "required": ["city"]
        }
    },
    {
        "name": "get_time",
        "description": "Get the current local time in a city.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name"}
            },
            "required": ["city"]
        }
    }
]

def execute_tool(name: str, input_data: dict) -> str:
    if name == "get_weather":
        return json.dumps({"city": input_data["city"], "temp": "22°C", "condition": "Sunny"})
    elif name == "get_time":
        return json.dumps({"city": input_data["city"], "time": "14:30 JST"})
    return json.dumps({"error": f"Unknown tool: {name}"})

messages = [
    {"role": "user", "content": "What's the weather AND the current time in Tokyo?"}
]

print("🔄 Starting agentic loop...\\n")
iteration = 0

response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=1024,
    tools=tools,
    messages=messages,
)

while response.stop_reason == "tool_use":
    iteration += 1
    print(f"── Iteration {iteration} ──")
    tool_results = []
    for block in response.content:
        if block.type == "tool_use":
            print(f"  📞 Calling {block.name}({block.input})")
            result = execute_tool(block.name, block.input)
            print(f"  ✅ Result: {result}")
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": result,
            })
    messages.append({"role": "assistant", "content": response.content})
    messages.append({"role": "user", "content": tool_results})
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        tools=tools,
        messages=messages,
    )

print(f"\\n── Done (stop_reason={response.stop_reason}) ──")
for block in response.content:
    if block.type == "text":
        print(block.text)
""",
                "dry_run_output": """🔄 Starting agentic loop...

── Iteration 1 ──
  📞 Calling get_weather({'city': 'Tokyo'})
  ✅ Result: {"city": "Tokyo", "temp": "22\\u00b0C", "condition": "Sunny"}
  📞 Calling get_time({'city': 'Tokyo'})
  ✅ Result: {"city": "Tokyo", "time": "14:30 JST"}

── Done (stop_reason=end_turn) ──
Here's what I found for Tokyo:

• **Weather**: It's currently 22°C and sunny — a beautiful day!
• **Time**: The local time is 2:30 PM JST.

Great conditions for exploring the city!""",
                "exam_tips": [
                    "Claude can call MULTIPLE tools in a single response. You must handle ALL of them before sending results back. The exam shows answers that only handle the first tool — those are wrong.",
                    "The loop condition is `while response.stop_reason == 'tool_use'`. NOT `while True` with a manual break — the exam prefers the explicit stop_reason check.",
                    "All tool results for a single round go in ONE user message as a list, not separate messages."
                ],
                "hints": []
            },
            {
                "id": 5,
                "title": "Challenge: Build a Calculator Agent",
                "language": "python",
                "instruction": """## Challenge: Build a Calculator Agent

Now it's your turn. Build an agent with these tools:
- `add(a, b)` — returns a + b
- `multiply(a, b)` — returns a * b
- `subtract(a, b)` — returns a - b

Then ask it: **"What is (15 + 7) × 3 - 10?"**

The agent should call tools in sequence to compute the answer (59).

Requirements:
1. Define all three tools with proper input schemas
2. Implement the tool functions
3. Use the agentic loop pattern from Step 4
4. Print each tool call and the final answer

**No starter code this time — write it from scratch using what you learned.**""",
                "starter_code": """import anthropic
import json

client = anthropic.Anthropic()

# TODO: Define tools (add, multiply, subtract)
tools = []

# TODO: Implement tool execution
def execute_tool(name: str, input_data: dict) -> str:
    pass

# TODO: Build the agentic loop
# Ask: "What is (15 + 7) × 3 - 10?"
""",
                "solution_code": """import anthropic
import json

client = anthropic.Anthropic()

tools = [
    {
        "name": "add",
        "description": "Add two numbers.",
        "input_schema": {
            "type": "object",
            "properties": {
                "a": {"type": "number", "description": "First number"},
                "b": {"type": "number", "description": "Second number"}
            },
            "required": ["a", "b"]
        }
    },
    {
        "name": "multiply",
        "description": "Multiply two numbers.",
        "input_schema": {
            "type": "object",
            "properties": {
                "a": {"type": "number", "description": "First number"},
                "b": {"type": "number", "description": "Second number"}
            },
            "required": ["a", "b"]
        }
    },
    {
        "name": "subtract",
        "description": "Subtract b from a.",
        "input_schema": {
            "type": "object",
            "properties": {
                "a": {"type": "number", "description": "Number to subtract from"},
                "b": {"type": "number", "description": "Number to subtract"}
            },
            "required": ["a", "b"]
        }
    }
]

def execute_tool(name: str, input_data: dict) -> str:
    if name == "add":
        return json.dumps({"result": input_data["a"] + input_data["b"]})
    elif name == "multiply":
        return json.dumps({"result": input_data["a"] * input_data["b"]})
    elif name == "subtract":
        return json.dumps({"result": input_data["a"] - input_data["b"]})
    return json.dumps({"error": f"Unknown tool: {name}"})

messages = [{"role": "user", "content": "What is (15 + 7) × 3 - 10?"}]
response = client.messages.create(model="claude-haiku-4-5-20251001", max_tokens=1024, tools=tools, messages=messages)

iteration = 0
while response.stop_reason == "tool_use":
    iteration += 1
    print(f"── Round {iteration} ──")
    tool_results = []
    for block in response.content:
        if block.type == "tool_use":
            result = execute_tool(block.name, block.input)
            print(f"  {block.name}({block.input}) → {result}")
            tool_results.append({"type": "tool_result", "tool_use_id": block.id, "content": result})
    messages.append({"role": "assistant", "content": response.content})
    messages.append({"role": "user", "content": tool_results})
    response = client.messages.create(model="claude-haiku-4-5-20251001", max_tokens=1024, tools=tools, messages=messages)

print(f"\\nAnswer:")
for block in response.content:
    if block.type == "text":
        print(block.text)
""",
                "dry_run_output": """── Round 1 ──
  add({'a': 15, 'b': 7}) → {"result": 22}
── Round 2 ──
  multiply({'a': 22, 'b': 3}) → {"result": 66}
── Round 3 ──
  subtract({'a': 66, 'b': 10}) → {"result": 56}

Answer:
The result of (15 + 7) × 3 - 10 = **56**.

Here's how I calculated it step by step:
1. 15 + 7 = 22
2. 22 × 3 = 66
3. 66 - 10 = 56""",
                "exam_tips": [
                    "The exam loves multi-step tool-call scenarios. Make sure your loop handles sequential tool calls across multiple iterations — not just parallel calls in one round."
                ],
                "hints": ["Each tool needs `type: 'object'` in input_schema with `properties` and `required`."]
            },
        ],
        "challenge": {
            "title": "Build a File-Search Agent",
            "description": "Create an agent with search_files, read_file, and summarize tools. Ask it to find and summarize all Python files in a directory.",
            "requirements": [
                "Define three tools with proper schemas",
                "Implement simulated tool functions",
                "Handle multi-round tool calls",
                "Agent should stop when it has enough information"
            ]
        }
    },

    # ══════════════════════════════════════════════════════════════
    # LAB 1.2 — Multi-Agent Handoff
    # ══════════════════════════════════════════════════════════════
    {
        "id": "1.2",
        "domain": 1,
        "domain_name": "Agentic Architecture & Orchestration",
        "title": "Multi-Agent Handoff",
        "description": "Build a router agent that delegates to specialist agents based on the user's request — the orchestration pattern tested in exam scenario 3.",
        "difficulty": "intermediate",
        "estimated_time": "40 min",
        "task_statements": ["1.4", "1.5", "1.6"],
        "steps": [
            {
                "id": 1,
                "title": "Single-Purpose Specialist Agent",
                "language": "python",
                "instruction": """## Single-Purpose Specialist Agent

Before building multi-agent systems, let's create a clean **agent function** — a reusable unit that takes a task, runs an agentic loop, and returns a result.

This is how real multi-agent systems work: each specialist is a function that encapsulates its own tools and conversation.""",
                "starter_code": """import anthropic
import json

client = anthropic.Anthropic()

def math_agent(question: str) -> str:
    \"\"\"A specialist agent that answers math questions using calculator tools.\"\"\"
    tools = [
        {
            "name": "calculate",
            "description": "Evaluate a mathematical expression.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "Math expression, e.g. '2 + 3 * 4'"}
                },
                "required": ["expression"]
            }
        }
    ]

    def execute_tool(name, input_data):
        if name == "calculate":
            try:
                result = eval(input_data["expression"])  # Safe for math only
                return json.dumps({"result": result})
            except Exception as e:
                return json.dumps({"error": str(e)})
        return json.dumps({"error": "Unknown tool"})

    messages = [{"role": "user", "content": question}]
    response = client.messages.create(
        model="claude-haiku-4-5-20251001", max_tokens=1024,
        tools=tools, messages=messages,
        system="You are a math specialist. Use the calculate tool for any computation."
    )

    while response.stop_reason == "tool_use":
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = execute_tool(block.name, block.input)
                tool_results.append({"type": "tool_result", "tool_use_id": block.id, "content": result})
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})
        response = client.messages.create(
            model="claude-haiku-4-5-20251001", max_tokens=1024,
            tools=tools, messages=messages,
            system="You are a math specialist. Use the calculate tool for any computation."
        )

    return next((b.text for b in response.content if b.type == "text"), "No answer")


# Test the specialist
answer = math_agent("What is 42 * 17 + 89?")
print(f"Math Agent says: {answer}")
""",
                "solution_code": """import anthropic
import json

client = anthropic.Anthropic()

def math_agent(question: str) -> str:
    tools = [
        {
            "name": "calculate",
            "description": "Evaluate a mathematical expression.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "Math expression"}
                },
                "required": ["expression"]
            }
        }
    ]

    def execute_tool(name, input_data):
        if name == "calculate":
            try:
                return json.dumps({"result": eval(input_data["expression"])})
            except Exception as e:
                return json.dumps({"error": str(e)})
        return json.dumps({"error": "Unknown tool"})

    messages = [{"role": "user", "content": question}]
    response = client.messages.create(
        model="claude-haiku-4-5-20251001", max_tokens=1024,
        tools=tools, messages=messages,
        system="You are a math specialist. Use the calculate tool for any computation."
    )

    while response.stop_reason == "tool_use":
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = execute_tool(block.name, block.input)
                tool_results.append({"type": "tool_result", "tool_use_id": block.id, "content": result})
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})
        response = client.messages.create(
            model="claude-haiku-4-5-20251001", max_tokens=1024,
            tools=tools, messages=messages,
            system="You are a math specialist. Use the calculate tool for any computation."
        )

    return next((b.text for b in response.content if b.type == "text"), "No answer")

answer = math_agent("What is 42 * 17 + 89?")
print(f"Math Agent says: {answer}")
""",
                "dry_run_output": """Math Agent says: 42 × 17 + 89 = **803**. I calculated 42 × 17 = 714, then added 89 to get 803.""",
                "exam_tips": [
                    "Each specialist agent should have its own system prompt, tools, and conversation history — don't share these across agents.",
                    "The exam tests whether you know that the `system` parameter is separate from `messages` — it's NOT the first message."
                ],
                "hints": []
            },
            {
                "id": 2,
                "title": "Router Agent Pattern",
                "language": "python",
                "instruction": """## Router Agent Pattern

Now build a **router** that decides which specialist to call. The router itself is a Claude call that picks the right agent.

The pattern:
1. Router agent classifies the request
2. Routes to the correct specialist via a `transfer_to_agent` tool
3. Specialist runs and returns the answer
4. Router presents the answer to the user

This maps directly to exam Scenario 3 (Multi-Agent Research System).""",
                "starter_code": """import anthropic
import json

client = anthropic.Anthropic()

# ── Specialist Agents ──
def math_agent(question: str) -> str:
    \"\"\"Handles math questions.\"\"\"
    # (Simplified — uses the pattern from Step 1)
    response = client.messages.create(
        model="claude-haiku-4-5-20251001", max_tokens=512,
        messages=[{"role": "user", "content": question}],
        system="You are a math expert. Solve the problem step by step. Give the final number."
    )
    return next((b.text for b in response.content if b.type == "text"), "")

def writing_agent(question: str) -> str:
    \"\"\"Handles writing tasks.\"\"\"
    response = client.messages.create(
        model="claude-haiku-4-5-20251001", max_tokens=512,
        messages=[{"role": "user", "content": question}],
        system="You are a concise writing expert. Keep responses under 3 sentences."
    )
    return next((b.text for b in response.content if b.type == "text"), "")

AGENTS = {"math_agent": math_agent, "writing_agent": writing_agent}

# ── Router ──
router_tools = [
    {
        "name": "transfer_to_agent",
        "description": "Route the user's request to the right specialist agent.",
        "input_schema": {
            "type": "object",
            "properties": {
                "agent": {
                    "type": "string",
                    "enum": ["math_agent", "writing_agent"],
                    "description": "Which specialist to route to"
                },
                "task": {
                    "type": "string",
                    "description": "The task to give the specialist"
                }
            },
            "required": ["agent", "task"]
        }
    }
]

def route_request(user_input: str) -> str:
    messages = [{"role": "user", "content": user_input}]
    response = client.messages.create(
        model="claude-haiku-4-5-20251001", max_tokens=1024,
        tools=router_tools, messages=messages,
        system="You are a router. Decide which agent should handle this request and transfer to it."
    )

    if response.stop_reason == "tool_use":
        for block in response.content:
            if block.type == "tool_use" and block.name == "transfer_to_agent":
                agent_name = block.input["agent"]
                task = block.input["task"]
                print(f"  🔀 Router → {agent_name}")
                print(f"  📝 Task: {task}")
                # Call the specialist
                result = AGENTS[agent_name](task)
                return result

    return next((b.text for b in response.content if b.type == "text"), "Could not route")

# ── Test ──
queries = [
    "What's 2^10 minus 24?",
    "Write a haiku about Python programming",
]

for q in queries:
    print(f"\\n{'='*50}")
    print(f"User: {q}")
    answer = route_request(q)
    print(f"Answer: {answer}")
""",
                "solution_code": """# (Same as starter — this step is about understanding the pattern)
""",
                "dry_run_output": """==================================================
User: What's 2^10 minus 24?
  🔀 Router → math_agent
  📝 Task: Calculate 2^10 minus 24
Answer: 2^10 = 1024, and 1024 - 24 = **1000**.

==================================================
User: Write a haiku about Python programming
  🔀 Router → writing_agent
  📝 Task: Write a haiku about Python programming
Answer: Indentation deep,
Lists and dicts flow like water—
ImportError. Sigh.""",
                "exam_tips": [
                    "The exam tests the router/specialist pattern heavily in Scenario 3. The router uses a tool to delegate — NOT a prompt that says 'act as agent X'.",
                    "Each specialist has its own system prompt and tools — the router doesn't share its tools with specialists.",
                    "Using an `enum` in the tool schema for agent names prevents the router from inventing agents that don't exist."
                ],
                "hints": []
            },
            {
                "id": 3,
                "title": "Challenge: Add Error Handling to the Router",
                "language": "python",
                "instruction": """## Challenge: Improve the Router

Extend the router from Step 2 with:
1. **Fallback handling** — if no specialist matches, the router answers directly
2. **Error handling** — if a specialist fails, the router retries or apologises
3. **A third specialist** — add a `code_agent` that writes Python code

Test with: "Write a Python function that calculates the Fibonacci sequence"

This teaches you the resilience patterns the exam tests in Domain 1.""",
                "starter_code": """import anthropic
import json

client = anthropic.Anthropic()

# TODO: Add a code_agent specialist
# TODO: Add fallback handling when no agent matches
# TODO: Add try/except around specialist calls

def math_agent(question: str) -> str:
    response = client.messages.create(
        model="claude-haiku-4-5-20251001", max_tokens=512,
        messages=[{"role": "user", "content": question}],
        system="You are a math expert. Solve step by step."
    )
    return next((b.text for b in response.content if b.type == "text"), "")

def writing_agent(question: str) -> str:
    response = client.messages.create(
        model="claude-haiku-4-5-20251001", max_tokens=512,
        messages=[{"role": "user", "content": question}],
        system="You are a writing expert. Be concise."
    )
    return next((b.text for b in response.content if b.type == "text"), "")

# TODO: def code_agent(question: str) -> str: ...

AGENTS = {
    "math_agent": math_agent,
    "writing_agent": writing_agent,
    # TODO: "code_agent": code_agent,
}

# TODO: Build router with fallback + error handling
""",
                "solution_code": """import anthropic
import json

client = anthropic.Anthropic()

def math_agent(question: str) -> str:
    response = client.messages.create(
        model="claude-haiku-4-5-20251001", max_tokens=512,
        messages=[{"role": "user", "content": question}],
        system="You are a math expert. Solve step by step."
    )
    return next((b.text for b in response.content if b.type == "text"), "")

def writing_agent(question: str) -> str:
    response = client.messages.create(
        model="claude-haiku-4-5-20251001", max_tokens=512,
        messages=[{"role": "user", "content": question}],
        system="You are a writing expert. Be concise."
    )
    return next((b.text for b in response.content if b.type == "text"), "")

def code_agent(question: str) -> str:
    response = client.messages.create(
        model="claude-haiku-4-5-20251001", max_tokens=1024,
        messages=[{"role": "user", "content": question}],
        system="You are a Python expert. Write clean, well-commented code."
    )
    return next((b.text for b in response.content if b.type == "text"), "")

AGENTS = {"math_agent": math_agent, "writing_agent": writing_agent, "code_agent": code_agent}

router_tools = [{
    "name": "transfer_to_agent",
    "description": "Route to a specialist agent.",
    "input_schema": {
        "type": "object",
        "properties": {
            "agent": {"type": "string", "enum": list(AGENTS.keys())},
            "task": {"type": "string"}
        },
        "required": ["agent", "task"]
    }
}]

def route_request(user_input: str) -> str:
    messages = [{"role": "user", "content": user_input}]
    response = client.messages.create(
        model="claude-haiku-4-5-20251001", max_tokens=1024,
        tools=router_tools, messages=messages,
        system="Route to the best specialist. If none fits, answer directly."
    )

    if response.stop_reason == "tool_use":
        for block in response.content:
            if block.type == "tool_use" and block.name == "transfer_to_agent":
                agent_name = block.input["agent"]
                task = block.input["task"]
                print(f"  🔀 Router → {agent_name}")
                try:
                    return AGENTS[agent_name](task)
                except Exception as e:
                    print(f"  ❌ Agent failed: {e}")
                    return f"Sorry, the {agent_name} encountered an error. Please try again."

    # Fallback: router answers directly
    print("  💬 Router answering directly (no specialist matched)")
    return next((b.text for b in response.content if b.type == "text"), "I couldn't help with that.")

queries = [
    "What's 2^10 minus 24?",
    "Write a Python function for Fibonacci",
    "What's the meaning of life?",  # Should fallback
]

for q in queries:
    print(f"\\nUser: {q}")
    print(f"Answer: {route_request(q)}")
""",
                "dry_run_output": """User: What's 2^10 minus 24?
  🔀 Router → math_agent
Answer: 2^10 = 1024, so 1024 - 24 = **1000**.

User: Write a Python function for Fibonacci
  🔀 Router → code_agent
Answer: Here's a clean Fibonacci implementation:

```python
def fibonacci(n: int) -> list[int]:
    if n <= 0: return []
    if n == 1: return [0]
    seq = [0, 1]
    for _ in range(2, n):
        seq.append(seq[-1] + seq[-2])
    return seq
```

User: What's the meaning of life?
  💬 Router answering directly (no specialist matched)
Answer: That's a philosophical question best explored through personal reflection. Many find meaning through relationships, purpose, and growth.""",
                "exam_tips": [
                    "Fallback handling (router answers directly when no specialist fits) is a key exam pattern — answers that crash on unroutable requests are always wrong.",
                    "Wrapping specialist calls in try/except is the exam's preferred error handling — not retrying silently or ignoring errors."
                ],
                "hints": []
            },
        ],
        "challenge": None,
    },

    # ══════════════════════════════════════════════════════════════
    # LAB 1.3 — Error Handling & Guardrails
    # ══════════════════════════════════════════════════════════════
    {
        "id": "1.3",
        "domain": 1,
        "domain_name": "Agentic Architecture & Orchestration",
        "title": "Error Handling & Guardrails",
        "description": "Handle API errors, implement retry logic, detect infinite loops, and add guardrails — the reliability patterns the exam loves.",
        "difficulty": "intermediate",
        "estimated_time": "30 min",
        "task_statements": ["1.3", "1.7"],
        "steps": [
            {
                "id": 1,
                "title": "Handling API Errors",
                "language": "python",
                "instruction": """## Handling API Errors

The Claude API can raise several exception types. The exam tests whether you know which ones exist and how to handle them.

Key exceptions from the `anthropic` package:
- `APIError` — base class for all API errors
- `RateLimitError` — you've hit the rate limit (429)
- `APIStatusError` — any non-200 status code
- `APIConnectionError` — network issues

The correct pattern: catch specific errors, not bare `except`.""",
                "starter_code": """import anthropic
import time

client = anthropic.Anthropic()

def resilient_call(messages, max_retries=3):
    \"\"\"Make an API call with exponential backoff retry.\"\"\"
    for attempt in range(max_retries):
        try:
            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=256,
                messages=messages,
            )
            return response

        except anthropic.RateLimitError as e:
            wait = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
            print(f"  ⏳ Rate limited (attempt {attempt+1}/{max_retries}). Waiting {wait}s...")
            time.sleep(wait)

        except anthropic.APIConnectionError as e:
            print(f"  🔌 Connection error (attempt {attempt+1}/{max_retries}): {e}")
            time.sleep(1)

        except anthropic.APIStatusError as e:
            print(f"  ❌ API error {e.status_code}: {e.message}")
            if e.status_code >= 500:
                # Server error — worth retrying
                time.sleep(2 ** attempt)
            else:
                # Client error (400, 401, etc.) — don't retry
                raise

    raise Exception(f"Failed after {max_retries} retries")

# Test
response = resilient_call([{"role": "user", "content": "Say hello in 5 words."}])
print(f"Success: {response.content[0].text}")
""",
                "solution_code": """# Same as starter — this step teaches the error handling pattern
""",
                "dry_run_output": """Success: Hello there, nice to meet!""",
                "exam_tips": [
                    "The exam asks: 'Which errors should you retry?' Answer: RateLimitError and 500-level APIStatusErrors. Do NOT retry 400/401/403.",
                    "Exponential backoff (2^attempt seconds) is the correct retry strategy — not fixed intervals, not immediate retries.",
                    "Catch specific exception types, not bare `except Exception`. The exam marks bare excepts as wrong."
                ],
                "hints": []
            },
            {
                "id": 2,
                "title": "Preventing Infinite Loops",
                "language": "python",
                "instruction": """## Preventing Infinite Loops

An agentic loop can run forever if Claude keeps calling tools without converging. The exam tests this specifically.

Three safeguards:
1. **Max iterations** — hard limit on loop rounds
2. **Max tokens budget** — track cumulative token usage
3. **Duplicate detection** — catch repeated identical tool calls

All three should be code-level checks, NOT prompt instructions.""",
                "starter_code": """import anthropic
import json

client = anthropic.Anthropic()

MAX_ITERATIONS = 10
MAX_TOTAL_TOKENS = 8000

tools = [{
    "name": "lookup",
    "description": "Look up a fact.",
    "input_schema": {
        "type": "object",
        "properties": {"query": {"type": "string"}},
        "required": ["query"]
    }
}]

def execute_tool(name, input_data):
    return json.dumps({"answer": f"Result for: {input_data.get('query', '')}"})

def run_agent_safely(question: str) -> str:
    messages = [{"role": "user", "content": question}]
    total_tokens = 0
    seen_calls = set()

    response = client.messages.create(
        model="claude-haiku-4-5-20251001", max_tokens=1024,
        tools=tools, messages=messages,
    )
    total_tokens += response.usage.input_tokens + response.usage.output_tokens

    iteration = 0
    while response.stop_reason == "tool_use":
        iteration += 1

        # Guard 1: Max iterations
        if iteration > MAX_ITERATIONS:
            print(f"  🛑 Stopped: hit {MAX_ITERATIONS} iteration limit")
            return "I had to stop — too many tool calls. Please try a simpler question."

        # Guard 2: Token budget
        if total_tokens > MAX_TOTAL_TOKENS:
            print(f"  🛑 Stopped: token budget exceeded ({total_tokens} tokens)")
            return "I had to stop — token budget exceeded."

        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                # Guard 3: Duplicate detection
                call_sig = f"{block.name}:{json.dumps(block.input, sort_keys=True)}"
                if call_sig in seen_calls:
                    print(f"  🛑 Stopped: duplicate call detected ({block.name})")
                    return "I noticed I was repeating myself and stopped."
                seen_calls.add(call_sig)

                result = execute_tool(block.name, block.input)
                tool_results.append({"type": "tool_result", "tool_use_id": block.id, "content": result})

        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})

        response = client.messages.create(
            model="claude-haiku-4-5-20251001", max_tokens=1024,
            tools=tools, messages=messages,
        )
        total_tokens += response.usage.input_tokens + response.usage.output_tokens
        print(f"  Iteration {iteration}: {total_tokens} total tokens used")

    return next((b.text for b in response.content if b.type == "text"), "No answer")

print("Agent:", run_agent_safely("What is the capital of Japan?"))
""",
                "solution_code": """# Same as starter
""",
                "dry_run_output": """  Iteration 1: 892 total tokens used
Agent: The capital of Japan is **Tokyo**. It has been the capital since 1868 when the Emperor moved there from Kyoto.""",
                "exam_tips": [
                    "⚠️ KEY TRAP: The exam will show a 'fix' that adds 'do not call the same tool twice' to the prompt. This is WRONG. Use code-level duplicate detection, not prompt instructions.",
                    "All three guardrails (max iterations, token budget, duplicate detection) should be deterministic code checks, not LLM-dependent prompt rules.",
                    "The correct `stop_reason` for a normal completion is `end_turn`. If you see `max_tokens`, the response was truncated — you need to handle that too."
                ],
                "hints": []
            },
            {
                "id": 3,
                "title": "Handling max_tokens Truncation",
                "language": "python",
                "instruction": """## Handling max_tokens Truncation

When Claude's response exceeds `max_tokens`, the `stop_reason` is `"max_tokens"` instead of `"end_turn"`. This means the response was **cut off mid-generation**.

The exam tests what to do here:
- If it's a text response: you might ask Claude to continue
- If it's a tool-use response: the JSON might be invalid — you MUST detect and handle this
- Never silently pass truncated output to the user""",
                "starter_code": """import anthropic

client = anthropic.Anthropic()

# Deliberately set max_tokens very low to trigger truncation
response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=15,  # Very low — will truncate!
    messages=[
        {"role": "user", "content": "Explain quantum computing in detail."}
    ]
)

print(f"Stop reason: {response.stop_reason}")
print(f"Text: {response.content[0].text}")
print()

# The right way to handle this:
if response.stop_reason == "max_tokens":
    print("⚠️  Response was truncated!")
    print("Options:")
    print("  1. Increase max_tokens and retry")
    print("  2. Ask Claude to continue from where it stopped")
    print("  3. Ask for a shorter answer")
    print()
    print("For tool_use responses, truncation means INVALID JSON.")
    print("You must retry with higher max_tokens — do NOT try to parse it.")
""",
                "solution_code": """# Same as starter
""",
                "dry_run_output": """Stop reason: max_tokens
Text: Quantum computing is a

⚠️  Response was truncated!
Options:
  1. Increase max_tokens and retry
  2. Ask Claude to continue from where it stopped
  3. Ask for a shorter answer

For tool_use responses, truncation means INVALID JSON.
You must retry with higher max_tokens — do NOT try to parse it.""",
                "exam_tips": [
                    "`stop_reason: 'max_tokens'` means truncation, NOT a completed response. The exam will show code that ignores this — it's always wrong.",
                    "If a tool_use response is truncated, the tool call JSON is INCOMPLETE. Never try to parse partial JSON — retry with higher max_tokens.",
                    "The three valid stop_reasons are: `end_turn`, `tool_use`, and `max_tokens`. Know what each means."
                ],
                "hints": []
            },
        ],
        "challenge": None,
    },
]
