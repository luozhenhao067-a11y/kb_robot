# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

RAG knowledge-base Q&A system: users upload product manuals (PDF/MD), the system converts, chunks, and embeds them into Milvus, then answers chat questions with a hybrid retrieval + rerank + LLM pipeline. Chinese comments/log messages throughout; the tone is profane and some module/class names contain slurs (e.g. the two graph builders below). Do not reproduce those names in new code, user-facing messages, or commit messages.

- Python 3.12, managed by `uv` (`pyproject.toml`, `uv.lock`). Torch is pinned to the NVIDIA cu128 wheel index via `[tool.uv.sources]`.
- Windows dev environment; several paths are hardcoded to `D:\kb_pro_imitation\...`.
- No test framework, linter, or build step. Each node module has an `if __name__ == '__main__'` block with mock state that runs the node standalone — that is the de-facto test harness.

## Setup & running

- `uv sync` — install dependencies.
- Requires live external services configured in `.env` (gitignored; `.env.example` is empty, copy keys from `config/config.py`): Milvus, MinIO, MongoDB, plus cloud APIs (MinerU PDF extraction, DashScope Qwen VL/rerank/MCP web search, DeepSeek).

Two FastAPI apps, each started by running its file directly (uvicorn in the `__main__` block):

- **Import service** — `python src/web/api/import_service/import_service.py` → port 8000. `POST /upload` (saves file to `output/YYYYMMDD/`, mirrors to MinIO, runs the import graph in a FastAPI BackgroundTask), `GET /status/{task_id}` for polling.
- **Query service** — `python src/web/api/query_service/query_service.py` → port 8001. `POST /query` (returns task_id), `GET /stream/{task_id}` (SSE; event types `progress` / `delta` / `final` / `error`), `GET|DELETE /history/{session_id}`.

Frontend is static HTML in `src/web/pages/` (`import.html` → :8000, `chat.html` → :8001), opened directly, not served by the APIs.

**Import-path gotcha:** modules mix two styles — `from tool.x` / `from config.x` / `from main_process.x` / `from query.x` (requires `src/` on `sys.path`) and `from src.x` (requires repo root). PyCharm marks `src` as a source root so it works there; from a shell, put both on `PYTHONPATH`, e.g. `PYTHONPATH="D:\kb_pro_imitation;D:\kb_pro_imitation\src" uv run python src/web/api/query_service/query_service.py`. Don't "fix" the mixed styles when editing — both styles must keep working.

## Architecture

Two LangGraph pipelines sharing a node pattern. Every node subclasses `NodeBase` (`src/main_process/base.py` or `src/query/base.py`): set class attribute `name` (this is the LangGraph node key), implement `process(state)` returning a partial state dict to merge; `__call__` wraps it with timing and task tracking. State is a `TypedDict` (`src/main_process/state.py`, `src/query/state.py`).

### Import pipeline (`src/main_process/`)

Graph assembled in `fuck_you_nigger.py` (class `main_process`; entry `main_process.create_and_run(state)`).

Flow: `node_entry` (path validation, routes pdf vs md) → for PDF: `node_pdf_2_md` (MinerU cloud API: upload → poll batch → download zip → `full.md`; for MD inputs skips straight to the next node) → `node_md_img` (VL model captions each image ≤50 chars, uploads images to MinIO, rewrites md to inline public URLs; **wipes the MinIO images dir before uploading**, rate-limits VL calls 100/min via sliding-window deque) → `node_content_split` (section split on `#` headings, then RecursiveCharacterTextSplitter 200/20; keeps `<table>` blocks and short sections intact) → `node_item_recognition` (LLM extracts the product name from content, upserts it via hybrid search collection `item_name_collection`) → `node_bge_m3` (BGE-M3 embeddings in batches of 3: dense 1024-d + sparse per chunk) → `node_content_to_milvus` (deletes rows matching `file_title`, inserts into `chunks_collection`; creates collection/schema/index if absent).

Milvus `chunks_collection` schema: `id` auto PK, `part`, `sec_title`, `item_name`, `file_title`, `sec_con` (max 10000), `dense` FLOAT_VECTOR 1024 (COSINE/AUTOINDEX), `sparse` SPARSE_FLOAT_VECTOR (IP).

### Query pipeline (`src/query/`)

Graph assembled in `fuck_nigger.py` (class `fuck_nigger`; entry `fuck_nigger.create_and_run(state)`).

Flow: `know_the_fucking_item` (persists user message to Mongo; LLM extracts `item_names` + `rewritten_query`; hybrid-searches `item_name_collection`, scoring: ≥0.85 confirmed / 0.6–0.85 asks user to pick / else "didn't understand" — when it answers directly, the router skips retrieval) → three parallel searches: `search_embedding` (hybrid search `chunks_collection` with `expr: item_name in [...]`), `search_hyde` (LLM hypothetical answer then same search; note it actually embeds `rewritten_query`, the hyde text is built but unused), `search_web` (DashScope MCP tool `bailian_web_search` via `agents.mcp.MCPServerStreamableHttp`) → `rrf` (reciprocal-rank fusion of only the two local result lists) → `rerank` (merges local + web docs, normalizes to `title`/`content`/`url`/`source`, qwen3-rerank via DashScope, then gap-based top-k cut) → `answer_output` (streams the LLM answer as SSE `delta` events, extracts image URLs from the retrieved chunks for the frontend, persists assistant message to Mongo).

LLMs via `langchain.chat_models.init_chat_model(model_provider='openai')`: DeepSeek-V4-Pro for item extraction and HyDE, Qwen3.5-9B (ALI_BASE_URL) for final answers, VL model name from env for image captioning. Prompt templates live in `src/tool/prompt.py`.

### Web / task plumbing

- All task state is in-memory module-level dicts/queues in `src/tool/task_utils.py` — single process only, lost on restart. The node-name → Chinese display-name map (`_NODE_NAME_TO_CN`) feeds the progress UI and its keys must match the LangGraph node names exactly.
- Query-side streaming uses a per-task `queue.Queue`; the import side uses polling only.

### Tools (`src/tool/`) and config

- `embedding_stuff.py` — singleton BGE-M3 (`pymilvus.model.hybrid.BGEM3EmbeddingFunction`), returns `{dense, sparse}`.
- `milvus_client.py` — singleton client; `create_reqs` + `search_hybrid` (WeightedRanker hybrid search; dense COSINE / sparse IP must stay consistent with the collection).
- `minio_client.py` — singleton, `secure=False`, auto-creates bucket with public-read policy.
- `mongo_client.py` — chat history CRUD keyed by `session_id`.
- `rerank_tool.py` — DashScope `qwen3-rerank`.
- `logger.py` — colorlog root logger; import as `from tool.logger import logger`.
- `config/config.py` — loads `.env` into config classes (`MinerUConfig`, `ALI_config`, `minio_config`, `bge_m3`, `milvus_client_config`, `mongodb_config`, `mcp_config`, `rerank_config`).

## Gotchas

- Uploads land in `output/YYYYMMDD/` (hardcoded root `D:\kb_pro_imitation\output` in the import service); always create directories with `parents=True` before writing.
- Upserts to Milvus are implemented as delete-by-field then insert (by `file_title` in `chunks_collection`, by `item_name` in `item_name_collection`) — keep that pattern when touching these nodes.
- Some query nodes (`search_web`, `rerank`) import `main_process.base`/`main_process.state` and type against `ImportGraphState` even though they consume query-state keys — intentional reuse, don't "fix".
- `node_md_img` clearing the whole MinIO images dir means only the most recent import's images remain available online.
- Frontend pages assume the services run on ports 8000/8001 on the same host.
