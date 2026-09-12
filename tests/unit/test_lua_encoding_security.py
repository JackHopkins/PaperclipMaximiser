"""Regression tests for ``Controller``'s Lua string encoding.

``slpp.encode`` (the encoder every RCON tool call goes through) escapes
double quotes but not backslashes or newlines. Any string argument
containing ``\\``, ``\n`` or ``\r`` therefore produces invalid Lua
(``C:\\path`` -> "invalid escape sequence", multi-line text -> "unfinished
string") and the tool call fails; a string ending in an odd number of
backslashes before a quote closes its literal early, so the remainder of
the argument is parsed as Lua rather than as string content.

The fix (``fle.env.tools.controller._lua_encode_safe`` /
``_lua_escape_string``) pre-escapes backslashes and raw newline/carriage
-return bytes before handing the value to ``lua.encode``, recursing into
dict/list/tuple structures because slpp reuses the same string branch for
every nested leaf.

Scope: this is a correctness fix plus defense in depth, not a privilege
boundary. FLE executes agent programs in-process with the
``FactorioInstance`` in scope, so an agent can already reach
``instance.rcon_client`` directly; the tests below check that the emitted
Lua is always well-formed and that string content can never escape its
literal, for any future frontend that passes tool arguments without
exposing Python.

These tests use a real Lua interpreter (``lupa``, an existing project
dependency -- see fle/env/lua_manager.py) to parse the encoded output,
rather than relying on hand-traced escaping reasoning.
"""

import warnings

import pytest

warnings.filterwarnings("ignore", category=SyntaxWarning, module="slpp")

from slpp import slpp as lua  # noqa: E402

from fle.env.tools.controller import (  # noqa: E402
    _lua_encode_safe,
    _lua_escape_string,
)

lupa = pytest.importorskip("lupa")


@pytest.fixture()
def lua_runtime():
    return lupa.LuaRuntime()


def _run_as_call_argument(rt, encoded_lua_text, injected_flag):
    """Mirror the real invocation shape built by Controller._execute_once:

        pcall(storage.actions.<name>(<encoded args>))

    with a stand-in ``actions_x`` and an ``INJECTED`` marker function that
    a successful escape would be able to call. Returns (ok, value) from
    the pcall, or raises if the generated text is not even valid Lua
    (which is also a safe outcome: a syntax error can't execute anything).
    """
    injected_flag["called"] = False
    rt.globals()["INJECTED"] = lambda: injected_flag.__setitem__("called", True)
    code = (
        "local function actions_x(v) return v end "
        f"local ok, res = pcall(function() return actions_x({encoded_lua_text}) end) "
        "return ok, res"
    )
    return rt.execute(code)


# ---------------------------------------------------------------------------
# Injection PoCs: must never let injected Lua execute, regardless of whether
# the malformed OLD encoding happened to raise a parse error or not.
# ---------------------------------------------------------------------------

INJECTION_POCS = [
    pytest.param('a\\" -- INJECTED() --', id="trailing-backslash-quote-comment"),
    pytest.param("ends with a lone backslash \\", id="string-ends-in-backslash"),
    pytest.param(
        'multi \\" quote\\" combo \\\\ end', id="multiple-quote-backslash-sequences"
    ),
    pytest.param(
        'break\\"); INJECTED(); local x=("',
        id="full-breakout-inject-statement-pattern",
    ),
    pytest.param('"); INJECTED(); --', id="quote-only-no-backslash-trick"),
]


@pytest.mark.parametrize("payload", INJECTION_POCS)
def test_injection_pocs_cannot_execute_injected_lua(lua_runtime, payload):
    injected_flag = {"called": False}
    safe_encoded = lua.encode(_lua_encode_safe(payload))

    try:
        ok, value = _run_as_call_argument(lua_runtime, safe_encoded, injected_flag)
    except lupa.LuaError:
        # A syntax error is also an acceptable, safe outcome (nothing
        # executes), but the whole point of the fix is that this should
        # no longer happen for well-formed input -- assert it parses.
        pytest.fail(f"safely-encoded payload failed to parse as Lua: {payload!r}")

    assert not injected_flag["called"], (
        f"INJECTED() was called -- injection succeeded for payload {payload!r} "
        f"(encoded: {safe_encoded!r})"
    )
    assert ok is True
    assert value == payload, "payload must round-trip unchanged as inert string data"


# The "quote-only" PoC contains no backslash, so slpp's pre-existing
# quote-escaping already handles it correctly even without our fix -- it's
# kept in INJECTION_POCS as a safety-net regression check (must keep
# working), but it doesn't demonstrate the backslash bug, so it's excluded
# from the "raw slpp is broken" sanity check below.
BACKSLASH_TRICK_POCS = [
    p for p in INJECTION_POCS if p.id != "quote-only-no-backslash-trick"
]


