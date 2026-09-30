from generator.checkout_generator import CheckoutGenerator


def test_generate_event_contains_required_fields():
    generator = CheckoutGenerator()

    event = generator.generate_event()

    required_fields = {
        "order_id",
        "customer_id",
        "product_id",
        "amount",
        "tax_amount",
        "payment_status",
        "timestamp",
    }

    assert required_fields.issubset(event.keys())


def test_order_id_has_expected_format():
    generator = CheckoutGenerator()

    event = generator.generate_event()

    assert event["order_id"].startswith("ORD")


def test_customer_id_has_expected_format():
    generator = CheckoutGenerator()

    event = generator.generate_event()

    assert event["customer_id"].startswith("CUS")


def test_amount_is_numeric_or_negative_numeric():
    generator = CheckoutGenerator()

    event = generator.generate_event()

    assert isinstance(event["amount"], (int, float))


def test_tax_amount_is_numeric_or_null():
    generator = CheckoutGenerator()

    event = generator.generate_event()

    assert (
        event["tax_amount"] is None
        or isinstance(event["tax_amount"], (int, float))
    )