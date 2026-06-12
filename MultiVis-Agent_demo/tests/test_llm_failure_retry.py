#!/usr/bin/env python3
"""Regression test for LLM failures that should surface to the UI."""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from vis_system.utils.Agent import Agent


class _AlwaysFailingCompletions:
    def __init__(self):
        self.calls = 0

    def create(self, **_kwargs):
        self.calls += 1
        raise RuntimeError("quota exhausted")


class _AlwaysFailingClient:
    def __init__(self):
        self.chat = type("Chat", (), {})()
        self.chat.completions = _AlwaysFailingCompletions()


def main():
    os.environ["MULTIVIS_LLM_MAX_RETRIES"] = "2"
    os.environ["MULTIVIS_LLM_RETRY_SLEEP_SECONDS"] = "0"

    client = _AlwaysFailingClient()
    agent = Agent.__new__(Agent)
    logs = []
    agent._log = logs.append

    try:
        agent.call_llm([{"role": "user", "content": "hello"}], client, "fake-model")
    except RuntimeError as exc:
        assert "LLM request failed after 2 attempts" in str(exc), str(exc)
    else:
        raise AssertionError("call_llm should raise after bounded retries")

    assert client.chat.completions.calls == 2, client.chat.completions.calls
    assert len(logs) == 2, logs
    print("ALL LLM FAILURE RETRY TESTS PASSED")


if __name__ == "__main__":
    main()
