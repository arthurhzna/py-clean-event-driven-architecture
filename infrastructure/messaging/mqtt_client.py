from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable
from urllib.parse import urlparse
import paho.mqtt.client as mqtt

logger = logging.getLogger(__name__)


def _parse_broker_url(url: str) -> tuple[str, int, bool]:
    parsed = urlparse(url)
    scheme = (parsed.scheme or "mqtt").lower()
    host = parsed.hostname or "localhost"
    if parsed.port is not None:
        port = parsed.port
    elif scheme in ("mqtts", "ssl"):
        port = 8883
    else:
        port = 1883
    use_tls = scheme in ("mqtts", "ssl")
    return host, port, use_tls


@dataclass(slots=True)
class MqttClient:
    broker_url: str
    on_connect: Callable[..., Any] | None = None
    on_message: Callable[[str, bytes], None] | None = None
    _paho: Any | None = field(init=False, default=None, repr=False)

    def connect(self, keepalive: int = 60) -> None:


        if self._paho is not None:
            self.disconnect()

        host, port, use_tls = _parse_broker_url(self.broker_url)

        def _cb_connect(client: Any, userdata: Any, flags: Any, rc: int) -> None:
            if rc != 0:
                logger.error("MQTT broker connection failed rc=%s", rc)
                return
            logger.info("MQTT connected to %s:%s", host, port)
            if self.on_connect:
                self.on_connect(client, userdata, flags, rc)

        def _cb_message(client: Any, userdata: Any, msg: Any) -> None:
            if not self.on_message:
                return
            topic = msg.topic.decode() if isinstance(msg.topic, bytes) else msg.topic
            payload = msg.payload if isinstance(msg.payload, bytes) else bytes(msg.payload)
            try:
                self.on_message(topic, payload)
            except Exception:
                logger.exception("MQTT on_message handler failed topic=%s", topic)

        client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION1)
        client.on_connect = _cb_connect
        client.on_message = _cb_message
        if use_tls:
            client.tls_set()

        client.connect(host, port, keepalive=keepalive)
        client.loop_start()
        self._paho = client

    def disconnect(self) -> None:
        if self._paho is None:
            return
        self._paho.loop_stop()
        self._paho.disconnect()
        self._paho = None

    def subscribe(self, topic: str, qos: int = 0) -> None:
        if self._paho is None:
            raise RuntimeError("MQTT client not connected; call connect() first")
        self._paho.subscribe(topic, qos)

    def publish(self, topic: str, payload: bytes, qos: int = 0) -> None:
        if self._paho is None:
