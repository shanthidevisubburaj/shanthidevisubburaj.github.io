Title: What is LangGraph Deep Dive: State Reducers, Checkpoints, and Multi-Agent Topologies
Date: 2026-07-22
Category: GenAI
Tags: GenAI, AI, LangGraph, LangChain, AI-Agents, Multi-Agent, RAG, Agentic-Systems
Slug: langgraph-deep-dive-state-reducers-checkpoints-multi-agent-topologies

LangGraph models an AI workflow as a graph of nodes (functions) connected by edges (control flow), with a shared state object flowing through the whole thing. Once you move beyond a single-node chain, five concepts come up in every real project: reducers, conditional routing, checkpointing, dynamic interrupts, and multi-agent topologies. This article covers all five.

## What is the Difference Between a Reducer and the Default Overwrite?

A LangGraph `StateGraph` runs on a `TypedDict`. Every node returns a partial state update, and LangGraph merges it into the running state. Without a reducer, the merge is a plain overwrite:

```python
from typing import TypedDict

class State(TypedDict):
    messages: list
    count: int
```

If a node returns `{"messages": [new_msg]}`, the entire `messages` list gets replaced with `[new_msg]`. Fine for `count` where each node computes a fresh value — disastrous for chat history, since every node would wipe out what came before.

With a reducer, a node's return value is combined with the existing value instead of replacing it:

```python
import operator
from typing import Annotated, TypedDict

class State(TypedDict):
    messages: Annotated[list, operator.add]
    count: int
```

`operator.add` gives list concatenation. The standard choice for chat state is `add_messages`, which also de-duplicates by message ID — replacing an existing message if a node returns one with a matching ID instead of appending a duplicate:

```python
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[list, add_messages]
```

**When to write a custom reducer** — use the default overwrite for scalar "current value" fields, `add_messages` for chat history, and a custom reducer the moment you need logic beyond plain append or replace:

- Dedup by a domain key (accumulated documents deduped by `doc_id`)
- Bounded accumulation (keep only the last N tool results to control context length)
- Dict merges with conflict rules (numeric fields sum, string fields overwrite)
- Aggregating scores from parallel evaluator nodes

```python
def keep_last_n(current: list, new: list, n: int = 10) -> list:
    return (current + new)[-n:]

from functools import partial

class State(TypedDict):
    recent_tool_results: Annotated[list, partial(keep_last_n, n=10)]
```

## How Does add_conditional_edges Work?

`add_conditional_edges` reads the graph state after a node finishes and routes to one of several next nodes based on whatever logic you write:

```python
graph.add_conditional_edges(
    source_node,       # node whose output triggers the decision
    routing_function,  # state -> key
    path_map=None      # optional dict: key -> node name
)
```

The routing function returns a key. If `path_map` is given, that key is looked up to find the real next node; otherwise the key itself must be a valid node name or `END`.

**The agent/tool loop** — the backbone of every tool-using LangGraph agent:

```python
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def call_llm(state: AgentState) -> dict:
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

def should_continue(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if getattr(last_message, "tool_calls", None):
        return "tools"
    return "end"

tool_node = ToolNode(tools)

graph = StateGraph(AgentState)
graph.add_node("agent", call_llm)
graph.add_node("tools", tool_node)
graph.set_entry_point("agent")

graph.add_conditional_edges(
    "agent",
    should_continue,
    {"tools": "tools", "end": END},
)

graph.add_edge("tools", "agent")  # unconditional — always return to LLM after a tool runs

app = graph.compile()
```

The only decision point is `agent → tools` or `END`. The `tools → agent` edge is unconditional because once a tool runs, control always returns to the LLM to interpret the result. Termination happens because `should_continue` checks `last_message.tool_calls` — no tool calls means the model considers itself done.

## What Does a Checkpointer Actually Do?

A checkpointer is LangGraph's persistence layer. After every super-step, it saves a full snapshot of graph state to storage. Memory, resuming, and time travel are all built on top of that one behavior.

**`thread_id` — the unit of a conversation**

```python
config = {"configurable": {"thread_id": "user-42-session-1"}}
app.invoke({"messages": [HumanMessage("hi")]}, config=config)
```

All checkpoints under one `thread_id` form a linked history. Invoking again with the same `thread_id` loads the latest checkpoint as the starting state — this is how memory works without manually resending history.

**Time-travel debugging**

```python
history = list(app.get_state_history(config))

past_config = {
    "configurable": {
        "thread_id": "user-42-session-1",
        "checkpoint_id": history[3].config["configurable"]["checkpoint_id"],
    }
}
app.invoke(None, config=past_config)  # resumes from that exact snapshot
```

