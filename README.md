# clepsy

A thin client SDK for the **Dynamic Auth Framework (DAF)** — time-based dynamic
password authentication where stolen credentials expire every 60 seconds by design.

Named after the *clepsydra*, the ancient water clock: a fitting root for a protocol
where your password quite literally tells time.

clepsy does **not** run any authentication logic locally. It's a thin wrapper over
your deployed DAF service's HTTP API, so identity stays centralized in one place —
this is what makes login shared across every project using clepsy.

[![PyPI](https://img.shields.io/pypi/v/clepsy)](https://pypi.org/project/clepsy/)

## Install

```bash
pip install clepsy
```

## Quickstart

```python
from clepsy import ClepsyClient

client = ClepsyClient(base_url="https://your-daf-api.com", api_key="daf_c_xxxxx")

# Register: static part "Botnet", placeholder "x" marks where the dynamic
# time value goes at login.
client.register("Botnet", "Botxxnetxx", placeholder="x")

# At login time, fill the placeholder positions with the current UTC HHMM.
dynamic = client.current_dynamic_value()          # e.g. "2130"
login_password = f"Bot{dynamic}net{dynamic[2:]}"  # depends on your pattern

result = client.authenticate("Botnet", login_password)
if result.success:
    print(f"Welcome, {result.username}")
```

## Error handling

```python
from clepsy import AuthenticationFailedError, ClepsyConnectionError, ClepsyError

try:
    result = client.authenticate(username, password)
except AuthenticationFailedError:
    show("wrong username or password")
except ClepsyConnectionError:
    show("auth service unavailable, try again")
except ClepsyError:
    show("something went wrong")
```

## Why a thin client, not a local library?

An earlier design considered shipping the full DPP engine (`dpp_core.py`) as an
importable library. That would mean every consuming project runs its own local
auth logic and its own user table — which breaks single sign-on across projects.
clepsy instead calls one centrally deployed DAF instance, so "register on Project A,
log in on Project B" works by construction.

## Status

v0.1.0 — early, built against DAF Phase 1. API surface may still change before 1.0.

## License

MIT