@pytest.mark.parametrize("payload", BACKSLASH_TRICK_POCS)
def test_unsafe_slpp_encode_is_demonstrably_broken(lua_runtime, payload):
    """Sanity check that these PoCs actually exercise the bug in raw slpp
    (either by corrupting the parsed value or raising a parse error) --
    otherwise the "fix" above wouldn't be proving anything.
    """
    injected_flag = {"called": False}
    unsafe_encoded = lua.encode(payload)

    try:
        ok, value = _run_as_call_argument(lua_runtime, unsafe_encoded, injected_flag)
    except lupa.LuaError:
        return  # broken: raw slpp output isn't even valid Lua for this payload

    # If it happens to parse, it must not have round-tripped correctly
    # (i.e. the string was corrupted/truncated by the early close), since
    # that's what "the string literal closed early" means in practice.
    assert value != payload or injected_flag["called"], (
        f"expected raw slpp.encode to mishandle {payload!r}, but it round-tripped "
        "correctly -- this PoC no longer demonstrates the bug"
    )


# ---------------------------------------------------------------------------
# Legitimate strings must still round-trip exactly (no functional regression).
# ---------------------------------------------------------------------------

LEGIT_STRINGS = [
    pytest.param("hello world", id="plain"),
    pytest.param("it's a test", id="single-quote"),
    pytest.param("back\\slash", id="single-backslash"),
    pytest.param("line1\nline2", id="newline"),
    pytest.param("carriage\rreturn", id="carriage-return"),
    pytest.param("unicode: héllo wörld 日本語 \U0001f680", id="unicode"),
    pytest.param("", id="empty-string"),
    pytest.param('quote " inside', id="double-quote"),
    pytest.param("furnace destroyed", id="report-fault-style-cause"),
]


@pytest.mark.parametrize("value", LEGIT_STRINGS)
def test_legitimate_strings_round_trip_exactly(lua_runtime, value):
    encoded = lua.encode(_lua_encode_safe(value))
    decoded = lua_runtime.execute(f"return {encoded}")
    assert decoded == value


def test_legitimate_strings_round_trip_via_slpp_decode():
    """Also confirm slpp's own decoder (used for real RCON responses) agrees,
    not just the Lua interpreter, for the strings it decodes correctly.

    Note: literal backslashes and newlines are deliberately excluded here.
    Making encode() correctly escape backslashes/newlines (this fix) means
    encode() can now legitimately emit `\\\\` and `\\n` escape sequences --
    and slpp's *own* decoder (independent of this fix, which only touches
    encode()) has pre-existing bugs where it (a) fails to collapse `\\\\`
    back into a single backslash, doubling it instead, and (b) doesn't
    recognize `\\n`/`\\r` as escapes at all (it only special-cases
    un-escaping the string's own terminator character). That decoder is
    only ever used on Lua text produced by the game's own `dump()` Lua
    function (see fle/env/utils/rcon.py), not on text produced by our
    encode() path, so it's out of scope for this fix -- flagged here rather
    than silently ignored. The real Lua interpreter (see
    test_legitimate_strings_round_trip_exactly above) parses all of these
    correctly, which is what the actual game engine does.
    """
    for value in (
        "hello world",
        "it's a test",
        'quote " inside',
        "",
    ):
        encoded = lua.encode(_lua_encode_safe(value))
        assert lua.decode(encoded) == value


# ---------------------------------------------------------------------------
# Nested structures: slpp recurses into dict/list/tuple values and reuses the
# same string-encoding branch for every leaf, so a malicious string nested
# inside a dict/list argument (e.g. a tool that passes a dict payload) must be
# neutralized too, not just top-level scalar args.
# ---------------------------------------------------------------------------


def test_nested_dict_string_leaves_are_escaped(lua_runtime):
    injected_flag = {"called": False}
    lua_runtime.globals()["INJECTED"] = lambda: injected_flag.__setitem__(
        "called", True
    )
    payload = {
        "kind": 'evil" -- INJECTED() --',
        "items": ['a\\"b', "normal", 3, True, None],
        "nested": {"x": 'y\\" -- inner injection --'},
    }
    encoded = lua.encode(_lua_encode_safe(payload))

    code = f"local ok, res = pcall(function() return {encoded} end) return ok, res"
    ok, res = lua_runtime.execute(code)

    assert ok is True
    assert not injected_flag["called"]
    assert res["kind"] == payload["kind"]
    assert res["nested"]["x"] == payload["nested"]["x"]
    assert res["items"][1] == payload["items"][0]  # Lua tables are 1-indexed


