from datetime import timedelta

def ist_now():
    """Return current IST timestamp in ISO format."""
    IST = timezone(timedelta(hours=5, minutes=30))
    return datetime.now(IST).isoformat()
