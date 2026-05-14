"""Human-readable formatting utilities for numbers, costs, and durations."""


def human_readable(n: int, unit: str = "") -> str:
    """Format an integer with K/M/B suffixes.

    Args:
        n: The number to format.
        unit: Optional unit string appended after a space (e.g. ``"tok"``).

    Returns:
        Formatted string like ``"1.2K"``, ``"3.5M"``, or ``"1.2K tok"``.
    """
    if n < 1000:
        result = str(n)
    elif n < 1_000_000:
        result = f"{n / 1000:.1f}K"
    elif n < 1_000_000_000:
        result = f"{n / 1_000_000:.1f}M"
    else:
        result = f"{n / 1_000_000_000:.1f}B"

    if unit:
        return f"{result} {unit}"
    return result


def human_readable_cost(n: float) -> str:
    """Format a float as a USD cost string.

    Args:
        n: Cost in USD.

    Returns:
        String like ``"$0.04"``, ``"$1.23"``, or ``"$123.45"``.
    """
    if n < 1:
        return f"${n:.2f}"
    elif n < 100:
        return f"${n:.2f}"
    else:
        return f"${n:.2f}"


def format_duration(seconds: float) -> str:
    """Format a duration in seconds as a human-readable string.

    Args:
        seconds: Duration in seconds.

    Returns:
        String like ``"45s"`` or ``"2m14s"``.
    """
    seconds_int = int(seconds)
    minutes, secs = divmod(seconds_int, 60)
    if minutes:
        return f"{minutes}m{secs:02d}s"
    return f"{secs}s"
