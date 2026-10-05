from migration_engine.normalizers import (
    normalize_date,
    normalize_email,
    normalize_name,
    normalize_phone,
)


def test_normalize_philippine_phone_from_local_format():
    assert normalize_phone("0917 123 4567", "Philippines") == "+639171234567"


def test_normalize_philippine_phone_without_zero():
    assert normalize_phone("9171234567", "Philippines") == "+639171234567"


def test_normalize_email():
    assert normalize_email(" Test.User@Example.COM ") == "test.user@example.com"


def test_normalize_name():
    assert normalize_name("  juan   dela cruz ") == "Juan Dela Cruz"


def test_normalize_date():
    assert normalize_date("09/05/1995") == "1995-09-05"
