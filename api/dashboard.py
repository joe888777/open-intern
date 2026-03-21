"""Dashboard API — REST endpoints for the web UI."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.config import AppConfig, IdentityConfig, LLMConfig, load_config
from memory.store import MemoryEntry, MemoryRecord, MemoryScope, MemoryStore

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

# These get set by server.py at startup
_agent = None
_memory_store: MemoryStore | None = None
_config: AppConfig | None = None
_config_path: str = "config/agent.yaml"


def init_dashboard(agent, memory_store: MemoryStore, config: AppConfig, config_path: str):
    global _agent, _memory_store, _config, _config_path
    _agent = agent
    _memory_store = memory_store
    _config = config
    _config_path = config_path


# --- Status ---

@router.get("/status")
def get_status():
    if _config is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    stats = _get_memory_stats()
    return {
        "name": _config.identity.name,
        "role": _config.identity.role,
        "platform": _config.platform.primary,
        "llm_provider": _config.llm.provider,
        "llm_model": _config.llm.model,
        "memory_stats": stats,
    }


# --- Config ---

@router.get("/config")
def get_config():
    if _config is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    data = _config.model_dump()
    # Redact secrets
    data["llm"]["api_key"] = "***" if data["llm"]["api_key"] else ""
    if data["platform"]["lark"]["app_secret"]:
        data["platform"]["lark"]["app_secret"] = "***"
    if data["platform"]["discord"]["bot_token"]:
        data["platform"]["discord"]["bot_token"] = "***"
    if data["platform"]["slack"]["bot_token"]:
        data["platform"]["slack"]["bot_token"] = "***"
    if data["platform"]["slack"]["app_token"]:
        data["platform"]["slack"]["app_token"] = "***"
    return data


class IdentityUpdate(BaseModel):
    name: str
    role: str
    personality: str
    avatar_url: str = ""


@router.put("/config/identity")
def update_identity(body: IdentityUpdate):
    global _config
    if _config is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    _config.identity = IdentityConfig(**body.model_dump())
    _save_config()
    return {"ok": True, "message": "Identity updated. Restart agent to apply."}


class LLMUpdate(BaseModel):
    provider: str
    model: str
    temperature: float = 0.7
    max_tokens_per_action: int = 4096
    daily_cost_budget_usd: float = 10.0


@router.put("/config/llm")
def update_llm(body: LLMUpdate):
    global _config
    if _config is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    # Preserve existing api_key
    existing_key = _config.llm.api_key
    _config.llm = LLMConfig(**body.model_dump(), api_key=existing_key)
    _save_config()
    return {"ok": True, "message": "LLM config updated. Restart agent to apply."}


# --- Chat ---

# In-memory thread metadata (title, created_at)
_thread_meta: dict[str, dict] = {}


class ChatRequest(BaseModel):
    message: str
    thread_id: str = ""


class ChatResponse(BaseModel):
    response: str
    thread_id: str
    title: str


@router.post("/chat", response_model=ChatResponse)
def chat(body: ChatRequest):
    if _agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    from uuid import uuid4
    is_new = not body.thread_id
    thread_id = body.thread_id or str(uuid4())
    response = _agent.chat(
        body.message,
        context={
            "platform": "web",
            "channel_id": "web-dashboard",
            "user_name": "admin",
            "is_dm": True,
        },
        thread_id=thread_id,
    )

    # Auto-generate title on first message
    if is_new:
        title = _generate_thread_title(body.message, response)
        _thread_meta[thread_id] = {
            "title": title,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
    else:
        title = _thread_meta.get(thread_id, {}).get("title", "")

    return ChatResponse(response=response, thread_id=thread_id, title=title)


def _generate_thread_title(user_message: str, agent_response: str) -> str:
    """Use the LLM to generate a short thread title."""
    if _agent is None or _agent._agent is None:
        return user_message[:40]
    try:
        from core.agent import _create_llm
        llm = _create_llm(_agent.config)
        result = llm.invoke(
            f"Generate a very short title (max 6 words, no quotes) for a conversation that starts with:\n"
            f"User: {user_message[:200]}\n"
            f"Reply in the same language as the user message."
        )
        content = result.content
        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    return block["text"].strip()[:50]
        return str(content).strip()[:50]
    except Exception as e:
        logger.warning(f"Failed to generate thread title: {e}")
        return user_message[:40]


# --- Threads ---

@router.get("/threads")
def list_threads():
    """List all conversation threads with titles."""
    if _agent is None or _agent._checkpointer is None:
        return {"threads": []}
    checkpointer = _agent._checkpointer
    threads: dict[str, dict] = {}
    for (thread_id, _ns), _cp_id in checkpointer.storage.items():
        if thread_id not in threads:
            meta = _thread_meta.get(thread_id, {})
            latest_key = max(_cp_id.keys())
            cp_data = _cp_id[latest_key]
            checkpoint = cp_data[0]
            threads[thread_id] = {
                "thread_id": thread_id,
                "title": meta.get("title", ""),
                "created_at": meta.get("created_at", checkpoint.get("ts", "")),
            }
    # Sort by created_at descending
    sorted_threads = sorted(threads.values(), key=lambda t: t["created_at"], reverse=True)
    return {"threads": sorted_threads}


@router.get("/threads/{thread_id}")
def get_thread(thread_id: str):
    """Get a thread's metadata."""
    meta = _thread_meta.get(thread_id, {})
    return {"thread_id": thread_id, "title": meta.get("title", "")}


