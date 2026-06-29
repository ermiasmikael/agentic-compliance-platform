# Extracted (sanitized, lightly trimmed) from DPS `agent-mcp` — the MCP tool client (ADR-0039).
# Representative of the platform; not a runnable copy.
#
# The three security properties this exists to enforce, all visible below:
#   1. CLOSED ALLOW-LIST  — `servers` (a dict passed at construction) IS the allow-list. A call to
#      any server not in the map is refused before any network I/O. No dynamic discovery of
#      arbitrary servers — that is the tool-poisoning / over-broad-scope risk a compliance product
#      must forbid.
#   2. NO CONFUSED DEPUTY — the caller's bearer is propagated on every call, so the server acts as
#      the requesting *user*, never an ambient service account.
#   3. AUDITABLE          — every call is recorded into the agent trace as a *digest* (size + hash,
#      never the raw payload, which can be large or carry tenant data). Tracing is best-effort: a
#      trace failure never breaks the tool call.
"""MCP tool client for the DPS agent tier (ADR-0039)."""

from __future__ import annotations

import hashlib
import json
import time
from typing import Any

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


class McpServerNotAllowed(Exception):
    """Raised when a tool call targets a server outside the closed allow-list."""


class McpToolError(Exception):
    """Raised when an allow-listed server returns a tool error."""


class McpToolClient:
    def __init__(self, servers: dict[str, str], *, timeout: float = 120.0, recorder=None) -> None:
        self._servers = dict(servers)  # the allow-list
        self._timeout = timeout
        self._recorder = recorder

    def allows(self, server: str) -> bool:
        return server in self._servers

    async def call(
        self, server: str, tool: str, arguments: dict[str, Any], *, bearer: str
    ) -> dict[str, Any]:
        url = self._servers.get(server)
        if url is None:
            raise McpServerNotAllowed(server)  # refused before any network I/O

        headers = {"Authorization": f"Bearer {bearer}"} if bearer else {}  # propagate caller identity
        started = time.monotonic()
        async with streamablehttp_client(url, headers=headers, timeout=self._timeout) as (
            read,
            write,
            _,
        ):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool, arguments)

        if result.isError:
            raise McpToolError(f"{server}/{tool}: {_text_of(result)}")

        payload = (
            dict(result.structuredContent)
            if result.structuredContent is not None
            else {"text": _text_of(result)}
        )
        await self._record(server, tool, started, digest=_digest(payload))  # trace, best-effort
        return payload

    async def _record(self, server: str, tool: str, started: float, *, digest: dict) -> None:
        if self._recorder is None:
            return
        try:
            await self._recorder.record_mcp_call(server, tool, digest, _ms(started))
        except Exception:  # tracing must never break the tool call
            pass


def _ms(started: float) -> int:
    return int((time.monotonic() - started) * 1000)


def _digest(payload: dict[str, Any]) -> dict[str, Any]:
    """A size + hash of the result — never the raw payload (may be large / tenant data)."""
    raw = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
    return {"bytes": len(raw), "sha256_16": hashlib.sha256(raw).hexdigest()[:16]}


def _text_of(result: Any) -> str:
    return "".join(
        getattr(b, "text", "") for b in result.content if getattr(b, "type", "") == "text"
    )
