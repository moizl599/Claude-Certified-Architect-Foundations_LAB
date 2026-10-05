"""Domain 4: Prompt Engineering & Structured Output (20%) — Labs 4.1–4.2"""

LABS = [
    # ══════════════════════════════════════════════════════════════
    # LAB 4.1 — Structured Output via Tool Use
    # ══════════════════════════════════════════════════════════════
    {
        "id": "4.1",
        "domain": 4,
        "domain_name": "Prompt Engineering & Structured Output",
        "title": "Structured Output via Tool Use",
        "description": "Force Claude to return perfectly structured JSON by using tool_use with schemas — the guaranteed-structure pattern the exam always picks over prompt-based approaches.",
        "difficulty": "intermediate",
        "estimated_time": "35 min",
        "task_statements": ["4.1", "4.2", "4.3"],
        "steps": [
            {
                "id": 1,
                "title": "The Problem with Prompt-Based JSON",
                "language": "python",
                "instruction": """## The Problem with Prompt-Based JSON

Asking Claude to "return JSON" via a prompt works most of the time, but it's **not guaranteed**:
- Claude might wrap JSON in markdown code blocks
- Claude might add explanatory text before/after
- The schema might not match what you expect

The exam's core principle: **When compliance must be guaranteed, use code (tool_use schemas), not prompts.**

Run this to see the problem, then we'll fix it in the next step.""",
                "starter_code": """import anthropic
import json

client = anthropic.Anthropic()

# The WRONG way — asking for JSON in a prompt
response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": \"\"\"Extract the following info as JSON:

Name: Dr. Sarah Chen
Age: 42
Speciality: Cardiology
Hospital: Mass General

Return a JSON object with keys: name, age, specialty, hospital\"\"\"
    }]
)

raw_text = response.content[0].text
print("=== Raw response (prompt-based) ===")
print(raw_text)
print()

# Try to parse it
try:
    # This often fails because Claude wraps in ```json ... ```
    data = json.loads(raw_text)
    print("✅ Parsed successfully (got lucky)")
    print(f"   {data}")
except json.JSONDecodeError as e:
    print(f"❌ JSON parse failed: {e}")
    print("   Claude likely added markdown or explanatory text")
    print()
    print("This is WHY the exam prefers tool_use for structured output.")
    print("Prompts can't guarantee the format. Tools can.")
""",
                "solution_code": """# Same as starter
""",
                "dry_run_output": """=== Raw response (prompt-based) ===
Here's the extracted information as JSON:

```json
{
  "name": "Dr. Sarah Chen",
  "age": 42,
  "specialty": "Cardiology",
  "hospital": "Mass General"
}
```

❌ JSON parse failed: Expecting value: line 1, column 1
   Claude likely added markdown or explanatory text

This is WHY the exam prefers tool_use for structured output.
Prompts can't guarantee the format. Tools can.""",
                "exam_tips": [
                    "⚠️ #1 EXAM PATTERN: When you need guaranteed JSON structure, the answer is ALWAYS tool_use with a schema, never a prompt saying 'return JSON'.",
                    "Prompt-based JSON fails because: Claude wraps in code blocks, adds text, or uses slightly different keys. Tool_use schemas prevent ALL of these.",
                    "If the exam asks 'which approach guarantees the output format?' → tool_use. Always."
                ],
                "hints": []
            },
            {
                "id": 2,
                "title": "Forcing Structure with tool_use",
                "language": "python",
                "instruction": """## Forcing Structure with tool_use

The fix: define a **tool** whose `input_schema` matches the exact JSON structure you want. Then use `tool_choice: {"type": "tool", "name": "..."}` to force Claude to call it.

When Claude is forced to call a tool, its output is **guaranteed to match the schema** — every field, every type, every required key.

This is the technique the exam tests in Domain 4 and in the Structured Data Extraction scenario.""",
                "starter_code": """import anthropic
import json

client = anthropic.Anthropic()

# Define the structure you want as a tool schema
extract_tool = {
    "name": "save_doctor_info",
    "description": "Save extracted doctor information.",
    "input_schema": {
        "type": "object",
        "properties": {
            "name":       {"type": "string", "description": "Doctor's full name"},
            "age":        {"type": "integer", "description": "Doctor's age"},
            "specialty":  {"type": "string", "description": "Medical specialty"},
            "hospital":   {"type": "string", "description": "Hospital name"},
        },
        "required": ["name", "age", "specialty", "hospital"]
    }
}

response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=1024,
    tools=[extract_tool],
    # Force Claude to call this specific tool
    tool_choice={"type": "tool", "name": "save_doctor_info"},
    messages=[{
        "role": "user",
        "content": "Name: Dr. Sarah Chen, Age: 42, Speciality: Cardiology, Hospital: Mass General"
    }]
)

# The tool input IS your structured data — guaranteed to match schema
for block in response.content:
    if block.type == "tool_use":
        data = block.input
        print("=== Structured output (tool_use) ===")
        print(json.dumps(data, indent=2))
        print()
        print(f"Name:      {data['name']}")
        print(f"Age:       {data['age']} (type: {type(data['age']).__name__})")
        print(f"Specialty: {data['specialty']}")
        print(f"Hospital:  {data['hospital']}")
        print()
        print("✅ Every field present, correct types, no markdown wrapping.")
        print("   This is GUARANTEED by the schema — not a lucky parse.")
""",
                "solution_code": """# Same as starter
""",
                "dry_run_output": """=== Structured output (tool_use) ===
{
  "name": "Dr. Sarah Chen",
  "age": 42,
  "specialty": "Cardiology",
  "hospital": "Mass General"
}

Name:      Dr. Sarah Chen
Age:       42 (type: int)
Specialty: Cardiology
Hospital:  Mass General

✅ Every field present, correct types, no markdown wrapping.
   This is GUARANTEED by the schema — not a lucky parse.""",
                "exam_tips": [
                    "`tool_choice: {type: 'tool', name: 'tool_name'}` FORCES Claude to call that tool. This guarantees the output structure.",
                    "The tool doesn't need to DO anything real — you're using the schema as a structured output contract.",
                    "Integer fields come back as actual integers, not strings. The schema enforces types. This is why it's better than prompt-based JSON."
                ],
                "hints": ["Notice that `tool_choice` has three options: `auto` (default), `any` (must call some tool), `{type: 'tool', name: '...'}` (must call specific tool)."]
            },
            {
                "id": 3,
                "title": "Complex Nested Schemas",
                "language": "python",
                "instruction": """## Complex Nested Schemas

Real-world extraction needs nested objects and arrays. The tool_use approach handles these perfectly.

This step extracts a structured invoice from unstructured text — a realistic scenario matching the exam's Structured Data Extraction scenario.""",
                "starter_code": """import anthropic
import json

client = anthropic.Anthropic()

# Complex nested schema
extract_invoice = {
    "name": "save_invoice",
    "description": "Save extracted invoice data.",
    "input_schema": {
        "type": "object",
        "properties": {
            "invoice_number": {"type": "string"},
            "date": {"type": "string", "description": "ISO 8601 date"},
            "vendor": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "address": {"type": "string"},
                },
                "required": ["name"]
            },
            "line_items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "description": {"type": "string"},
                        "quantity": {"type": "integer"},
                        "unit_price": {"type": "number"},
                        "total": {"type": "number"},
                    },
                    "required": ["description", "quantity", "unit_price", "total"]
                }
            },
            "subtotal": {"type": "number"},
            "tax": {"type": "number"},
            "total": {"type": "number"},
        },
        "required": ["invoice_number", "date", "vendor", "line_items", "total"]
    }
}

invoice_text = \"\"\"
INVOICE #INV-2024-0847
Date: March 15, 2024

From: Acme Corp
      123 Business Ave, Suite 400
      San Francisco, CA 94102

Items:
- Widget Pro (x10) @ $29.99 each = $299.90
- Gadget Basic (x5) @ $14.50 each = $72.50
- Premium Support (x1) @ $199.00 = $199.00

Subtotal: $571.40
Tax (8.5%): $48.57
TOTAL: $619.97
\"\"\"

response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=2048,
    tools=[extract_invoice],
    tool_choice={"type": "tool", "name": "save_invoice"},
    messages=[{"role": "user", "content": f"Extract invoice data:\\n{invoice_text}"}]
)

for block in response.content:
    if block.type == "tool_use":
        invoice = block.input
        print("=== Extracted Invoice ===")
        print(json.dumps(invoice, indent=2))
        print()
        print(f"Invoice: {invoice['invoice_number']}")
        print(f"Vendor:  {invoice['vendor']['name']}")
        print(f"Items:   {len(invoice['line_items'])}")
        for item in invoice['line_items']:
            print(f"  - {item['description']}: {item['quantity']} × ${item['unit_price']} = ${item['total']}")
        print(f"Total:   ${invoice['total']}")
""",
                "solution_code": """# Same as starter
""",
                "dry_run_output": """=== Extracted Invoice ===
{
  "invoice_number": "INV-2024-0847",
  "date": "2024-03-15",
  "vendor": {
    "name": "Acme Corp",
    "address": "123 Business Ave, Suite 400, San Francisco, CA 94102"
  },
  "line_items": [
    {"description": "Widget Pro", "quantity": 10, "unit_price": 29.99, "total": 299.90},
    {"description": "Gadget Basic", "quantity": 5, "unit_price": 14.50, "total": 72.50},
    {"description": "Premium Support", "quantity": 1, "unit_price": 199.00, "total": 199.00}
  ],
  "subtotal": 571.40,
  "tax": 48.57,
  "total": 619.97
}

Invoice: INV-2024-0847
Vendor:  Acme Corp
Items:   3
  - Widget Pro: 10 × $29.99 = $299.9
  - Gadget Basic: 5 × $14.5 = $72.5
  - Premium Support: 1 × $199.0 = $199.0
Total:   $619.97""",
                "exam_tips": [
                    "Nested objects and arrays work perfectly in tool schemas. The exam will show both flat and nested extraction scenarios.",
                    "Use `required` at every level of nesting to ensure fields aren't omitted.",
                    "Dates should specify the expected format in the description (e.g., 'ISO 8601'). Without this, Claude might use different formats."
                ],
                "hints": []
            },
        ],
        "challenge": {
            "title": "Extract a Resume",
            "description": "Build a structured extractor for resume/CV text. Schema: personal info, education (array), work experience (array with company, role, dates, bullets), skills (array).",
            "requirements": [
                "Nested schema with at least 3 levels",
                "Arrays of objects for education and experience",
                "Use tool_choice to force the extraction",
                "Validate that all required fields are present"
            ]
        },
    },

    # ══════════════════════════════════════════════════════════════
    # LAB 4.2 — Few-Shot Prompting & Extraction
    # ══════════════════════════════════════════════════════════════
    {
        "id": "4.2",
        "domain": 4,
        "domain_name": "Prompt Engineering & Structured Output",
        "title": "Few-Shot Prompting & Extraction",
        "description": "Design effective system prompts and few-shot examples for consistent, high-quality extraction.",
        "difficulty": "intermediate",
        "estimated_time": "30 min",
        "task_statements": ["4.4", "4.5", "4.6"],
        "steps": [
            {
                "id": 1,
                "title": "System Prompt Best Practices",
                "language": "python",
                "instruction": """## System Prompt Best Practices

The `system` parameter sets Claude's role and constraints for the entire conversation. The exam tests specific patterns:

1. **Role definition** — who Claude is acting as
2. **Output constraints** — format, length, style rules
3. **Negative constraints** — what NOT to do (equally important)
4. **XML tags** — Claude responds well to structured prompts using XML

Key rule: system prompts work best when they are **specific and behavioral**, not vague aspirational statements.""",
                "starter_code": """import anthropic

client = anthropic.Anthropic()

# BAD system prompt (vague, no constraints)
bad_system = "You are a helpful assistant that extracts data."

# GOOD system prompt (specific, behavioral, constrained)
good_system = \"\"\"You are a data extraction specialist. Your job is to extract structured information from unstructured text.

<rules>
- Extract ONLY information explicitly stated in the text
- Never infer, guess, or add information not present
- If a field cannot be determined from the text, use null
- Do not add commentary or explanations
- Respond using the provided tool only
</rules>

<output_format>
- Dates: ISO 8601 (YYYY-MM-DD)
- Currency: numeric value only, no symbols
- Names: as written in the source text
</output_format>\"\"\"

# Test with the good system prompt
tools = [{
    "name": "extract_event",
    "description": "Extract event information.",
    "input_schema": {
        "type": "object",
        "properties": {
            "event_name": {"type": "string"},
            "date": {"type": ["string", "null"]},
            "location": {"type": ["string", "null"]},
            "price": {"type": ["number", "null"]},
        },
        "required": ["event_name"]
    }
}]

text = "Join us for PyCon 2024 in Pittsburgh on May 15th! Early bird tickets are $350."

response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=1024,
    system=good_system,
    tools=tools,
    tool_choice={"type": "tool", "name": "extract_event"},
    messages=[{"role": "user", "content": f"Extract event info: {text}"}]
)

import json
for block in response.content:
    if block.type == "tool_use":
        print("=== Extracted Event ===")
        print(json.dumps(block.input, indent=2))
        print()
        print("Notice:")
        print("  - Date is ISO 8601 (as instructed)")
        print("  - Price is numeric (no $ symbol)")
        print("  - Only explicitly stated info extracted")
""",
                "solution_code": """# Same as starter
""",
                "dry_run_output": """=== Extracted Event ===
{
  "event_name": "PyCon 2024",
  "date": "2024-05-15",
  "location": "Pittsburgh",
  "price": 350
}

Notice:
  - Date is ISO 8601 (as instructed)
  - Price is numeric (no $ symbol)
  - Only explicitly stated info extracted""",
                "exam_tips": [
                    "XML tags in system prompts (<rules>, <output_format>) give Claude clear structure. The exam prefers tagged prompts over plain-text instructions.",
                    "Negative constraints ('never infer') are as important as positive ones. The exam will show prompts missing these.",
                    "The `system` parameter is separate from `messages`. It's NOT the first user message. The exam tests this distinction."
                ],
                "hints": []
            },
            {
                "id": 2,
                "title": "Few-Shot Examples in Messages",
                "language": "python",
                "instruction": """## Few-Shot Examples in Messages

Few-shot prompting means giving Claude examples of the input→output pattern you want. With the Claude API, examples go in the `messages` array as user/assistant pairs BEFORE the real request.

The exam tests:
- Where examples go (in messages, not in system prompt)
- Format (alternating user/assistant turns)
- How many examples to use (2-3 is usually enough)""",
                "starter_code": """import anthropic
import json

client = anthropic.Anthropic()

system = \"\"\"You are a sentiment classifier. Classify text as positive, negative, or neutral.
Respond with the classification tool only.\"\"\"

tools = [{
    "name": "classify",
    "description": "Submit classification result.",
    "input_schema": {
        "type": "object",
        "properties": {
            "sentiment": {"type": "string", "enum": ["positive", "negative", "neutral"]},
            "confidence": {"type": "number", "description": "0.0 to 1.0"},
            "key_phrase": {"type": "string", "description": "The phrase that most indicates the sentiment"},
        },
        "required": ["sentiment", "confidence", "key_phrase"]
    }
}]

# Few-shot examples as message pairs
examples = [
    # Example 1
    {"role": "user", "content": "Classify: The product exceeded my expectations in every way!"},
    {"role": "assistant", "content": [{"type": "tool_use", "id": "ex1", "name": "classify",
        "input": {"sentiment": "positive", "confidence": 0.95, "key_phrase": "exceeded my expectations"}}]},
    {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "ex1", "content": "saved"}]},

    # Example 2
    {"role": "user", "content": "Classify: The delivery was late and the item was damaged."},
    {"role": "assistant", "content": [{"type": "tool_use", "id": "ex2", "name": "classify",
        "input": {"sentiment": "negative", "confidence": 0.9, "key_phrase": "late and damaged"}}]},
    {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "ex2", "content": "saved"}]},

    # Example 3
    {"role": "user", "content": "Classify: The package arrived on Tuesday."},
    {"role": "assistant", "content": [{"type": "tool_use", "id": "ex3", "name": "classify",
        "input": {"sentiment": "neutral", "confidence": 0.85, "key_phrase": "arrived on Tuesday"}}]},
    {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "ex3", "content": "saved"}]},
]

# Real request
real_query = {"role": "user", "content": "Classify: I can't believe how terrible the customer service was today."}
messages = examples + [real_query]

response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=1024,
    system=system,
    tools=tools,
    tool_choice={"type": "tool", "name": "classify"},
    messages=messages,
)

for block in response.content:
    if block.type == "tool_use":
        result = block.input
        print("=== Classification Result ===")
        print(f"Sentiment:  {result['sentiment']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Key phrase: {result['key_phrase']}")
        print()
        print("The few-shot examples taught Claude:")
        print("  - The expected confidence range (0.85-0.95)")
        print("  - To pick a specific key phrase, not summarise")
        print("  - The exact output format via tool_use")
""",
                "solution_code": """# Same as starter
""",
                "dry_run_output": """=== Classification Result ===
Sentiment:  negative
Confidence: 0.92
Key phrase: how terrible the customer service was

The few-shot examples taught Claude:
  - The expected confidence range (0.85-0.95)
  - To pick a specific key phrase, not summarise
  - The exact output format via tool_use""",
                "exam_tips": [
                    "Few-shot examples go in `messages` as user/assistant pairs — NOT in the system prompt. The exam tests this placement.",
                    "For tool_use few-shot, each example needs 3 messages: user input → assistant tool_use → user tool_result. Forgetting the tool_result breaks the pattern.",
                    "2-3 examples is usually enough. The exam won't ask for more than 3. More examples = more tokens = higher cost."
                ],
                "hints": []
            },
        ],
        "challenge": None,
    },
]
