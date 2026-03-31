import json
import tempfile
import unittest
from pathlib import Path

from runtime.session.musetalk_integration import (
    IntegrationFailureReason,
    LifecycleStage,
    build_musetalk_command_plan,
)


class MuseTalkIntegrationTests(unittest.TestCase):
    def _make_policy(self) -> str:
        payload = {
            "default": {"chunk_ms": 120, "startup_chunks": 3},
            "fallback": {"chunk_ms": 160, "startup_chunks": 2},
            "aggressive_not_default": [{"chunk_ms": 80, "startup_chunks": 4}],
        }
        tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
        tmp.write(json.dumps(payload))
        tmp.flush()
        tmp.close()
        return tmp.name

    def test_policy_override_precedence_is_kept(self) -> None:
        policy_path = self._make_policy()
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "inference.py").write_text("print('ok')\n")
            plan = build_musetalk_command_plan(
                policy_config=policy_path,
                policy_mode="default",
                infer_template="python {musetalk_root}/inference.py --chunk {chunk_ms} --startup {startup_chunks}",
                musetalk_root=str(root),
                chunk_ms_override=240,
                startup_chunks_override=5,
                dry_run_command="python -c \"print('dry-run-ok')\"",
            )
        self.assertEqual(plan.policy.chunk_ms, 240)
        self.assertEqual(plan.policy.startup_chunks, 5)
        self.assertTrue(plan.is_real_runtime_available)

    def test_missing_entrypoint_is_classified(self) -> None:
        policy_path = self._make_policy()
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            plan = build_musetalk_command_plan(
                policy_config=policy_path,
                policy_mode="default",
                infer_template="python {musetalk_root}/inference.py --chunk {chunk_ms}",
                musetalk_root=str(root),
                required_entrypoint_relpath="inference.py",
            )
        reasons = {f.reason for f in plan.readiness.failures}
        self.assertIn(IntegrationFailureReason.ENTRYPOINT_MISSING, reasons)

    def test_lifecycle_path_success(self) -> None:
        policy_path = self._make_policy()
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "inference.py").write_text("print('ok')\n")
            (root / "smoke.py").write_text("print('smoke')\n")
            (root / "tiny_real.py").write_text("print('tiny')\n")
            plan = build_musetalk_command_plan(
                policy_config=policy_path,
                policy_mode="default",
                infer_template="python {musetalk_root}/inference.py --chunk {chunk_ms}",
                musetalk_root=str(root),
                dry_run_command="python -c \"print('dry')\"",
                executable_smoke_command="python smoke.py",
                tiny_real_execution_command="python tiny_real.py",
                lifecycle_commands={
                    LifecycleStage.SESSION_START: "python -c \"print('session-start')\"",
                    LifecycleStage.AVATAR_READY_OR_WARM_ASSUMED: "python -c \"print('avatar-ready')\"",
                    LifecycleStage.AUDIO_ACCEPTED: "python -c \"print('audio-accepted')\"",
                    LifecycleStage.FIRST_SPEAKING_FRAME_SIGNAL: "python -c \"print('first-frame')\"",
                },
            )

        self.assertTrue(plan.readiness.readiness_passed)
        self.assertTrue(plan.readiness.dry_run_passed)
        self.assertTrue(plan.readiness.executable_smoke_passed)
        self.assertTrue(plan.readiness.tiny_real_execution_passed)
        self.assertTrue(plan.readiness.lifecycle_execution_passed)
        self.assertEqual(len(plan.readiness.lifecycle_execution_outcome.stages), 4)

    def test_lifecycle_failure_is_classified(self) -> None:
        policy_path = self._make_policy()
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "inference.py").write_text("print('ok')\n")
            (root / "smoke.py").write_text("print('smoke')\n")
            (root / "tiny_real.py").write_text("print('tiny')\n")
            plan = build_musetalk_command_plan(
                policy_config=policy_path,
                policy_mode="default",
                infer_template="python {musetalk_root}/inference.py --chunk {chunk_ms}",
                musetalk_root=str(root),
                dry_run_command="python -c \"print('dry')\"",
                executable_smoke_command="python smoke.py",
                tiny_real_execution_command="python tiny_real.py",
                lifecycle_commands={
                    LifecycleStage.SESSION_START: "python -c \"print('session-start')\"",
                    LifecycleStage.AVATAR_READY_OR_WARM_ASSUMED: "python -c \"import sys; sys.exit(7)\"",
                    LifecycleStage.AUDIO_ACCEPTED: "python -c \"print('audio-accepted')\"",
                    LifecycleStage.FIRST_SPEAKING_FRAME_SIGNAL: "python -c \"print('first-frame')\"",
                },
            )

        reasons = {f.reason for f in plan.readiness.failures}
        self.assertIn(IntegrationFailureReason.LIFECYCLE_STAGE_FAILED, reasons)
        self.assertFalse(plan.readiness.lifecycle_execution_passed)


if __name__ == "__main__":
    unittest.main()
