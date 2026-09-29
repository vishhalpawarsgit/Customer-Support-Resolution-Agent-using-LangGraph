# AI Customer Support Resolution Agent

A LangGraph-based agentic workflow for preparing e-commerce customer-support responses.

## Workflow

Customer Query -> Understand -> Classify -> Generate Response -> Review -> Router

- Approved -> Final -> END
- Not approved -> Fix -> Review
- Maximum 2 fix cycles

The workflow follows the assignment requirement to use state, multiple nodes, normal edges,
a conditional edge, compilation, and graph invocation.

## Project structure

```text
customer-support-agent/
├── .env
├── .env.example
├── .gitignore
├── pyproject.toml
├── README.md
├── app/
│   ├── __init__.py
│   ├── state.py
│   ├── prompts.py
│   ├── nodes.py
│   └── graph.py
├── output/
│   ├── final_response.txt
│   └── execution_result.json
└── main.py
```

## Setup with uv

```bash
uv sync
```

Copy `.env.example` to `.env` and add your Groq API key:

```env
GROQ_API_KEY=your_key_here
GROQ_MODEL=llama-3.1-8b-instant
TEMPERATURE=0
```

`GROQ_MODEL` is configurable because provider model availability can change.

## Run

```bash
uv run python main.py
```

## Example queries

1. `Where is my order? It was supposed to arrive yesterday.`
2. `My headphones arrived broken.`
3. `I ordered a blue shirt but received a red shirt.`
4. `I was charged twice for my order.`
5. `I have a problem with my order.`

The last example is intentionally ambiguous; the model should not invent missing details.

## Key LangGraph concepts

`AgentState` carries information between nodes. Each node returns state updates.
The reviewer writes `approved` and `review_feedback`. `review_router()` uses a conditional
edge to choose `fix` or `final`. The `iteration_count` prevents an endless review/fix loop.

## Output

The application creates:

- `output/final_response.txt`
- `output/execution_result.json`