# ---------------------------------------------------------------------------
# Exact-shape reproduction: Controller._execute_once/execute2 don't actually
# build `pcall(f(args))` (nested call) -- they build the idiomatic Lua
# `pcall(f, args...)` (function passed as pcall's first argument, real args
# as pcall's remaining arguments; see controller.py's `invocation =
# f"pcall(storage.actions.{{self.name}}{{...}})"` producing e.g.
# `pcall(storage.actions.echo_cause, 1, 6, 6, "cause")`). That shape only
# needs ONE closing paren to close `pcall(...)` itself, not two -- a payload
# balanced for a nested-call shape (like the generic PoCs above) actually
# produces a Lua syntax error against the *real* shape rather than a clean
# injection, which under-proves the fix. This test uses the exact real
# shape and confirms live-equivalent behavior: a properly single-paren
# -balanced payload achieves genuine statement injection (sets a canary) pre
# -fix, and is fully neutralized post-fix. (Cross-checked live against a
# real Factorio 2.0.73 headless server.)
# ---------------------------------------------------------------------------


def _real_shape_command(encoded_cause):
    """Reproduce controller.py's actual invocation string builder for
    echo_cause(player_index=1, x=6, y=6, cause)."""
    return f"pcall(storage.actions.echo_cause, 1, 6, 6, {encoded_cause})"


def test_real_invocation_shape_injection_is_neutralized(lua_runtime):
    lua_runtime.execute(
        "storage = { probe = {} } "
        "storage.actions = {} "
        "storage.actions.echo_cause = function(player, x, y, cause) "
        "  table.insert(storage.probe, cause) return true end"
    )
    payload = 'legit-looking-cause\\" ) storage.probe.INJECTED_PWNED = true --'
    safe_encoded = lua.encode(_lua_encode_safe(payload))
    code = f"local a, b = {_real_shape_command(safe_encoded)}"
    lua_runtime.execute(code)
    canary = lua_runtime.eval("storage.probe.INJECTED_PWNED")
    assert canary is None, (
        f"real-shape injection succeeded even with the fix applied -- canary={canary!r}"
    )


def test_real_invocation_shape_injection_succeeds_without_fix(lua_runtime):
    """Sanity check / documentation: proves the exact real invocation shape
    is genuinely exploitable pre-fix (not just theoretically), matching what
    was independently confirmed live against a real Factorio server."""
    lua_runtime.execute(
        "storage = { probe = {} } "
        "storage.actions = {} "
        "storage.actions.echo_cause = function(player, x, y, cause) "
        "  table.insert(storage.probe, cause) return true end"
    )
    payload = 'legit-looking-cause\\" ) storage.probe.INJECTED_PWNED = true --'
    unsafe_encoded = lua.encode(payload)  # raw slpp.encode, no pre-escaping
    code = f"local a, b = {_real_shape_command(unsafe_encoded)}"
    lua_runtime.execute(code)
    canary = lua_runtime.eval("storage.probe.INJECTED_PWNED")
    assert canary is True, (
        "expected the unfixed encoder to be exploitable via the real "
        f"invocation shape, but canary={canary!r}"
    )


def test_nested_list_string_leaves_are_escaped(lua_runtime):
    injected_flag = {"called": False}
    lua_runtime.globals()["INJECTED"] = lambda: injected_flag.__setitem__(
        "called", True
    )
    payload = ['a\\" -- INJECTED() --', "plain", {"x": 'y\\" -- INJECTED() --'}]
    encoded = lua.encode(_lua_encode_safe(payload))

    code = f"local ok, res = pcall(function() return {encoded} end) return ok, res"
    ok, res = lua_runtime.execute(code)

    assert ok is True
    assert not injected_flag["called"]


# ---------------------------------------------------------------------------
# Unit-level checks on the helper functions themselves.
# ---------------------------------------------------------------------------


def test_lua_escape_string_order_is_backslash_before_quote_composition():
    # slpp.encode still does the quote-escaping; our helper must only add
    # backslash/newline escaping ahead of it, not duplicate quote handling.
    assert _lua_escape_string('a\\"b') == 'a\\\\"b'
    assert _lua_escape_string("a\nb") == "a\\nb"
    assert _lua_escape_string("a\rb") == "a\\rb"
    assert _lua_escape_string("no-escapes-needed") == "no-escapes-needed"


def test_lua_encode_safe_preserves_non_string_types():
    assert _lua_encode_safe(42) == 42
    assert _lua_encode_safe(3.14) == 3.14
    assert _lua_encode_safe(True) is True
    assert _lua_encode_safe(None) is None


def test_lua_encode_safe_recurses_dict_and_list():
    out = _lua_encode_safe({"a": ["x\\y", {"b": "p\\q"}]})
    assert out == {"a": ["x\\\\y", {"b": "p\\\\q"}]}
