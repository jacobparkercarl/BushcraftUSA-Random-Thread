"""
Random-thread redirector for bushcraftusa.com (XenForo forum).
Deploy as a Lambda with a public Function URL (Auth type: NONE).
Bookmark the Function URL for a one-click random-thread button.
Jacob.Parker.Carl
9.2.26
"""
import logging
import random
import urllib.error
import urllib.request

logger = logging.getLogger()
logger.setLevel(logging.INFO)

THREAD_URL = "https://bushcraftusa.com/threads/{}"
# Default urllib User-Agent gets 403'd by a lot of forum bot protection,
# and some stacks don't handle HEAD cleanly -- plain GET with a normal
# User-Agent avoids both.
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}

# Bump MAX_ID every few months -- thread count grows by roughly 35 a day from what I can see.
# Verified against real threads: #399454 dated Jan 21 2026 and
# #405354 dated Jul 10 2026. This ceiling has a few weeks of
# headroom built in as of Sep 2026.
MIN_ID = 1
MAX_ID = 407500
FALLBACK_ID = 66596  # "The American Chestnut" -- known-good
MAX_ATTEMPTS = 5


def _resolves(thread_id: int) -> bool:
    req = urllib.request.Request(THREAD_URL.format(thread_id), headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=3) as resp:
            logger.info("id=%s status=%s", thread_id, resp.status)
            return resp.status < 400
    except urllib.error.HTTPError as e:
        logger.info("id=%s http_error=%s", thread_id, e.code)
        return False
    except Exception as e:
        logger.info("id=%s network_error=%r", thread_id, e)
        # Network hiccup on our end -- don't sink the redirect over it.
        return True


def handler(event, context):
    thread_id = FALLBACK_ID
    for _ in range(MAX_ATTEMPTS):
        candidate = random.randint(MIN_ID, MAX_ID)
        if _resolves(candidate):
            thread_id = candidate
            break

    return {
        "statusCode": 302,
        "headers": {
            "Location": THREAD_URL.format(thread_id),
            "Cache-Control": "no-store",
        },
    }
