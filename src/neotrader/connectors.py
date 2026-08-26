from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Protocol


@dataclass(frozen=True)
class ConnectorMessage:
    connector: str
    direction: str
    kind: str
    correlation_id: str
    payload: dict[str, Any]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class BidirectionalConnector(Protocol):
    name: str

    def send(self, message: ConnectorMessage) -> None: ...
    def receive(self) -> list[ConnectorMessage]: ...


class InMemoryConnector:
    """Deterministic bidirectional connector used by the integration layer and tests."""

    def __init__(self, name: str) -> None:
        self.name = name
        self._inbound: list[ConnectorMessage] = []
        self._outbound: list[ConnectorMessage] = []

    def send(self, message: ConnectorMessage) -> None:
        if message.connector != self.name:
            raise ValueError(f"connector mismatch: {message.connector} != {self.name}")
        self._outbound.append(message)

    def inject(self, message: ConnectorMessage) -> None:
        if message.connector != self.name:
            raise ValueError(f"connector mismatch: {message.connector} != {self.name}")
        self._inbound.append(message)

    def receive(self) -> list[ConnectorMessage]:
        messages = self._inbound[:]
        self._inbound.clear()
        return messages

    @property
    def outbound(self) -> tuple[ConnectorMessage, ...]:
        return tuple(self._outbound)


@dataclass
class ConnectorRegistry:
    """Single registry for all external input/output channels."""

    connectors: dict[str, BidirectionalConnector] = field(default_factory=dict)

    def register(self, connector: BidirectionalConnector) -> None:
        if connector.name in self.connectors:
            raise ValueError(f"connector already registered: {connector.name}")
        self.connectors[connector.name] = connector

    def get(self, name: str) -> BidirectionalConnector:
        try:
            return self.connectors[name]
        except KeyError as exc:
            raise KeyError(f"unknown connector: {name}") from exc

    def send(self, message: ConnectorMessage) -> None:
        self.get(message.connector).send(message)

    def receive_all(self) -> list[ConnectorMessage]:
        messages: list[ConnectorMessage] = []
        for connector in self.connectors.values():
            messages.extend(connector.receive())
        return messages
