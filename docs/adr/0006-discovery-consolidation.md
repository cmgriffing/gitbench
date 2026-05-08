# Benchmark discovery consolidated — no more explicit imports in `__init__.py`

The benchmarks `__init__.py` hardcoded explicit imports of 10 out of 17 benchmark classes, creating a second discovery mechanism that was already stale. We removed all explicit subclass imports; `__init__.py` now only re-exports `Benchmark` from the harness. Auto-discovery via `discover_benchmarks()` (which scans every `.py` file in the package) is the single source of truth. Adding a benchmark requires only creating the file — no import or `__all__` registration.
