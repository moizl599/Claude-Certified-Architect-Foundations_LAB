"""Domain 5: Context Management & Reliability (15%) — Lab 5.1"""

LABS = [
    # ══════════════════════════════════════════════════════════════
    # LAB 5.1 — Context Window Strategies
    # ══════════════════════════════════════════════════════════════
    {
        "id": "5.1",
        "domain": 5,
        "domain_name": "Context Management & Reliability",
        "title": "Context Window Strategies",
        "description": "Manage long conversations that approach the context limit — counting tokens, implementing summarisation, and using sliding windows.",
        "difficulty": "intermediate",
        "estimated_time": "35 min",
        "task_statements": ["5.1", "5.2", "5.3", "5.4", "5.5", "5.6"],
        "steps": [
            {
                "id": 1,
                "title": "Understanding Token Limits",
                "language": "python",
                "instruction": """## Understanding Token Limits

Every Claude model has a **context window** — the maximum number of tokens it can process in a single request (input + output combined).

Model limits (as of 2024):
- **Claude Haiku**: 200K tokens
- **Claude Sonnet**: 200K tokens
- **Claude Opus**: 200K tokens

The `usage` field in every API response tells you exactly how many tokens were used. The exam tests whether you monitor this.

Key concept: as conversations grow, the input tokens increase with every turn because you send the ENTIRE conversation history each time.""",
                "starter_code": """import anthropic

client = anthropic.Anthropic()

# Simulate a growing conversation
messages = []
topics = [
    "Explain what a REST API is.",
    "Now explain GraphQL and how it differs from REST.",
    "What about gRPC? When would you use it instead?",
    "Compare all three for a microservices architecture.",
    "Give me a decision matrix for choosing between them.",
]

print("=== Token Growth Across Turns ===\\n")
total_input = 0
total_output = 0

for i, topic in enumerate(topics):
    messages.append({"role": "user", "content": topic})

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        messages=messages,
    )

    input_tokens = response.usage.input_tokens
    output_tokens = response.usage.output_tokens
    total_input += input_tokens
    total_output += output_tokens

    print(f"Turn {i+1}: {input_tokens:,} in + {output_tokens:,} out = {input_tokens + output_tokens:,} total")

    # Add assistant response to conversation
    messages.append({"role": "assistant", "content": response.content[0].text})

print(f"\\n{'='*40}")
print(f"Cumulative tokens sent: {total_input:,}")
print(f"Cumulative tokens received: {total_output:,}")
print(f"Final message array size: {len(messages)} messages")
print()
print("⚠️  Notice: input_tokens GROWS each turn because")
print("   the entire conversation history is re-sent every time.")
print()
print("At this rate, a long conversation will hit the context")
print("window limit. The next steps show how to handle this.")
""",
                "solution_code": """# Same as starter
""",
                "dry_run_output": """=== Token Growth Across Turns ===

Turn 1: 18 in + 156 out = 174 total
Turn 2: 192 in + 203 out = 395 total
Turn 3: 413 in + 187 out = 600 total
Turn 4: 618 in + 245 out = 863 total
Turn 5: 881 in + 198 out = 1,079 total

========================================
Cumulative tokens sent: 2,122
Cumulative tokens received: 989
Final message array size: 10 messages

⚠️  Notice: input_tokens GROWS each turn because
   the entire conversation history is re-sent every time.

At this rate, a long conversation will hit the context
window limit. The next steps show how to handle this.""",
                "exam_tips": [
                    "Token counts come from `response.usage.input_tokens` and `response.usage.output_tokens`. The exam tests whether you check these.",
                    "Input tokens grow with EVERY turn because the full conversation is re-sent. This is the fundamental reason you need context management.",
                    "The context window includes BOTH input and output tokens. max_tokens limits only the OUTPUT."
                ],
                "hints": []
            },
            {
                "id": 2,
                "title": "Sliding Window Strategy",
                "language": "python",
                "instruction": """## Sliding Window Strategy

The simplest context management: keep only the last N turns and drop older ones.

**Pros:** Simple, predictable token usage
**Cons:** Loses earlier context entirely

The exam tests when this is appropriate:
- ✅ Stateless tasks (each turn is independent)
- ✅ Chat where only recent context matters
- ❌ Tasks where early context is critical (contracts, specifications)""",
                "starter_code": """import anthropic

client = anthropic.Anthropic()

MAX_TURNS = 6  # Keep only last 6 messages (3 user + 3 assistant)

def sliding_window_chat(messages: list, max_turns: int = MAX_TURNS) -> list:
    \"\"\"Keep only the most recent turns.\"\"\"
    if len(messages) <= max_turns:
        return messages

    # Always keep messages in pairs (user + assistant)
    # Take the last max_turns messages
    trimmed = messages[-max_turns:]

    # Ensure we start with a user message
    if trimmed[0]["role"] == "assistant":
        trimmed = trimmed[1:]

    return trimmed


# Simulate a long conversation
messages = []
questions = [
    "What is Python?",
    "What are its main features?",
    "How does memory management work in Python?",
    "What is the GIL?",
    "Explain Python decorators.",
    "What about context managers?",
    "How do generators work?",
    "What is asyncio?",
]

print("=== Sliding Window Demo ===\\n")

for i, q in enumerate(questions):
    messages.append({"role": "user", "content": q})

    # Apply sliding window BEFORE sending
    windowed = sliding_window_chat(messages)

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=256,
        messages=windowed,
    )

    answer = response.content[0].text
    messages.append({"role": "assistant", "content": answer})

    print(f"Turn {i+1}: '{q}'")
    print(f"  Messages sent: {len(windowed)} (of {len(messages)} total)")
    print(f"  Tokens: {response.usage.input_tokens}")
    print()

print("The window keeps token count stable regardless of")
print("how long the conversation gets.")
""",
                "solution_code": """# Same as starter
""",
                "dry_run_output": """=== Sliding Window Demo ===

Turn 1: 'What is Python?'
  Messages sent: 1 (of 1 total)
  Tokens: 12

Turn 2: 'What are its main features?'
  Messages sent: 3 (of 3 total)
  Tokens: 178

Turn 3: 'How does memory management work in Python?'
  Messages sent: 5 (of 5 total)
  Tokens: 412

Turn 4: 'What is the GIL?'
  Messages sent: 6 (of 7 total)
  Tokens: 498

Turn 5: 'Explain Python decorators.'
  Messages sent: 6 (of 9 total)
  Tokens: 487

Turn 6: 'What about context managers?'
  Messages sent: 6 (of 11 total)
  Tokens: 501

Turn 7: 'How do generators work?'
  Messages sent: 6 (of 13 total)
  Tokens: 493

Turn 8: 'What is asyncio?'
  Messages sent: 6 (of 15 total)
  Tokens: 510

The window keeps token count stable regardless of
how long the conversation gets.""",
                "exam_tips": [
                    "Sliding window is the simplest strategy but loses early context. The exam asks WHEN to use it — for stateless/chat tasks, not document analysis.",
                    "Always ensure the trimmed messages start with a `user` message. The API requires alternating user/assistant turns starting with user.",
                    "The exam will ask: 'How to keep costs predictable in a long conversation?' → sliding window (fixed token budget per turn)."
                ],
                "hints": []
            },
            {
                "id": 3,
                "title": "Summarisation Strategy",
                "language": "python",
                "instruction": """## Summarisation Strategy

A smarter approach: when the conversation gets long, summarise the older turns into a compact summary and prepend it.

**Pros:** Retains key information from the entire conversation
**Cons:** Summary may lose details; adds an API call

The exam tests this as the preferred strategy when early context matters.""",
                "starter_code": """import anthropic

client = anthropic.Anthropic()

TOKEN_THRESHOLD = 1000  # Summarise when input exceeds this

def summarise_history(messages: list) -> str:
    \"\"\"Ask Claude to summarise the conversation so far.\"\"\"
    history_text = ""
    for msg in messages:
        role = msg["role"].upper()
        content = msg["content"] if isinstance(msg["content"], str) else str(msg["content"])
        history_text += f"{role}: {content}\\n\\n"

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        messages=[{
            "role": "user",
            "content": f\"\"\"Summarise this conversation in 2-3 sentences, preserving:
- Key facts and decisions
- Any unresolved questions
- Important context for future turns

Conversation:
{history_text}\"\"\"
        }]
    )
    return response.content[0].text


def managed_chat(messages: list, new_question: str) -> tuple[list, str]:
    \"\"\"Send a message with automatic summarisation when context grows too large.\"\"\"
    messages.append({"role": "user", "content": new_question})

    # Check if we need to summarise
    # (In production, use anthropic.count_tokens() for accuracy)
    estimated_tokens = sum(
        len(m.get("content", "") if isinstance(m.get("content"), str) else str(m.get("content", ""))) // 4
        for m in messages
    )

    if estimated_tokens > TOKEN_THRESHOLD and len(messages) > 4:
        print(f"  📝 Context too large (~{estimated_tokens} tokens). Summarising...")
        summary = summarise_history(messages[:-1])  # Summarise everything except the new question
        print(f"  📝 Summary: {summary[:100]}...")

        # Replace old messages with summary + new question
        messages = [
            {"role": "user", "content": f"[Previous conversation summary: {summary}]"},
            {"role": "assistant", "content": "I understand the context from our previous discussion. How can I help?"},
            messages[-1],  # Keep the new question
        ]

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        messages=messages,
    )

    answer = response.content[0].text
    messages.append({"role": "assistant", "content": answer})
    return messages, answer


# Demo
messages = []
questions = [
    "I'm building a REST API for a library system with books, members, and loans.",
    "What database schema would you recommend?",
    "Now let's design the API endpoints.",
    "What about authentication?",
    "Let's add rate limiting. What approach do you recommend?",
    "Summarise our full API design so far.",
]

print("=== Summarisation Strategy Demo ===\\n")
for i, q in enumerate(questions):
    print(f"Turn {i+1}: {q}")
    messages, answer = managed_chat(messages, q)
    print(f"  Messages in context: {len(messages)}")
    print(f"  Answer: {answer[:120]}...\\n")
""",
                "solution_code": """# Same as starter
""",
                "dry_run_output": """=== Summarisation Strategy Demo ===

Turn 1: I'm building a REST API for a library system with books, members, and loans.
  Messages in context: 2
  Answer: Great! A library management REST API is a solid project. Let me help you design it. We'll need three core resources...

Turn 2: What database schema would you recommend?
  Messages in context: 4
  Answer: For a library system, I'd recommend a PostgreSQL schema with three main tables: books (id, title, author, isbn, ...

Turn 3: Now let's design the API endpoints.
  Messages in context: 6
  Answer: Here are the RESTful endpoints for your library API: GET /api/books, POST /api/books, GET /api/books/:id, ...

Turn 4: What about authentication?
  Messages in context: 8
  Answer: For your library API, I'd recommend JWT-based authentication with role-based access control (RBAC)...

Turn 5: Let's add rate limiting. What approach do you recommend?
  📝 Context too large (~1247 tokens). Summarising...
  📝 Summary: We're designing a REST API for a library system with books, members, and loans. We've established a Post...
  Messages in context: 4
  Answer: For rate limiting your library API, I recommend a token bucket algorithm using Redis...

Turn 6: Summarise our full API design so far.
  Messages in context: 6
  Answer: Here's our complete library API design: PostgreSQL schema with books/members/loans tables, RESTful endpoints...""",
                "exam_tips": [
                    "Summarisation preserves key context from the ENTIRE conversation. The exam prefers it over sliding window when early context matters.",
                    "The summary goes in a user message at the start of the trimmed history, NOT in the system prompt.",
                    "⚠️ TRAP: The exam will ask 'How to handle a conversation that exceeds the context window?' — 'Increase max_tokens' is WRONG (that controls output only). The answer is summarisation or sliding window."
                ],
                "hints": []
            },
            {
                "id": 4,
                "title": "Challenge: Build a Context Manager",
                "language": "python",
                "instruction": """## Challenge: Build a Context Manager Class

Create a reusable `ConversationManager` class that:
1. Tracks token usage across turns
2. Automatically switches between strategies:
   - Under 50% of limit → send full history
   - 50-80% → summarise old turns, keep recent
   - Over 80% → sliding window with summary prefix
3. Logs decisions for debugging

This is the kind of production-grade context management the exam expects you to understand.""",
                "starter_code": """import anthropic

client = anthropic.Anthropic()

class ConversationManager:
    def __init__(self, max_context_tokens: int = 4000):
        self.max_tokens = max_context_tokens
        self.messages = []
        self.total_tokens_used = 0
        self.summaries = []

    def _estimate_tokens(self) -> int:
        \"\"\"Rough token estimate (4 chars ≈ 1 token).\"\"\"
        return sum(
            len(str(m.get("content", ""))) // 4
            for m in self.messages
        )

    def _get_strategy(self) -> str:
        estimated = self._estimate_tokens()
        ratio = estimated / self.max_tokens
        if ratio < 0.5:
            return "full"
        elif ratio < 0.8:
            return "summarise"
        else:
            return "window"

    def send(self, user_message: str) -> str:
        \"\"\"Send a message with automatic context management.\"\"\"
        self.messages.append({"role": "user", "content": user_message})
        strategy = self._get_strategy()
        print(f"  Strategy: {strategy} (~{self._estimate_tokens()}/{self.max_tokens} tokens)")

        # TODO: Implement the three strategies
        # For "full": send self.messages as-is
        # For "summarise": summarise older messages, keep recent 4
        # For "window": keep only last 4 messages with summary prefix

        # For now, just send full history
        context = self.messages

        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=512,
            messages=context,
        )

        answer = response.content[0].text
        self.messages.append({"role": "assistant", "content": answer})
        self.total_tokens_used += response.usage.input_tokens + response.usage.output_tokens
        return answer

# Test
mgr = ConversationManager(max_context_tokens=2000)
questions = [
    "Explain microservices architecture.",
    "What are the main challenges?",
    "How do you handle inter-service communication?",
    "What about data consistency?",
    "Explain the saga pattern.",
    "How do you monitor microservices?",
]

for q in questions:
    print(f"\\nQ: {q}")
    answer = mgr.send(q)
    print(f"A: {answer[:100]}...")

print(f"\\nTotal tokens used: {mgr.total_tokens_used:,}")
""",
                "solution_code": """import anthropic

client = anthropic.Anthropic()

class ConversationManager:
    def __init__(self, max_context_tokens=4000):
        self.max_tokens = max_context_tokens
        self.messages = []
        self.total_tokens_used = 0
        self.summary = None

    def _estimate_tokens(self):
        return sum(len(str(m.get("content", ""))) // 4 for m in self.messages)

    def _get_strategy(self):
        ratio = self._estimate_tokens() / self.max_tokens
        if ratio < 0.5: return "full"
        elif ratio < 0.8: return "summarise"
        else: return "window"

    def _summarise(self, msgs):
        text = "\\n".join(f"{m['role']}: {str(m['content'])[:200]}" for m in msgs)
        r = client.messages.create(
            model="claude-haiku-4-5-20251001", max_tokens=200,
            messages=[{"role": "user", "content": f"Summarise in 2 sentences: {text}"}])
        return r.content[0].text

    def send(self, user_message):
        self.messages.append({"role": "user", "content": user_message})
        strategy = self._get_strategy()
        print(f"  Strategy: {strategy} (~{self._estimate_tokens()}/{self.max_tokens} tokens)")

        if strategy == "full":
            context = self.messages
        elif strategy == "summarise":
            old = self.messages[:-4]
            self.summary = self._summarise(old)
            context = [
                {"role": "user", "content": f"[Context: {self.summary}]"},
                {"role": "assistant", "content": "Understood."},
            ] + self.messages[-4:]
        else:
            prefix = f"[Context: {self.summary}]" if self.summary else "[Earlier conversation omitted]"
            recent = self.messages[-4:]
            if recent[0]["role"] == "assistant":
                recent = recent[1:]
            context = [
                {"role": "user", "content": prefix},
                {"role": "assistant", "content": "Understood."},
            ] + recent

        response = client.messages.create(
            model="claude-haiku-4-5-20251001", max_tokens=512, messages=context)
        answer = response.content[0].text
        self.messages.append({"role": "assistant", "content": answer})
        self.total_tokens_used += response.usage.input_tokens + response.usage.output_tokens
        return answer

mgr = ConversationManager(max_context_tokens=2000)
for q in ["Explain microservices.", "Challenges?", "Inter-service comms?",
          "Data consistency?", "Saga pattern?", "Monitoring?"]:
    print(f"\\nQ: {q}")
    print(f"A: {mgr.send(q)[:100]}...")
print(f"\\nTotal tokens: {mgr.total_tokens_used:,}")
""",
                "dry_run_output": """Q: Explain microservices architecture.
  Strategy: full (~12/2000 tokens)
A: Microservices architecture breaks an application into small, independent services that communicate ov...

Q: What are the main challenges?
  Strategy: full (~189/2000 tokens)
A: The main challenges include: distributed data management, network latency, service discovery, and de...

Q: How do you handle inter-service communication?
  Strategy: full (~401/2000 tokens)
A: There are two main patterns: synchronous (REST/gRPC for real-time requests) and asynchronous (messag...

Q: What about data consistency?
  Strategy: full (~634/2000 tokens)
A: In microservices, you can't use traditional ACID transactions across services. Instead, you use even...

Q: Explain the saga pattern.
  Strategy: full (~877/2000 tokens)
A: The Saga pattern manages distributed transactions by breaking them into a sequence of local transact...

Q: How do you monitor microservices?
  Strategy: summarise (~1103/2000 tokens)
A: For microservices monitoring, implement the three pillars of observability: metrics (Prometheus), lo...

Total tokens used: 4,231""",
                "exam_tips": [
                    "The exam expects you to know MULTIPLE context strategies and when each applies. No single strategy is always correct.",
                    "Token counting should use `response.usage` (exact) or `anthropic.count_tokens()` — not character-based estimates. The exam knows the difference.",
                    "The system prompt does NOT count against max_tokens but DOES count against the context window. The exam tests this distinction."
                ],
                "hints": []
            },
        ],
        "challenge": None,
    },
]
