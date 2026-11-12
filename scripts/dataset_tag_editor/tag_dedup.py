"""Smart tag deduplication.

Removes generic tags from a caption when a more specific tag of the same
kind is already present, e.g.:

    "white thighhighs" -> removes "thighhighs"
    "white panties"    -> removes "panties" and "underwear"
    "rose"             -> removes "flowers" / "flower"

Two engines are provided:

* ``rules``  -- fully offline. A built-in implication table (booru-style
  specific -> generic) plus a "<color> <noun>" prefix heuristic. The table
  can be extended or overridden with a JSON file::

      {
        "implications": {
          "white thighhighs": ["thighhighs"],
          "rose": ["flowers", "flower"]
        },
        "colors": ["white", "black", "..."]   // optional, replaces defaults
      }

* ``llm`` -- asks an OpenAI-compatible or Anthropic-compatible chat API to
  decide which tags are subsumed. Works with local servers (llama.cpp,
  Ollama, vLLM, ...) as well as hosted APIs. Only ``requests`` is needed.

Both engines return the *original* tag strings that should be removed and
never remove every tag of a caption (a caption must keep at least one tag).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

# --------------------------------------------------------------------------
# built-in rules
# --------------------------------------------------------------------------

# specific tag -> generic tags that become redundant when it is present.
# Keys and values are normalized (lowercase, underscores -> spaces).
BUILTIN_IMPLICATIONS: dict[str, list[str]] = {
    # --- underwear / legwear ---
    "panties": ["underwear"],
    "bra": ["underwear"],
    "lingerie": ["underwear"],
    "thighhighs": ["legwear"],
    "pantyhose": ["legwear"],
    "stockings": ["legwear"],
    "knee highs": ["legwear"],
    # --- footwear ---
    "sneakers": ["shoes"],
    "high heels": ["shoes"],
    "boots": ["footwear"],
    "sandals": ["footwear"],
    "loafers": ["shoes"],
    # --- flowers / plants ---
    "rose": ["flower", "flowers"],
    "tulip": ["flower", "flowers"],
    "lily": ["flower", "flowers"],
    "sunflower": ["flower", "flowers"],
    "daisy": ["flower", "flowers"],
    "orchid": ["flower", "flowers"],
    "cherry blossoms": ["flower", "flowers"],
    "lotus": ["flower", "flowers"],
    "dandelion": ["flower", "flowers"],
    "hydrangea": ["flower", "flowers"],
    "bouquet": ["flower", "flowers"],
    # --- animals ---
    "dog": ["animal"],
    "cat": ["animal"],
    "bird": ["animal"],
    "horse": ["animal"],
    "rabbit": ["animal"],
    "fox": ["animal"],
    "wolf": ["animal"],
    "bear": ["animal"],
    "lion": ["animal"],
    "tiger": ["animal"],
    "dragon": ["creature"],
    # --- weapons ---
    "katana": ["sword", "weapon"],
    "sword": ["weapon"],
    "rifle": ["gun", "weapon"],
    "pistol": ["gun", "weapon"],
    "gun": ["weapon"],
    "knife": ["weapon"],
    "dagger": ["knife", "weapon"],
    # --- food / drink ---
    "apple": ["fruit"],
    "banana": ["fruit"],
    "orange": ["fruit"],
    "strawberry": ["fruit"],
    "grape": ["fruit"],
    "cake": ["food"],
    "bread": ["food"],
    "rice": ["food"],
    "tea": ["drink"],
    "coffee": ["drink"],
    "juice": ["drink"],
    # --- vehicles ---
    "car": ["vehicle"],
    "truck": ["vehicle"],
    "bus": ["vehicle"],
    "motorcycle": ["vehicle"],
    "bicycle": ["vehicle"],
    "airplane": ["vehicle"],
    "train": ["vehicle"],
    "ship": ["vehicle"],
    # --- instruments ---
    "guitar": ["instrument"],
    "piano": ["instrument"],
    "violin": ["instrument"],
    "drum": ["instrument"],
    # --- weather / sky ---
    "rain": ["weather"],
    "snow": ["weather"],
    "cloud": ["sky"],
    "sunset": ["sky"],
    # --- misc ---
    "smile": ["expression"],
    "smartphone": ["phone"],
    "laptop": ["computer"],
}

DEFAULT_COLORS = [
    "white", "black", "red", "blue", "green", "yellow", "purple", "pink",
    "orange", "brown", "grey", "gray", "silver", "gold", "golden",
    "beige", "cyan", "magenta", "lavender", "crimson", "scarlet", "navy",
    "teal", "turquoise", "violet", "maroon", "olive", "aqua", "blonde",
]

# multi-word color prefixes handled by the built-in table above; the
# heuristic itself only fires on "<color> <single word>" to avoid breaking
# proper nouns such as "black rock shooter".


def normalize(tag: str) -> str:
    return tag.strip().lower().replace("_", " ")


def _variants(word: str) -> set[str]:
    """Cheap singular/plural variants so 'flower' also matches 'flowers'."""
    out = {word}
    if word.endswith("s"):
        out.add(word[:-1])
    else:
        out.add(word + "s")
    return out


def load_rules(rules_path: str | Path | None = None) -> dict:
    """Merge built-in implications with an optional user JSON file."""
    implications = {k: set(v) for k, v in BUILTIN_IMPLICATIONS.items()}
    colors = set(DEFAULT_COLORS)
    if rules_path:
        p = Path(rules_path)
        if p.is_file():
            data = json.loads(p.read_text("utf8"))
            for specific, generics in data.get("implications", {}).items():
                if isinstance(generics, str):
                    generics = [generics]
                implications.setdefault(normalize(specific), set()).update(
                    normalize(g) for g in generics
                )
            if "colors" in data:
                colors = {normalize(c) for c in data["colors"]}
    return {"implications": implications, "colors": colors}


def compute_removals_rules(tags: list[str], rules: dict | None = None) -> list[str]:
    """Return the original tag strings that are redundant under the rules."""
    if rules is None:
        rules = load_rules()
    implications = rules["implications"]
    colors = rules["colors"]

    norm = {t: normalize(t) for t in tags}
    present = set(norm.values())
    remove: set[str] = set()

    for original, n in norm.items():
        generics: set[str] = set(implications.get(n, ()))
        parts = n.split()
        if len(parts) == 2 and parts[0] in colors:
            generics.add(parts[1])
        for generic in generics:
            for variant in _variants(generic):
                if variant in present and variant != n:
                    for orig2, n2 in norm.items():
                        if n2 == variant:
                            remove.add(orig2)

    remove.discard("")
    if len(remove) >= len(set(norm.values())):
        # never strip a caption down to nothing
        return []
    return sorted(remove)


# --------------------------------------------------------------------------
# LLM engine
# --------------------------------------------------------------------------

SYSTEM_PROMPT = (
    "You deduplicate booru-style image caption tags. Given a list of tags "
    "describing ONE image, find generic tags that are fully implied by a "
    "more specific tag in the SAME list (e.g. 'thighhighs' is implied by "
    "'white thighhighs'; 'underwear' and 'panties' are implied by "
    "'white panties'; 'flowers' is implied by 'rose'). "
    "Reply with ONLY a JSON object: {\"remove\": [\"tag\", ...]}. "
    "Rules: only list tags that appear verbatim in the input list; "
    "never remove the more specific tag; never remove tags that are merely "
    "related but not implied (e.g. keep 'blue eyes' when 'blue hair' is "
    "present, keep '1girl' when 'solo' is present); "
    "when unsure, keep the tag; keep at least one tag; no explanations."
)


def _chat_openai(base_url: str, model: str, api_key: str, user_prompt: str,
                 timeout: float) -> str:
    import requests

    base = base_url.rstrip("/")
    if not base.endswith("/v1"):
        base += "/v1"
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    resp = requests.post(
        base + "/chat/completions",
        headers=headers,
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
            "max_tokens": 1024,
            # Dedup only needs a short JSON answer, not chain-of-thought.
            # Hybrid reasoning models (Qwen3 etc.) otherwise burn ~98% of the
            # tokens and tens of seconds per caption "thinking", which makes a
            # whole-dataset dedup look frozen. Servers/models without a
            # thinking toggle simply ignore this kwarg.
            "chat_template_kwargs": {"enable_thinking": False},
        },
        timeout=timeout,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"] or ""


def _chat_anthropic(base_url: str, model: str, api_key: str, user_prompt: str,
                    timeout: float) -> str:
    import requests

    base = base_url.rstrip("/")
    if not base.endswith("/v1"):
        base += "/v1"
    resp = requests.post(
        base + "/messages",
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
        json={
            "model": model,
            "max_tokens": 1024,
            "system": SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": user_prompt}],
        },
        timeout=timeout,
    )
    resp.raise_for_status()
    data = resp.json()
    return "".join(
        block.get("text", "") for block in data.get("content", [])
        if block.get("type") == "text"
    )


def _parse_removals(text: str) -> list[str]:
    """Extract {"remove": [...]} from a model reply, tolerating fences/prose."""
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    if fence:
        text = fence.group(1).strip()
    try:
        obj = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.S)
        if not match:
            return []
        try:
            obj = json.loads(match.group(0))
        except json.JSONDecodeError:
            return []
    if isinstance(obj, dict):
        removals = obj.get("remove", [])
    elif isinstance(obj, list):
        removals = obj
    else:
        return []
    return [str(t) for t in removals if isinstance(t, (str, int, float))]


def compute_removals_llm(tags: list[str], *, api_type: str, base_url: str,
                         model: str, api_key: str = "",
                         timeout: float = 60.0) -> list[str]:
    """Ask an LLM which tags are redundant. Returns original tag strings."""
    if not base_url or not model:
        raise ValueError("LLM dedup requires base URL and model (see Settings)")
    user_prompt = "Tags:\n" + json.dumps(tags, ensure_ascii=False)
    api_type = (api_type or "openai").strip().lower()
    if api_type == "anthropic":
        reply = _chat_anthropic(base_url, model, api_key, user_prompt, timeout)
    else:
        reply = _chat_openai(base_url, model, api_key, user_prompt, timeout)

    proposed = _parse_removals(reply)
    by_norm: dict[str, list[str]] = {}
    for t in tags:
        by_norm.setdefault(normalize(t), []).append(t)

    remove: set[str] = set()
    for p in proposed:
        for orig in by_norm.get(normalize(str(p)), ()):
            remove.add(orig)
    if len(remove) >= len(set(normalize(t) for t in tags)):
        return []  # model tried to wipe the caption; ignore
    return sorted(remove)


def compute_removals(tags: list[str], mode: str = "rules",
                     rules: dict | None = None,
                     llm_options: dict | None = None) -> list[str]:
    if not tags:
        return []
    if mode == "llm":
        return compute_removals_llm(tags, **(llm_options or {}))
    return compute_removals_rules(tags, rules)
