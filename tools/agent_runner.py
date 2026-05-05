#!/usr/bin/env python3
"""Agent provider adapters for changelog generation."""

from __future__ import annotations

import asyncio
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Sequence


SUPPORTED_AGENT_PROVIDERS = ("claude", "codex")


class AgentRunnerError(RuntimeError):
    """Raised when an agent provider cannot complete a request."""


def _tail(text: str, max_chars: int = 4000) -> str:
    if len(text) <= max_chars:
        return text
    return text[-max_chars:]


def get_isolated_claude_config() -> Path:
    """Return an isolated CLAUDE_CONFIG_DIR for SDK tasks.

    Sessions are written to ~/.claude/projects/harness-investigations/projects/...
    so ccusage finds them automatically and groups them under the project name
    "harness-investigations". They do not appear in --resume because real
    project dirs start with hyphenated cwd paths; this dir does not.
    """
    user_claude = Path.home() / ".claude"
    claude_dir = user_claude / "projects" / "harness-investigations"
    claude_dir.mkdir(parents=True, exist_ok=True)

    for fname in (".credentials.json", "settings.json"):
        src = user_claude / fname
        dst = claude_dir / fname
        if src.exists() and not dst.exists():
            dst.symlink_to(src)

    return claude_dir


@dataclass(frozen=True)
class AgentRunRequest:
    prompt: str
    system_prompt: str = ""
    cwd: Path = field(default_factory=Path.cwd)
    allowed_tools: Optional[Sequence[str]] = None
    env: Optional[dict[str, str]] = None
    timeout: Optional[int] = None


class BaseAgentRunner:
    provider = "base"
    supports_file_write_tool = False

    def check_available(self) -> None:
        raise NotImplementedError

    def run(self, request: AgentRunRequest) -> str:
        raise NotImplementedError


class ClaudeSdkRunner(BaseAgentRunner):
    provider = "claude"
    supports_file_write_tool = True

    def __init__(self, model: Optional[str] = None):
        self.model = model

    def check_available(self) -> None:
        try:
            import claude_agent_sdk  # noqa: F401
        except ImportError as exc:
            raise AgentRunnerError(
                "claude-agent-sdk is not installed. Install with: pip install claude-agent-sdk"
            ) from exc

    def run(self, request: AgentRunRequest) -> str:
        from claude_agent_sdk import ClaudeAgentOptions, ResultMessage, query

        env = dict(request.env or {})
        env.setdefault("CLAUDE_CONFIG_DIR", str(get_isolated_claude_config()))

        kwargs = {
            "system_prompt": request.system_prompt,
            "allowed_tools": list(request.allowed_tools or []),
            "permission_mode": "bypassPermissions",
            "cwd": str(request.cwd),
            "env": env,
        }
        if self.model:
            kwargs["model"] = self.model

        options = ClaudeAgentOptions(**kwargs)

        async def _execute() -> str:
            result = ""
            async for msg in query(prompt=request.prompt, options=options):
                if isinstance(msg, ResultMessage):
                    if msg.is_error:
                        raise AgentRunnerError(msg.result or "Claude query failed")
                    result = msg.result or ""
            return result

        if request.timeout:
            async def _with_timeout() -> str:
                return await asyncio.wait_for(_execute(), timeout=request.timeout)

            return asyncio.run(_with_timeout())

        return asyncio.run(_execute())


class CodexExecRunner(BaseAgentRunner):
    provider = "codex"
    supports_file_write_tool = False

    def __init__(
        self,
        model: Optional[str] = None,
        reasoning_effort: Optional[str] = None,
        executable: str = "codex",
    ):
        self.model = model
        self.reasoning_effort = reasoning_effort
        self.executable = executable

    def check_available(self) -> None:
        if shutil.which(self.executable) is None:
            raise AgentRunnerError(f"{self.executable!r} was not found on PATH")

    def run(self, request: AgentRunRequest) -> str:
        self.check_available()

        cwd = Path(request.cwd).resolve()
        with tempfile.NamedTemporaryFile("w+", encoding="utf-8", delete=False) as tmp:
            output_path = Path(tmp.name)

        try:
            cmd = [self.executable]
            if self.model:
                cmd.extend(["--model", self.model])
            if self.reasoning_effort:
                cmd.extend([
                    "--config",
                    f'model_reasoning_effort="{self.reasoning_effort}"',
                ])
            cmd.extend([
                "--sandbox",
                "read-only",
                "--ask-for-approval",
                "never",
                "--cd",
                str(cwd),
                "exec",
                "--ephemeral",
                "--ignore-rules",
                "--output-last-message",
                str(output_path),
                "--color",
                "never",
                "-",
            ])

            env = os.environ.copy()
            if request.env:
                env.update(request.env)

            prompt = self._compose_prompt(request)
            completed = subprocess.run(
                cmd,
                input=prompt,
                text=True,
                capture_output=True,
                cwd=str(cwd),
                env=env,
                timeout=request.timeout,
                check=False,
            )

            output = output_path.read_text(encoding="utf-8", errors="replace")
            if completed.returncode != 0:
                detail = "\n".join(
                    part for part in (
                        f"codex exec exited with code {completed.returncode}",
                        "stdout tail:",
                        _tail(completed.stdout),
                        "stderr tail:",
                        _tail(completed.stderr),
                        "last-message tail:",
                        _tail(output),
                    )
                    if part
                )
                raise AgentRunnerError(detail)

            return output.strip() or completed.stdout.strip()
        finally:
            output_path.unlink(missing_ok=True)

    @staticmethod
    def _compose_prompt(request: AgentRunRequest) -> str:
        parts = []
        if request.system_prompt.strip():
            parts.append(
                "Treat the following as the task instructions that govern this run.\n"
                "<task_instructions>\n"
                f"{request.system_prompt.strip()}\n"
                "</task_instructions>"
            )

        if request.allowed_tools is not None:
            tools = ", ".join(request.allowed_tools) or "none"
            parts.append(
                "Tool policy for this run: use only read-only inspection commands "
                f"equivalent to these capabilities: {tools}. Do not edit files."
            )

        parts.append(request.prompt.strip())
        return "\n\n".join(parts).strip() + "\n"


def make_agent_runner(
    provider: str,
    model: Optional[str] = None,
    reasoning_effort: Optional[str] = None,
    executable: str = "codex",
) -> BaseAgentRunner:
    provider = provider.lower()
    if provider == "claude":
        return ClaudeSdkRunner(model=model)
    if provider == "codex":
        return CodexExecRunner(
            model=model,
            reasoning_effort=reasoning_effort,
            executable=executable,
        )
    raise AgentRunnerError(
        f"Unsupported agent provider {provider!r}; choose one of: "
        f"{', '.join(SUPPORTED_AGENT_PROVIDERS)}"
    )


def default_model_for(provider: str, role: str) -> str:
    provider = provider.lower()
    role = role.lower()
    if provider == "claude":
        return (
            "claude-haiku-4-5-20251001"
            if role == "annotation"
            else "claude-sonnet-4-6"
        )
    if provider == "codex":
        return "gpt-5.4-mini" if role == "annotation" else "gpt-5.5"
    raise AgentRunnerError(f"Unsupported agent provider {provider!r}")
