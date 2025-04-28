import pytest
import tempfile
import os

from kkk import parse_logs, generate_report

log_content = """
2025-03-26 12:03:00,000 INFO django.request: GET /api/v1/reviews/ 204 OK
2025-03-26 12:45:32,000 WARNING django.security: ConnectionError: Failed to connect to payment gateway
2025-03-26 12:49:53,000 ERROR django.request: Internal Server Error: /api/v1/orders/
2025-03-26 12:05:59,000 DEBUG django.db.backends: (0.6) SELECT * FROM ...
2025-03-26 13:00:00,000 INFO django.request: POST /api/v1/cart/ 201 Created
"""

@pytest.fixture
def temp_log_file():
    with tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8') as f:
        f.write(log_content)
        f.flush()
        yield f.name
    os.remove(f.name)

def test_parse_logs(temp_log_file):
    result = parse_logs([temp_log_file])
    assert '/api/v1/reviews/' in result
    assert '/api/v1/cart/' in result
    assert '/api/v1/orders/' in result
    assert result['/api/v1/reviews/']['INFO'] == 1
    assert result['/api/v1/orders/']['ERROR'] == 1
    assert result['/api/v1/cart/']['INFO'] == 1

def test_generate_report(temp_log_file):
    handler_stats = parse_logs([temp_log_file])

    with tempfile.NamedTemporaryFile(delete=False, mode='r+', encoding='utf-8') as output:
        generate_report(handler_stats, output.name)
        output.seek(0)
        content = output.read()

        assert "Total requests:" in content
        assert "/api/v1/reviews/" in content
        assert "/api/v1/cart/" in content
        assert "/api/v1/orders/" in content
        assert "INFO" in content
        assert "ERROR" in content
