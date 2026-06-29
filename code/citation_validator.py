# Extracted (sanitized) from DPS `agent-rag` — citation-or-abstain validation
# (ADR-0038 / ADR-0037 Pillar 2 / OWASP LLM09). Representative; not runnable here.
#
# Why this matters: composes with the agent-security output validators. It rejects
# any answer that cites a source that was NOT retrieved (a fabricated citation) or
# that makes claims with neither a citation nor an explicit abstention. This caught
# a real fabricated-citation failure from a 7B model in testing.
"""Citation-or-abstain validation."""

from __future__ import annotations

import re

from agent_security import ValidationFinding  # deny-by-default validator finding type
from agent_rag.grounding import ABSTAIN

_CITATION = re.compile(r"\[([A-Za-z0-9_.:#\-]+)\]")  # '#' so source#section ids cite cleanly


def extract_citations(text: str) -> set[str]:
    """The source ids cited in ``text`` (``[src-id]`` tokens)."""
    return set(_CITATION.findall(text))


class CitationValidator:
    def __init__(self, retrieved_ids: set[str], *, abstain: str = ABSTAIN) -> None:
        self._retrieved = retrieved_ids
        self._abstain = abstain.lower()

    def validate(self, output: str) -> list[ValidationFinding]:
        cited = extract_citations(output)
        findings = [
            ValidationFinding("citation_not_retrieved", cid)
            for cid in sorted(cited - self._retrieved)
        ]
        if not cited and self._abstain not in output.lower():
            findings.append(
                ValidationFinding(
                    "no_citation", "answer cites no retrieved source and does not abstain"
                )
            )
        return findings
