"""Minimal TypeSafe Jev client (direct API), verified 2026-09-22.

Endpoint facts confirmed by live calls on 2026-09-22 (see refine-logs/EXPERIMENT_TRACKER.md):
  - POST https://api.typesafe.ai/v1/systemone, Bearer $TYPESAFE_API_KEY
  - body must carry "model": "jev-latest"  (missing -> 422); served model was jev-1.13.0
  - question types: "noul" (boolean; criteria must be {"true":..., "false":...} or omitted),
    "choice" (criteria = {option: description}), "score" (criteria = ordered list)
  - ~0.25 s per call, ~310 input tokens for a short item -> ~$1.3e-5 per call at $0.042/M input tokens
"""
import json
import os
import time
import urllib.error
import urllib.request

URL = "https://api.typesafe.ai/v1/systemone"

# 2026-09-22: mid-run, the endpoint began returning HTTP 403 "error code: 1010"
# to this client. 1010 is Cloudflare's "banned based on browser signature", and
# urllib's default User-Agent is `Python-urllib/x.y`. Chrome on the same machine
# and IP reached the same endpoint normally, the API key stayed Active and usage
# showed no limit, so the block was on the client signature, not on us.
# Identifying the client honestly clears it. This is not a browser impersonation:
# it says what the client is, who runs it and how to reach them, which is what an
# API client should send anyway. See prereg/DEVIATIONS_B1.md DEV-2.
USER_AGENT = "open-jev-eval/1.0 (independent research; ickma2311@gmail.com)"


def ask(state, questions, model="jev-latest", timeout=60, retries=3):
    """Send one Jev request. Returns (response_dict, elapsed_seconds)."""
    key = os.environ.get("TYPESAFE_API_KEY")
    if not key:
        raise RuntimeError("TYPESAFE_API_KEY not set (source ~/.zshrc)")
    body = json.dumps({"model": model, "state": state, "questions": questions}).encode()
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "User-Agent": USER_AGENT,
    }
    for attempt in range(retries):
        start = time.time()
        try:
            with urllib.request.urlopen(urllib.request.Request(URL, data=body, headers=headers), timeout=timeout) as fh:
                return json.load(fh), time.time() - start
        except urllib.error.HTTPError as exc:
            detail = exc.read()[:400].decode("utf-8", "replace")
            if exc.code in (429, 500, 502, 503) and attempt < retries - 1:
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(f"Jev HTTP {exc.code}: {detail}") from exc
        except urllib.error.URLError:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
                continue
            raise


def choice(state, instructions, options, name="q"):
    """One multiple-choice question. `options` maps option key -> description."""
    resp, secs = ask(state, {name: {"type": "choice", "instructions": instructions, "criteria": options}})
    return resp["answers"][name], secs


def noul(state, instructions, criteria=None, name="q"):
    """One boolean question; returns p(true) in [0, 1]."""
    q = {"type": "noul", "instructions": instructions}
    if criteria:
        q["criteria"] = criteria
    resp, secs = ask(state, {name: q})
    return resp["answers"][name]["noul"], secs


if __name__ == "__main__":
    p, secs = noul("A user writes: 'my card was charged twice for one order'.", "Is this a billing issue?")
    print(f"p(billing)={p} in {secs:.2f}s")
