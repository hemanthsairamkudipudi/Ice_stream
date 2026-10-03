from typing import Any

from pyiceberg.catalog import load_catalog


def load_checkout_table():
    catalog = load_catalog(
        "iceberg_catalog",
        type="rest",
        uri="http://localhost:8181",
        warehouse="s3://warehouse/",
        **{
            "s3.endpoint": "http://localhost:9000",
            "s3.access-key-id": "admin",
            "s3.secret-access-key": "password",
            "s3.path-style-access": "true",
        },
    )

    return catalog.load_table(("checkout", "checkout_events"))


def read_checkout_records() -> list[dict[str, Any]]:
    table = load_checkout_table()

    arrow_table = table.scan().to_arrow()

    return arrow_table.to_pylist()