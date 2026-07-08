"""Telegram bot for Eutridats - reuses FastAPI backend."""

import asyncio
import logging
import os

import httpx
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_PREFIX = "/api/v1"
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

_token_cache: str | None = None


async def get_auth_token() -> str:
    global _token_cache
    if _token_cache:
        return _token_cache
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_BASE_URL}{API_PREFIX}/auth/login",
            json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
        )
        response.raise_for_status()
        _token_cache = response.json()["access_token"]
        return _token_cache


async def api_request(method: str, path: str, **kwargs) -> dict:
    token = await get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.request(
            method,
            f"{API_BASE_URL}{API_PREFIX}{path}",
            headers=headers,
            **kwargs,
        )
        if response.status_code == 401:
            global _token_cache
            _token_cache = None
            token = await get_auth_token()
            headers["Authorization"] = f"Bearer {token}"
            response = await client.request(
                method,
                f"{API_BASE_URL}{API_PREFIX}{path}",
                headers=headers,
                **kwargs,
            )
        response.raise_for_status()
        return response.json()


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Welcome to Eutridats Bot!\n\n"
        "Commands:\n"
        "/search <query> - Search the knowledge graph\n"
        "/person <name> - Find a person\n"
        "/company <name> - Find a company\n"
        "/ask <question> - Ask a natural language question\n\n"
        "Or just send a message to chat!"
    )


async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = " ".join(context.args) if context.args else ""
    if not query:
        await update.message.reply_text("Usage: /search <query>")
        return

    try:
        result = await api_request("POST", "/search", json={"query": query, "mode": "hybrid"})
        results = result.get("results", [])
        if not results:
            await update.message.reply_text("No results found.")
            return

        lines = [f"• {r.get('name', 'Unknown')} ({', '.join(r.get('_labels', []))})" for r in results[:10]]
        await update.message.reply_text(f"Found {result.get('total', 0)} results:\n\n" + "\n".join(lines))
    except Exception as exc:
        await update.message.reply_text(f"Search failed: {exc}")


async def person_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    name = " ".join(context.args) if context.args else ""
    if not name:
        await update.message.reply_text("Usage: /person <name>")
        return

    try:
        result = await api_request("POST", "/search", json={"query": name, "mode": "hybrid", "limit": 1})
        results = result.get("results", [])
        if not results:
            await update.message.reply_text(f"No person found matching '{name}'.")
            return

        person_id = results[0].get("id")
        if person_id:
            profile = await api_request("GET", f"/person/{person_id}")
            text = f"*{profile.get('name', 'Unknown')}*\n"
            if profile.get("title"):
                text += f"Title: {profile['title']}\n"
            if profile.get("email"):
                text += f"Email: {profile['email']}\n"
            await update.message.reply_text(text, parse_mode="Markdown")
        else:
            await update.message.reply_text(f"Found: {results[0].get('name')}")
    except Exception as exc:
        await update.message.reply_text(f"Error: {exc}")


async def company_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    name = " ".join(context.args) if context.args else ""
    if not name:
        await update.message.reply_text("Usage: /company <name>")
        return

    try:
        result = await api_request("POST", "/search", json={"query": name, "mode": "hybrid", "limit": 5})
        companies = [r for r in result.get("results", []) if "Company" in r.get("_labels", [])]
        if not companies:
            await update.message.reply_text(f"No company found matching '{name}'.")
            return
        lines = [f"• {c.get('name')} ({c.get('industry', 'N/A')})" for c in companies]
        await update.message.reply_text("\n".join(lines))
    except Exception as exc:
        await update.message.reply_text(f"Error: {exc}")


async def ask_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    question = " ".join(context.args) if context.args else ""
    if not question:
        await update.message.reply_text("Usage: /ask <question>")
        return
    await _handle_chat(update, question)


async def chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return
    await _handle_chat(update, update.message.text)


async def _handle_chat(update: Update, message: str) -> None:
    await update.message.reply_chat_action("typing")
    try:
        result = await api_request("POST", "/chat", json={"message": message})
        answer = result.get("answer", "No response")
        if len(answer) > 4000:
            answer = answer[:4000] + "..."
        await update.message.reply_text(answer)
    except Exception as exc:
        await update.message.reply_text(f"Sorry, I couldn't process that: {exc}")


def main() -> None:
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set")
        return

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("search", search_command))
    app.add_handler(CommandHandler("person", person_command))
    app.add_handler(CommandHandler("company", company_command))
    app.add_handler(CommandHandler("ask", ask_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_handler))

    logger.info("Starting Eutridats Telegram bot...")
    app.run_polling()


if __name__ == "__main__":
    main()
