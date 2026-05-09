from __future__ import annotations

from threading import Lock
from typing import Any, Callable

import paho.mqtt.client as mqtt


class MqttClient:
    def __init__(
        self,
        broker: str,
        port: int,
        client_id: str,
        username: str | None = None,
        password: str | None = None,
        use_tls: bool = False,
    ) -> None:

        self._broker = broker
        self._port = port
        self._client_id = client_id
        self._username = username
        self._password = password
        self._use_tls = use_tls

        self._paho: mqtt.Client | None = None

        self._connected = False

        self._subscriptions: list[
            tuple[str, int]
        ] = []

        self._publish_lock = Lock()

        self.on_connect: (
            Callable[..., Any] | None
        ) = None

        self.on_disconnect: (
            Callable[..., Any] | None
        ) = None

        self.on_message: (
            Callable[[str, bytes], None]
            | None
        ) = None

    @property
    def is_connected(
        self,
    ) -> bool:

        return self._connected

    def connect(
        self,
        keepalive: int = 60,
    ) -> None:

        if self._paho is not None:
            self.disconnect()

        def _cb_connect(
            client: Any,
            userdata: Any,
            flags: Any,
            rc: int,
        ) -> None:

            if rc != 0:
                self._connected = False
                return

            self._connected = True

            for topic, qos in (
                self._subscriptions
            ):

                client.subscribe(
                    topic,
                    qos,
                )

            if self.on_connect:

                self.on_connect(
                    client,
                    userdata,
                    flags,
                    rc,
                )

        def _cb_disconnect(
            client: Any,
            userdata: Any,
            rc: int,
        ) -> None:

            self._connected = False

            if self.on_disconnect:

                self.on_disconnect(
                    client,
                    userdata,
                    rc,
                )

        def _cb_message(
            client: Any,
            userdata: Any,
            msg: Any,
        ) -> None:

            if not self.on_message:
                return

            topic = (
                msg.topic.decode()
                if isinstance(
                    msg.topic,
                    bytes,
                )
                else msg.topic
            )

            payload = (
                msg.payload
                if isinstance(
                    msg.payload,
                    bytes,
                )
                else bytes(
                    msg.payload,
                )
            )

            self.on_message(
                topic,
                payload,
            )

        client = mqtt.Client(
            client_id=self._client_id,
            callback_api_version=(
                mqtt.CallbackAPIVersion.VERSION1
            ),
        )

        if self._username:

            client.username_pw_set(
                username=self._username,
                password=self._password,
            )

        if self._use_tls:
            client.tls_set()

        client.reconnect_delay_set(
            min_delay=1,
            max_delay=30,
        )

        client.on_connect = (
            _cb_connect
        )

        client.on_disconnect = (
            _cb_disconnect
        )

        client.on_message = (
            _cb_message
        )

        client.connect(
            self._broker,
            self._port,
            keepalive=keepalive,
        )

        client.loop_start()

        self._paho = client

    def disconnect(
        self,
    ) -> None:

        if self._paho is None:
            return

        self._connected = False

        self._paho.loop_stop()

        self._paho.disconnect()

        self._paho = None

    def subscribe(
        self,
        topics: list[tuple[str, int]],
    ) -> None:

        for topic, qos in topics:

            subscription = (
                topic,
                qos,
            )

            if subscription not in (
                self._subscriptions
            ):

                self._subscriptions.append(
                    subscription,
                )

            if (
                self._paho is not None
                and self._connected
            ):

                self._paho.subscribe(
                    topic,
                    qos,
                )

    def publish(
        self,
        topic: str,
        payload: bytes,
        qos: int = 0,
    ) -> None:

        if self._paho is None:

            raise RuntimeError(
                "MQTT client not connected",
            )

        with self._publish_lock:

            self._paho.publish(
                topic,
                payload,
                qos=qos,
            )