# Extracted (sanitized) from DPS `agent-llm` — the model-agnostic LLM port (ADR-0035).
# Representative of the platform; not a runnable copy.
#
# Why this matters: the agent loop talks to this Protocol, never a provider SDK.
# Runner + model are swappable per-agent behind an adapter (LiteLLM -> on-prem
# Ollama in the lab), with zero agent-code change and no framework lock-in.
"""Model-agnostic LLM port (ADR-0035)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class LlmMessage:
    role: str  # "system", "user", or "assistant"
    content: str


@dataclass(frozen=True)
class LlmResult:
    text: str
    model: str
    input_tokens: int
    output_tokens: int


class Llm(Protocol):
    async def complete(
        self, messages: list[LlmMessage], *, temperature: float = 0.2
    ) -> LlmResult: ...
