import pytest

from quality.iceberg_reader import read_checkout_records_at_snapshot


def test_read_checkout_records_at_snapshot_invalid_id():
    with pytest.raises(ValueError, match="Iceberg snapshot not found"):
        read_checkout_records_at_snapshot(999999999999999999)