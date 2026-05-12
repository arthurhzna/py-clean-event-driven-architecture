from yoyo import step

steps = [
    step(
        """
        CREATE TABLE IF NOT EXISTS device (
            device_id     VARCHAR(255) PRIMARY KEY,
            is_registered BOOLEAN      NOT NULL DEFAULT FALSE
        );
        """,
        """
        DROP TABLE IF EXISTS device;
        """
    ),
]