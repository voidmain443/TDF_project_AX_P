"""Fetcher protocol + Proframe XML envelope builder."""

from __future__ import annotations

from typing import Protocol, runtime_checkable
from xml.sax.saxutils import escape

from ..config import ServiceSpec


@runtime_checkable
class Fetcher(Protocol):
    """Anything that can turn a service request into raw response bytes."""

    def fetch(self, spec: ServiceSpec, params: dict) -> bytes: ...


def build_envelope(spec: ServiceSpec, params: dict) -> bytes:
    """Build the Proframe ``<message>`` request body for a service call."""
    parts = [
        '<?xml version="1.0" encoding="utf-8"?>',
        "<message>",
        "<proframeHeader>",
        f"<pfmAppName>{escape(spec.app_name)}</pfmAppName>",
        f"<pfmSvcName>{escape(spec.service_name)}</pfmSvcName>",
        f"<pfmFnName>{escape(spec.function_name)}</pfmFnName>",
        "</proframeHeader>",
        "<systemHeader></systemHeader>",
        f"<{spec.input_dto}>",
    ]
    for key, value in params.items():
        text = "" if value is None else escape(str(value))
        parts.append(f"<{key}>{text}</{key}>")
    parts.append(f"</{spec.input_dto}>")
    parts.append("</message>")
    return "".join(parts).encode("utf-8")
