"""Direct Composio tool discovery and execution for web research."""

import json
import os
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from agent.ssl_config import configure_ssl


class ComposioUnavailable(RuntimeError):
    pass


def _tool_data(tool: Any) -> dict[str, Any]:
    if hasattr(tool, "model_dump"):
        return tool.model_dump(exclude_none=True)
    return dict(tool) if isinstance(tool, dict) else {}


def _properties(tool: dict[str, Any]) -> set[str]:
    schema = tool.get("input_parameters", {})
    properties = schema.get("properties", {}) if isinstance(schema, dict) else {}
    return set(properties) if isinstance(properties, dict) else set()


def _select_capability(
    tools: list[dict[str, Any]], capability: str
) -> dict[str, Any]:
    """Select a current tool by input schema and descriptive capability signals."""
    scored: list[tuple[int, str, dict[str, Any]]] = []
    for tool in tools:
        deprecated = tool.get("deprecated")
        deprecated_flag = (
            deprecated.get("is_deprecated", False)
            if isinstance(deprecated, dict)
            else bool(deprecated)
        )
        if deprecated_flag or tool.get("is_deprecated"):
            continue
        slug = str(tool.get("slug", ""))
        label = " ".join(
            str(tool.get(key, "")) for key in ("slug", "name", "description")
        ).lower()
        inputs = _properties(tool)
        score = 0
        if capability == "search" and "query" in inputs:
            score = 20
            score += 8 if " web " in f" {label} " else 0
            score += 5 if "search" in label else 0
            score -= 10 if any(
                term in label
                for term in (
                    "amazon",
                    "event",
                    "finance",
                    "flight",
                    "hotel",
                    "image",
                    "map",
                    "news",
                    "scholar",
                    "shopping",
                    "tripadvisor",
                    "walmart",
                )
            ) else 0
        elif capability == "fetch" and inputs.intersection({"url", "urls"}):
            score = 20
            score += sum(5 for term in ("fetch", "url", "content", "page") if term in label)
        if score:
            scored.append((score, slug, tool))
    if not scored:
        raise ComposioUnavailable(
            f"composio_search exposes no {capability} capability with a compatible schema"
        )
    return max(scored, key=lambda item: (item[0], item[1]))[2]


class ComposioDirectAdapter:
    """Discover and execute Composio Search tools without Tool Router Sessions."""

    execution_mode = "direct_tool_execution"

    def __init__(self, api_key: str, artifact_path: Path):
        self.api_key = api_key
        self.artifact_path = artifact_path
        self._log_handle = artifact_path.open("a", encoding="utf-8")
        self.client: Any = None
        self.search_tool: dict[str, Any] = {}
        self.fetch_tool: dict[str, Any] = {}
        self.discovered_slugs: list[str] = []

    def __enter__(self) -> "ComposioDirectAdapter":
        os.environ.setdefault(
            "COMPOSIO_CACHE_DIR", str(Path(".composio-cache").resolve())
        )
        configure_ssl()
        try:
            from composio import Composio
        except ImportError as error:
            self._log_handle.close()
            raise ComposioUnavailable(
                "install composio before live research"
            ) from error
        try:
            self.client = Composio(api_key=self.api_key)
            response = self.client.client.tools.list(
                toolkit_slug="composio_search", limit=100
            )
            payload = _tool_data(response)
            tools = [_tool_data(tool) for tool in payload.get("items", [])]
            self.discovered_slugs = [
                str(tool["slug"]) for tool in tools if tool.get("slug")
            ]
            self.search_tool = _select_capability(tools, "search")
            self.fetch_tool = _select_capability(tools, "fetch")
            self._log(
                {
                    "event": "tool_discovery",
                    "discovered_slugs": self.discovered_slugs,
                    "search_tool_slug": self.search_tool["slug"],
                    "fetch_tool_slug": self.fetch_tool["slug"],
                }
            )
        except Exception:
            self._log_handle.close()
            raise
        return self

    def __exit__(self, *_: object) -> None:
        self._log_handle.close()

    def _log(self, payload: dict[str, Any]) -> None:
        record = {
            "execution_mode": self.execution_mode,
            "timestamp": datetime.now(UTC).isoformat(),
            **payload,
        }
        self._log_handle.write(json.dumps(record, default=str) + "\n")
        self._log_handle.flush()

    @staticmethod
    def _jsonable(value: Any) -> Any:
        if hasattr(value, "model_dump"):
            return value.model_dump(mode="json")
        if isinstance(value, dict | list | str | int | float | bool) or value is None:
            return value
        return str(value)

    def _sanitize_error(self, error: Exception) -> str:
        message = str(error).replace(self.api_key, "[REDACTED]")
        return re.sub(r"\s+", " ", message).strip()[:2000]

    def _execute(self, tool: dict[str, Any], arguments: dict[str, Any]) -> Any:
        slug = str(tool["slug"])
        version = str(tool.get("version", ""))
        try:
            response = self.client.tools.execute(
                slug,
                arguments,
                user_id="composio100-salesforce",
                version=version or None,
            )
            result = self._jsonable(response)
            successful = not isinstance(result, dict) or result.get("successful", True)
            sanitized_error = None if successful else str(result.get("error") or "tool failed")
            self._log(
                {
                    "tool_slug": slug,
                    "tool_input": arguments,
                    "success": successful,
                    "sanitized_error": sanitized_error,
                    "result": result,
                }
            )
            if not successful:
                raise ComposioUnavailable(f"{slug} failed: {sanitized_error}")
            return result
        except Exception as error:
            if not isinstance(error, ComposioUnavailable):
                sanitized_error = self._sanitize_error(error)
                self._log(
                    {
                        "tool_slug": slug,
                        "tool_input": arguments,
                        "success": False,
                        "sanitized_error": sanitized_error,
                    }
                )
                raise ComposioUnavailable(
                    f"direct execution failed for {slug}: {sanitized_error}"
                ) from error
            raise

    def search(self, query: str) -> Any:
        return self._execute(self.search_tool, {"query": query})

    def fetch(self, url: str) -> Any:
        inputs = _properties(self.fetch_tool)
        arguments: dict[str, Any] = {"urls": [url]} if "urls" in inputs else {"url": url}
        if "text" in inputs:
            arguments["text"] = True
        if "max_characters" in inputs:
            arguments["max_characters"] = 50_000
        return self._execute(self.fetch_tool, arguments)
