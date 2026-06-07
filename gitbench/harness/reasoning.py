"""Model-name parsing for GitBench reasoning levels.

Provides the canonical VALID_REASONING_LEVELS constant and utility functions
for parsing model names that may include effort-level suffixes.
"""

VALID_REASONING_LEVELS = ["none", "minimal", "low", "medium", "high", "xhigh", "max"]


def parse_model_reasoning(model_name: str) -> tuple[str, str | None]:
    """Split a model name into base name and optional reasoning level.

    Syntax: ``base_model``, ``base_model#level``, or ``base_model:level``.
    A final colon segment is only treated as effort when it exactly matches a
    valid GitBench effort value. If multiple ``#`` are present, only the last
    one delimits the level.

    Args:
        model_name: Full model name, optionally with ``#level`` suffix.

    Returns:
        A tuple of ``(base_model, reasoning_level)`` where
        ``reasoning_level`` is ``None`` when no ``#`` is present.
    """
    hash_idx = model_name.rfind("#")
    colon_idx = model_name.rfind(":")

    if hash_idx > colon_idx:
        return model_name[:hash_idx], model_name[hash_idx + 1:]

    if colon_idx != -1:
        suffix = model_name[colon_idx + 1:]
        if suffix in VALID_REASONING_LEVELS:
            return model_name[:colon_idx], suffix

    return model_name, None
