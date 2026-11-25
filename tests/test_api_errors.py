from core.api_errors import explain_api_error, parse_api_error


def test_explain_429():
    msg = explain_api_error("429 Too Many Requests")
    assert "rate limit" in msg.lower() or "429" in msg


def test_explain_quota():
    msg = explain_api_error("RESOURCE_EXHAUSTED: quota exceeded for project")
    assert "quota" in msg.lower()


def test_explain_short():
    msg = explain_api_error(RuntimeError("connection reset"))
    assert "connection reset" in msg.lower()


def test_parse_returns_detail():
    exc = RuntimeError("429 Too Many Requests: trial ended")
    reason, detail = parse_api_error(exc)
    assert "rate limit" in reason.lower() or "429" in reason
    assert "429" in detail