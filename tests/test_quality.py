from quality.engine import DataQualityEngine


def valid_record():
    return {
        "order_id": "ORD100001",
        "customer_id": "CUS001",
        "product_id": "P101",
        "amount": 1000.0,
        "tax_amount": 180.0,
        "payment_status": "SUCCESS",
    }


def test_valid_record_passes():
    engine = DataQualityEngine()

    result = engine.validate_batch([valid_record()])

    assert result.passed is True
    assert result.errors == []


def test_null_order_id_fails():
    record = valid_record()
    record["order_id"] = None

    engine = DataQualityEngine()

    result = engine.validate_batch([record])

    assert result.passed is False
    assert "order_id must not be NULL" in result.errors[0]


def test_null_customer_id_fails():
    record = valid_record()
    record["customer_id"] = None

    engine = DataQualityEngine()

    result = engine.validate_batch([record])

    assert result.passed is False
    assert "customer_id must not be NULL" in result.errors[0]


def test_null_amount_fails():
    record = valid_record()
    record["amount"] = None

    engine = DataQualityEngine()

    result = engine.validate_batch([record])

    assert result.passed is False
    assert "amount must not be NULL" in result.errors[0]


def test_negative_amount_fails():
    record = valid_record()
    record["amount"] = -100.0

    engine = DataQualityEngine()

    result = engine.validate_batch([record])

    assert result.passed is False
    assert any("amount must be >= 0" in error for error in result.errors)


def test_tax_null_below_threshold_passes():
    records = [valid_record() for _ in range(10)]

    records[0]["tax_amount"] = None

    engine = DataQualityEngine(null_threshold=0.10)

    result = engine.validate_batch(records)

    assert result.passed is True
    assert result.null_tax_rate == 0.10


def test_tax_null_above_threshold_fails():
    records = [valid_record() for _ in range(10)]

    records[0]["tax_amount"] = None
    records[1]["tax_amount"] = None

    engine = DataQualityEngine(null_threshold=0.10)

    result = engine.validate_batch(records)

    assert result.passed is False
    assert result.null_tax_rate == 0.20


def test_multiple_errors_are_detected():
    record = valid_record()
    record["order_id"] = None
    record["amount"] = -500.0

    engine = DataQualityEngine()

    result = engine.validate_batch([record])

    assert result.passed is False
    assert len(result.errors) >= 2