# clepsy

A thin client SDK for the **Dynamic Auth Framework (DAF)** — time-based dynamic
password authentication where stolen credentials expire every 60 seconds by design.

Named after the *clepsydra*, the ancient water clock: a fitting root for a protocol
where your password quite literally tells time.

[![PyPI](https://img.shields.io/pypi/v/clepsy)](https://pypi.org/project/clepsy/)

## Install

```bash
pip install clepsy
```

## How Dynamic Password Protocol (DPP) works

A DPP password has two parts, chosen entirely by the end user at registration:

- **Static part** — characters the user remembers, like a normal password
- **Dynamic part** — one or more placeholder characters (default `x`) marking
  positions that get filled with the current UTC time (`HHMM`) at login

The user decides both *what* the static characters are and *where* the
placeholder characters go — anywhere in the string, in any grouping. All of
these are valid registration patterns for the same static part (`Botnet`):

| Pattern | Static part | Placeholder positions |
|---|---|---|
| `Botxxnetxx` | `Botnet` | two 2-char runs, interspersed |
| `Botnetxxxx` | `Botnet` | one 4-char run, suffix |
| `xxBotnetxx` | `Botnet` | split across prefix and suffix |

A stolen password is only valid for the current minute — by the next minute,
the dynamic part has changed and the old password is rejected.

**Important: your application never constructs the login password.** The end
user does, in their head, the same way they'd recall any password — they
remember their static characters and where to slot in the current time. Your
code only ever receives and forwards whatever string the user typed into the
password field. There's no parsing or reconstruction logic to write.

## Building a login page with clepsy

### 1. Registration

Your registration form collects a username and a full pattern (static +
placeholder characters, in whatever arrangement the user wants):

```python
from clepsy import ClepsyClient

client = ClepsyClient(base_url="https://your-daf-api.com", api_key="daf_c_xxxxx")

result = client.register("Botnet", "Botxxnetxx", placeholder="x")
print(result.parameter_map)   # "0001100011" -- stored server-side, not needed by your app
```

Tell the user their pattern was accepted, and remind them: *"remember your
password exactly as you typed it -- you'll fill the same positions with the
current time each time you log in."*

### 2. Login page UI

Two things are genuinely useful to show the user at login time:

- The password field itself (masked, like any password field)
- A live hint for the current dynamic value, since DPP asks the user to do a
  small mental substitution each time:

```python
current_hint = client.current_dynamic_value()   # e.g. "2130"
print(f"Current time value: {current_hint}")     # or render it however your UI framework expects
```

This isn't required -- a confident user doesn't need it -- but it removes any
guesswork about what "the current time" means in HHMM format.

### 3. Authenticate

The user types their full password (static + today's time, wherever their
pattern puts it). Whatever collects that input in your app — a web form, a
CLI prompt, anything — just pass the raw string straight through, untouched:

```python
username = input("Username: ")
password = input("Password: ")

# `client` here is the same ClepsyClient created once in Section 1 --
# create it a single time per app (e.g. at startup), not per request.
result = client.authenticate(username, password)
if result.success:
    print(f"Welcome, {result.username}")
```

If you're building a web app instead of a CLI, the only thing that changes is
*where* `username`/`password` come from (Flask's `request.form`, FastAPI's
request model, etc.) — the `client.authenticate(...)` call itself is identical.

No slicing, no splitting, no knowledge of *where* the placeholders are in this
particular user's pattern -- that's entirely between DAF's server-side
`parameter_map` and the user's own memory. Your app is just a relay.

## Error handling

Wrapping the same `client.authenticate(username, password)` call from above:

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

v0.1.2 — early, built against DAF Phase 1. API surface may still change before 1.0.

## License

MIT