Rewind to any checkpoint, tweak state or input, and re-run forward — without re-executing everything before it.

**Resuming after human input** — an interrupted graph is checkpointed exactly at the pause point. A human reviews or supplies input, then resuming means invoking again on the same `thread_id`. LangGraph picks up from the saved checkpoint rather than starting over.

**`MemorySaver` vs. a Postgres saver** — the API is identical; you only swap the object passed to `.compile(checkpointer=...)`:

| | `MemorySaver` | `PostgresSaver` |
|---|---|---|
| Storage | In-process Python dict | Real database |
| Survives restart | No | Yes |
| Multi-process sharing | No | Yes |
| Use for | Local dev, notebooks, tests | Any real backend, production |

## How Do interrupt() and Command(resume=...) Work Together?

**Static interrupts** — set once at compile time, these pause at a fixed structural point every time execution reaches it:

```python
app = graph.compile(checkpointer=checkpointer, interrupt_before=["tools"])
```

Resuming means invoking with `None` as input on the same config:

```python
app.invoke(None, config=config)
```

Use case: a compliance rule that every tool call must be reviewed by a human, no exceptions, no conditional logic needed.

**Dynamic interrupts** — `interrupt()` is called from inside node code, conditionally, based on runtime state:

```python
from langgraph.types import interrupt, Command

def review_tool_call(state: AgentState) -> dict:
    last_message = state["messages"][-1]
    tool_call = last_message.tool_calls[0]

    if tool_call["name"] in SENSITIVE_TOOLS:
        decision = interrupt({
            "question": f"Approve call to {tool_call['name']}?",
            "args": tool_call["args"],
        })
        if decision != "approve":
            return {"messages": [ToolMessage(content="Rejected by reviewer", tool_call_id=tool_call["id"])]}
```

Resuming passes a value back in:

```python
app.invoke(Command(resume="approve"), config=config)
```

The node re-runs from the top. `interrupt()` now returns the resume value instead of pausing again.

Use case: only pause for tool calls touching production data or exceeding a cost threshold, where the human decision needs to flow back into the waiting node — not just a "continue" signal.

| | Static (`interrupt_before`/`after`) | Dynamic (`interrupt()` + `Command`) |
|---|---|---|
| Set where | Compile time | Inside node logic, at runtime |
| Condition | Structural, always at this node | Conditional, any logic |
| Resume call | `invoke(None, config)` | `invoke(Command(resume=value), config)` |
| Data back in | None | Arbitrary payload |

## How Do Supervisor, Hierarchical, and Network Topologies Compare?

**Supervisor** — a central node routes to worker agents and regains control after each one finishes, deciding what happens next every time. Workers report back to the supervisor only, never to each other. Good for centralized sequencing and a single place that decides "are we done."

**Hierarchical** — a tree of supervisors: a top-level supervisor routes to team supervisors, each routing to its own workers. Each team is its own supervisor graph, wrapped as a subgraph and used as one node in the parent. Use this when a flat supervisor's routing logic gets too complex managing many workers across genuinely different domains.

**Network** — no central router. Any agent can hand off directly to any other, each deciding via its own conditional edge who acts next. Use this when there is no natural single point of control — e.g., a support triage agent handing directly to billing, which hands directly to a technical agent, with no supervisor in between.

**How a subgraph shares state with its parent** — state is shared by matching key names between the two `TypedDict` schemas:

```python
class ParentState(TypedDict):
    messages: Annotated[list, add_messages]
    task: str

class SubState(TypedDict):
    messages: Annotated[list, add_messages]
    sub_scratchpad: dict

parent_graph.add_node("team_a", compiled_subgraph)
```

`messages` is shared because the key and reducer line up. `task` and `sub_scratchpad` are private to their own graph — non-overlapping keys are simply invisible to the other graph, no error. To pass something new from a subgraph back to the parent, either add that key to the parent's schema, or wrap the subgraph invocation in a function that maps its output fields into the shape the parent expects.

## The Golden Rule of LangGraph Design

**State schema design is the first real decision in any multi-agent project.**

Decide up front which fields must be shared across agents (usually `messages`, sometimes a shared `task` or `plan`) versus which are private working memory for one agent or team. Getting this wrong means rewriting schemas later — and every schema change touches every node that reads or writes state.

## Final Thought

LangGraph's value compounds as a pipeline grows. Reducers handle concurrent writes cleanly. Checkpointing makes memory, resuming, and time travel first-class features rather than custom infrastructure. Conditional edges keep branching logic visible and composable. And the three multi-agent topologies give a vocabulary for expressing any coordination pattern — from a single supervisor to a fully decentralized agent network. Understanding these five concepts is what separates a working LangGraph prototype from a production-ready system.
