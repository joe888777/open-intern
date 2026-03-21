"""HTTP server for receiving webhook events (Lark, etc.) and running the agent."""

from __future__ import annotations

import asyncio
import logging
import sys
from contextlib import asynccontextmanager

from core.agent import OpenInternAgent
from core.config import AppConfig, load_config

logger = logging.getLogger(__name__)

# Global agent instance
_agent: OpenInternAgent | None = None


def get_agent() -> OpenInternAgent:
    if _agent is None:
        raise RuntimeError("Agent not initialized")
    return _agent


async def run_lark(config: AppConfig, agent: OpenInternAgent) -> None:
    """Run the Lark bot with a webhook server."""
    try:
        from fastapi import FastAPI, Request
        import uvicorn
    except ImportError:
        logger.error("FastAPI and uvicorn required for Lark. pip install fastapi uvicorn")
        sys.exit(1)

    from integrations.lark.bot import LarkBot, create_lark_webhook_handler

    bot = LarkBot(agent, config)
    await bot.start()
    handler = create_lark_webhook_handler(bot)

    app = FastAPI(title=f"open_intern - {config.identity.name}")

    @app.post("/lark/webhook")
    async def lark_webhook(request: Request):
        body = await request.json()
        return await handler(body)

    @app.get("/health")
    async def health():
        return {
            "status": "ok",
            "agent": config.identity.name,
            "platform": "lark",
            "memory_count": agent.memory_store.count(),
        }

    server_config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(server_config)
    await server.serve()


async def run_discord(config: AppConfig, agent: OpenInternAgent) -> None:
    """Run the Discord bot."""
    from integrations.discord.bot import DiscordBot

    bot = DiscordBot(agent, config)
    await bot.start()


async def run_agent(config_path: str | None = None) -> None:
    """Main entry point — initialize and run the agent on the configured platform."""
    global _agent

    config = load_config(config_path)

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logger.info(f"Starting open_intern agent: {config.identity.name}")
    logger.info(f"Platform: {config.platform.primary}")
    logger.info(f"LLM: {config.llm.provider}:{config.llm.model}")

    # Initialize agent
    agent = OpenInternAgent(config)
    agent.initialize()
    _agent = agent

    # Run on the configured platform
    platform = config.platform.primary
    if platform == "lark":
        await run_lark(config, agent)
    elif platform == "discord":
        await run_discord(config, agent)
    elif platform == "slack":
        logger.error("Slack integration not yet implemented. Use lark or discord.")
        sys.exit(1)
    else:
        logger.error(f"Unknown platform: {platform}")
        sys.exit(1)
