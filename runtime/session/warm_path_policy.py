"""Warm-path policy resolver for runtime/session integration.

Precedence (highest -> lowest):
1) Explicit CLI overrides (`chunk_ms_override`, `startup_chunks_override`)
2) Scenario-provided values (if caller forwards them as overrides)
3) Policy mode section from policy config (`default`, `fallback`, `aggressive_not_default`)
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class WarmPolicySelection:
    policy_mode: str
    chunk_ms: int
    startup_chunks: int
    source: str


def load_policy(path: str) -> dict:
    return json.loads(Path(path).read_text())


def resolve_policy(
    policy_path: str,
    policy_mode: str,
    chunk_ms_override: Optional[int] = None,
    startup_chunks_override: Optional[int] = None,
) -> WarmPolicySelection:
    policy = load_policy(policy_path)

    if policy_mode in ("default", "fallback"):
        base = policy[policy_mode]
        chunk_ms = int(base["chunk_ms"])
        startup_chunks = int(base["startup_chunks"])
        source = f"policy:{policy_mode}"
    elif policy_mode == "experimental":
        exp = policy.get("aggressive_not_default", [])
        if not exp:
            raise ValueError("policy_mode experimental requested but aggressive_not_default is empty")
        chunk_ms = int(exp[0]["chunk_ms"])
        startup_chunks = int(exp[0]["startup_chunks"])
        source = "policy:aggressive_not_default[0]"
    else:
        raise ValueError(f"unsupported policy_mode: {policy_mode}")

    if chunk_ms_override is not None:
        chunk_ms = int(chunk_ms_override)
        source = f"override:chunk_ms({chunk_ms})"
    if startup_chunks_override is not None:
        startup_chunks = int(startup_chunks_override)
        source = f"override:startup_chunks({startup_chunks})"

    return WarmPolicySelection(
        policy_mode=policy_mode,
        chunk_ms=chunk_ms,
        startup_chunks=startup_chunks,
        source=source,
    )
