"""MuseTalk-facing session command integration helpers.

This module keeps warm-path policy resolution intact while adding a truthful,
stage-aware integration check that remains explicitly non-production.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import shlex
import subprocess
import time
from typing import Optional

from runtime.session.warm_path_policy import resolve_policy, WarmPolicySelection


class IntegrationFailureReason(str, Enum):
    MISSING_ROOT = "missing_root"
    ROOT_NOT_FOUND = "root_not_found"
    COMMAND_TEMPLATE_ERROR = "command_template_error"
    COMMAND_EMPTY = "command_empty"
    COMMAND_PARSE_ERROR = "command_parse_error"
    ENTRYPOINT_MISSING = "entrypoint_missing"
    REQUIRED_PATH_MISSING = "required_path_missing"
    DRY_RUN_FAILED = "dry_run_failed"
    TINY_REAL_EXECUTION_FAILED = "tiny_real_execution_failed"
    LIFECYCLE_STAGE_FAILED = "lifecycle_stage_failed"


class LifecycleStage(str, Enum):
    SESSION_START = "session_start"
    AVATAR_READY_OR_WARM_ASSUMED = "avatar_ready_or_warm_assumed"
    AUDIO_ACCEPTED = "audio_accepted"
    FIRST_SPEAKING_FRAME_SIGNAL = "first_speaking_frame_signal"


@dataclass
class IntegrationFailure:
    reason: IntegrationFailureReason
    message: str


@dataclass
class SmokeOutcome:
    attempted: bool
    success: bool
    mode: str
    command: Optional[str]
    returncode: Optional[int]
    duration_ms: Optional[int]
    stdout: Optional[str]
    stderr: Optional[str]
    note: str


@dataclass
class LifecycleStageOutcome:
    stage: LifecycleStage
    outcome: SmokeOutcome


@dataclass
class LifecycleExecutionOutcome:
    attempted: bool
    success: bool
    stages: list[LifecycleStageOutcome]
    note: str


@dataclass
class IntegrationReadiness:
    is_ready: bool
    failures: list[IntegrationFailure]
    dry_run_outcome: Optional[SmokeOutcome] = None
    executable_smoke_outcome: Optional[SmokeOutcome] = None
    tiny_real_execution_outcome: Optional[SmokeOutcome] = None
    lifecycle_execution_outcome: Optional[LifecycleExecutionOutcome] = None

    @property
    def readiness_passed(self) -> bool:
        return self.is_ready

    @property
    def dry_run_passed(self) -> Optional[bool]:
        return None if self.dry_run_outcome is None else self.dry_run_outcome.success

    @property
    def executable_smoke_passed(self) -> Optional[bool]:
        return None if self.executable_smoke_outcome is None else self.executable_smoke_outcome.success

    @property
    def tiny_real_execution_passed(self) -> Optional[bool]:
        return None if self.tiny_real_execution_outcome is None else self.tiny_real_execution_outcome.success

    @property
    def lifecycle_execution_passed(self) -> Optional[bool]:
        return None if self.lifecycle_execution_outcome is None else self.lifecycle_execution_outcome.success


@dataclass
class MuseTalkCommandPlan:
    policy: WarmPolicySelection
    command: str
    is_real_runtime_available: bool
    musetalk_root: Optional[str]
    readiness: IntegrationReadiness


def _render_command(
    infer_template: str,
    musetalk_root: Optional[str],
    policy: WarmPolicySelection,
) -> tuple[str, Optional[IntegrationFailure]]:
    try:
        resolved = infer_template.format(
            musetalk_root=musetalk_root or "<musetalk_root>",
            chunk_ms=policy.chunk_ms,
            startup_chunks=policy.startup_chunks,
        )
    except (IndexError, KeyError, ValueError) as exc:
        return "", IntegrationFailure(
            reason=IntegrationFailureReason.COMMAND_TEMPLATE_ERROR,
            message=f"failed to render infer template: {exc}",
        )

    if not resolved.strip():
        return "", IntegrationFailure(
            reason=IntegrationFailureReason.COMMAND_EMPTY,
            message="rendered command is empty",
        )

    return resolved, None


def _run_command(*, mode: str, command: str, cwd: str, timeout_s: float) -> SmokeOutcome:
    start = time.monotonic()
    try:
        proc = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout_s,
            check=False,
        )
        return SmokeOutcome(
            attempted=True,
            success=proc.returncode == 0,
            mode=mode,
            command=command,
            returncode=proc.returncode,
            duration_ms=int((time.monotonic() - start) * 1000),
            stdout=(proc.stdout or "").strip(),
            stderr=(proc.stderr or "").strip(),
            note="completed",
        )
    except subprocess.TimeoutExpired as exc:
        return SmokeOutcome(
            attempted=True,
            success=False,
            mode=mode,
            command=command,
            returncode=None,
            duration_ms=int((time.monotonic() - start) * 1000),
            stdout=(exc.stdout or "").strip() if isinstance(exc.stdout, str) else None,
            stderr=(exc.stderr or "").strip() if isinstance(exc.stderr, str) else None,
            note=f"timed out after {timeout_s}s",
        )


def _run_lifecycle_path(
    *,
    cwd: str,
    lifecycle_commands: dict[LifecycleStage, str],
    lifecycle_timeout_s: float,
) -> LifecycleExecutionOutcome:
    stages: list[LifecycleStageOutcome] = []

    for stage in (
        LifecycleStage.SESSION_START,
        LifecycleStage.AVATAR_READY_OR_WARM_ASSUMED,
        LifecycleStage.AUDIO_ACCEPTED,
        LifecycleStage.FIRST_SPEAKING_FRAME_SIGNAL,
    ):
        command = lifecycle_commands.get(stage)
        if not command:
            return LifecycleExecutionOutcome(
                attempted=False,
                success=False,
                stages=stages,
                note=f"missing lifecycle command for stage: {stage.value}",
            )

        outcome = _run_command(
            mode=f"lifecycle:{stage.value}",
            command=command,
            cwd=cwd,
            timeout_s=lifecycle_timeout_s,
        )
        stages.append(LifecycleStageOutcome(stage=stage, outcome=outcome))
        if not outcome.success:
            return LifecycleExecutionOutcome(
                attempted=True,
                success=False,
                stages=stages,
                note=f"stage failed: {stage.value}",
            )

    return LifecycleExecutionOutcome(
        attempted=True,
        success=True,
        stages=stages,
        note="all lifecycle stages passed",
    )


def _check_musetalk_runtime_readiness(
    *,
    musetalk_root: Optional[str],
    command: str,
    required_entrypoint_relpath: Optional[str],
    required_paths_rel: Optional[list[str]],
    dry_run_command: Optional[str],
    dry_run_timeout_s: float,
    executable_smoke_command: Optional[str],
    executable_smoke_timeout_s: float,
    tiny_real_execution_command: Optional[str],
    tiny_real_execution_timeout_s: float,
    lifecycle_commands: Optional[dict[LifecycleStage, str]],
    lifecycle_timeout_s: float,
) -> IntegrationReadiness:
    failures: list[IntegrationFailure] = []
    dry_run_outcome: Optional[SmokeOutcome] = None
    executable_smoke_outcome: Optional[SmokeOutcome] = None
    tiny_real_execution_outcome: Optional[SmokeOutcome] = None
    lifecycle_execution_outcome: Optional[LifecycleExecutionOutcome] = None

    root_path: Optional[Path] = None
    if not musetalk_root:
        failures.append(IntegrationFailure(IntegrationFailureReason.MISSING_ROOT, "musetalk_root was not provided"))
    else:
        root_path = Path(musetalk_root)
        if not root_path.exists():
            failures.append(
                IntegrationFailure(
                    IntegrationFailureReason.ROOT_NOT_FOUND,
                    f"musetalk_root does not exist: {musetalk_root}",
                )
            )

    if command:
        try:
            shlex.split(command)
        except ValueError as exc:
            failures.append(
                IntegrationFailure(
                    IntegrationFailureReason.COMMAND_PARSE_ERROR,
                    f"command is not shell-parseable: {exc}",
                )
            )

    if root_path and root_path.exists() and required_entrypoint_relpath:
        entrypoint_path = root_path / required_entrypoint_relpath
        if not entrypoint_path.exists():
            failures.append(
                IntegrationFailure(
                    IntegrationFailureReason.ENTRYPOINT_MISSING,
                    f"required entrypoint missing: {entrypoint_path}",
                )
            )

    if root_path and root_path.exists() and required_paths_rel:
        for relpath in required_paths_rel:
            candidate = root_path / relpath
            if not candidate.exists():
                failures.append(
                    IntegrationFailure(
                        IntegrationFailureReason.REQUIRED_PATH_MISSING,
                        f"required path missing: {candidate}",
                    )
                )

    if dry_run_command and root_path and root_path.exists():
        dry_run_outcome = _run_command(
            mode="dry_run",
            command=dry_run_command,
            cwd=str(root_path),
            timeout_s=dry_run_timeout_s,
        )
        if not dry_run_outcome.success:
            failures.append(
                IntegrationFailure(
                    IntegrationFailureReason.DRY_RUN_FAILED,
                    (
                        f"dry run failed rc={dry_run_outcome.returncode}; "
                        f"stdout={dry_run_outcome.stdout!r}; stderr={dry_run_outcome.stderr!r}; "
                        f"note={dry_run_outcome.note}"
                    ),
                )
            )
    elif dry_run_command:
        dry_run_outcome = SmokeOutcome(
            attempted=False,
            success=False,
            mode="dry_run",
            command=dry_run_command,
            returncode=None,
            duration_ms=None,
            stdout=None,
            stderr=None,
            note="skipped because musetalk_root is unavailable",
        )

    # Permanent pre-gate before tiny real: executable smoke.
    if executable_smoke_command:
        if root_path and root_path.exists() and not failures:
            executable_smoke_outcome = _run_command(
                mode="executable_smoke",
                command=executable_smoke_command,
                cwd=str(root_path),
                timeout_s=executable_smoke_timeout_s,
            )
        else:
            executable_smoke_outcome = SmokeOutcome(
                attempted=False,
                success=False,
                mode="executable_smoke",
                command=executable_smoke_command,
                returncode=None,
                duration_ms=None,
                stdout=None,
                stderr=None,
                note="skipped because readiness gate did not pass",
            )

    if tiny_real_execution_command:
        if root_path and root_path.exists() and not failures and (
            executable_smoke_outcome is None or executable_smoke_outcome.success
        ):
            tiny_real_execution_outcome = _run_command(
                mode="tiny_real_execution",
                command=tiny_real_execution_command,
                cwd=str(root_path),
                timeout_s=tiny_real_execution_timeout_s,
            )
            if not tiny_real_execution_outcome.success:
                failures.append(
                    IntegrationFailure(
                        IntegrationFailureReason.TINY_REAL_EXECUTION_FAILED,
                        (
                            f"tiny real execution failed rc={tiny_real_execution_outcome.returncode}; "
                            f"stdout={tiny_real_execution_outcome.stdout!r}; "
                            f"stderr={tiny_real_execution_outcome.stderr!r}; "
                            f"note={tiny_real_execution_outcome.note}"
                        ),
                    )
                )
        else:
            tiny_real_execution_outcome = SmokeOutcome(
                attempted=False,
                success=False,
                mode="tiny_real_execution",
                command=tiny_real_execution_command,
                returncode=None,
                duration_ms=None,
                stdout=None,
                stderr=None,
                note="skipped because readiness/smoke gate did not pass",
            )

    if lifecycle_commands:
        if root_path and root_path.exists() and not failures:
            lifecycle_execution_outcome = _run_lifecycle_path(
                cwd=str(root_path),
                lifecycle_commands=lifecycle_commands,
                lifecycle_timeout_s=lifecycle_timeout_s,
            )
            if not lifecycle_execution_outcome.success:
                failures.append(
                    IntegrationFailure(
                        IntegrationFailureReason.LIFECYCLE_STAGE_FAILED,
                        f"lifecycle path failed: {lifecycle_execution_outcome.note}",
                    )
                )
        else:
            lifecycle_execution_outcome = LifecycleExecutionOutcome(
                attempted=False,
                success=False,
                stages=[],
                note="skipped because readiness/tiny-real gates did not pass",
            )

    return IntegrationReadiness(
        is_ready=not failures,
        failures=failures,
        dry_run_outcome=dry_run_outcome,
        executable_smoke_outcome=executable_smoke_outcome,
        tiny_real_execution_outcome=tiny_real_execution_outcome,
        lifecycle_execution_outcome=lifecycle_execution_outcome,
    )


def build_musetalk_command_plan(
    policy_config: str,
    policy_mode: str,
    infer_template: str,
    musetalk_root: Optional[str] = None,
    chunk_ms_override: Optional[int] = None,
    startup_chunks_override: Optional[int] = None,
    required_entrypoint_relpath: Optional[str] = "inference.py",
    required_paths_rel: Optional[list[str]] = None,
    dry_run_command: Optional[str] = None,
    dry_run_timeout_s: float = 2.0,
    executable_smoke_command: Optional[str] = None,
    executable_smoke_timeout_s: float = 3.0,
    tiny_real_execution_command: Optional[str] = None,
    tiny_real_execution_timeout_s: float = 3.0,
    lifecycle_commands: Optional[dict[LifecycleStage, str]] = None,
    lifecycle_timeout_s: float = 1.5,
) -> MuseTalkCommandPlan:
    """Build a policy-informed command plan and verify staged integration readiness.

    This remains explicitly non-production and does not claim full end-to-end
    MuseTalk runtime/session orchestration.
    """
    policy = resolve_policy(
        policy_path=policy_config,
        policy_mode=policy_mode,
        chunk_ms_override=chunk_ms_override,
        startup_chunks_override=startup_chunks_override,
    )

    command, render_failure = _render_command(
        infer_template=infer_template,
        musetalk_root=musetalk_root,
        policy=policy,
    )

    readiness = _check_musetalk_runtime_readiness(
        musetalk_root=musetalk_root,
        command=command,
        required_entrypoint_relpath=required_entrypoint_relpath,
        required_paths_rel=required_paths_rel,
        dry_run_command=dry_run_command,
        dry_run_timeout_s=dry_run_timeout_s,
        executable_smoke_command=executable_smoke_command,
        executable_smoke_timeout_s=executable_smoke_timeout_s,
        tiny_real_execution_command=tiny_real_execution_command,
        tiny_real_execution_timeout_s=tiny_real_execution_timeout_s,
        lifecycle_commands=lifecycle_commands,
        lifecycle_timeout_s=lifecycle_timeout_s,
    )

    if render_failure is not None:
        readiness = IntegrationReadiness(
            is_ready=False,
            failures=[render_failure, *readiness.failures],
            dry_run_outcome=readiness.dry_run_outcome,
            executable_smoke_outcome=readiness.executable_smoke_outcome,
            tiny_real_execution_outcome=readiness.tiny_real_execution_outcome,
            lifecycle_execution_outcome=readiness.lifecycle_execution_outcome,
        )

    return MuseTalkCommandPlan(
        policy=policy,
        command=command,
        is_real_runtime_available=readiness.is_ready,
        musetalk_root=musetalk_root,
        readiness=readiness,
    )
