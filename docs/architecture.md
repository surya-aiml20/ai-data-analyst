# Architecture

               User
                │
                ▼
      Natural Language Query
                │
                ▼
        AI Agent / LLM Brain
                │
      Understands Intent
                │
        Decides What To Do
                │
 ┌──────────────┼──────────────┐
 │              │              │
 ▼              ▼              ▼
Pandas      SQL Engine     Chart Tool
 │              │              │
 ▼              ▼              ▼
Results     Query Output     Figure
 └──────────────┼──────────────┘
                │
                ▼
        LLM Explains Result
                │
                ▼
             Response

The backend keeps uploaded CSVs in an in-memory session store for a simple assignment deployment. For production, replace the store with object storage plus a metadata database, and persist conversation checkpoints with LangGraph memory.