class ThreadTitleUpdate(BaseModel):
    title: str


@router.put("/threads/{thread_id}/title")
def update_thread_title(thread_id: str, body: ThreadTitleUpdate):
    """Update a thread's title."""
    if thread_id not in _thread_meta:
        _thread_meta[thread_id] = {"created_at": datetime.now(timezone.utc).isoformat()}
    _thread_meta[thread_id]["title"] = body.title
    return {"ok": True, "title": body.title}


@router.delete("/threads/{thread_id}")
def delete_thread(thread_id: str):
    """Delete a conversation thread."""
    if _agent is None or _agent._checkpointer is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    keys_to_delete = [k for k in _agent._checkpointer.storage if k[0] == thread_id]
    if not keys_to_delete:
        raise HTTPException(status_code=404, detail="Thread not found")
    for key in keys_to_delete:
        del _agent._checkpointer.storage[key]
    _thread_meta.pop(thread_id, None)
    return {"ok": True}


# --- Memories ---

@router.get("/memories")
def list_memories(scope: str | None = None, limit: int = 50, offset: int = 0):
    if _memory_store is None:
        raise HTTPException(status_code=503, detail="Memory store not initialized")

    with _memory_store._session() as session:
        q = session.query(MemoryRecord)
        if scope:
            q = q.filter(MemoryRecord.scope == scope)
        q = q.order_by(MemoryRecord.created_at.desc())
        total = q.count()
        records = q.offset(offset).limit(limit).all()

        items = []
        for r in records:
            items.append({
                "id": r.id,
                "content": r.content,
                "scope": r.scope,
                "scope_id": r.scope_id,
                "source": r.source,
                "importance": r.importance,
                "created_at": r.created_at.isoformat() if r.created_at else "",
            })
        return {"items": items, "total": total}


@router.get("/memories/stats")
def memory_stats():
    return _get_memory_stats()


@router.delete("/memories/{memory_id}")
def delete_memory(memory_id: str):
    if _memory_store is None:
        raise HTTPException(status_code=503, detail="Memory store not initialized")
    deleted = _memory_store.forget(memory_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Memory not found")
    return {"ok": True}


# --- Helpers ---

def _get_memory_stats() -> dict:
    if _memory_store is None:
        return {"shared": 0, "channel": 0, "personal": 0, "total": 0}
    return {
        "shared": _memory_store.count(MemoryScope.SHARED),
        "channel": _memory_store.count(MemoryScope.CHANNEL),
        "personal": _memory_store.count(MemoryScope.PERSONAL),
        "total": _memory_store.count(),
    }


def _save_config():
    """Write current config back to YAML."""
    if _config is None:
        return
    path = Path(_config_path)
    data = _config.model_dump()
    path.write_text(yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True))
    logger.info(f"Config saved to {path}")
