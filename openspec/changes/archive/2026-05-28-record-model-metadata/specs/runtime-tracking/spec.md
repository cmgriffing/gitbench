## ADDED Requirements

### Requirement: Score supports optional api_duration_ms field alongside duration_ms

The `Score` dataclass SHALL have an optional `api_duration_ms: float | None` field with a default of `None`, representing the API call latency in milliseconds. This SHALL be measured separately from `duration_ms` (wall-clock time) and stored on the same `Score` object. The `to_dict()` method SHALL omit the field when it is `None`. The `from_dict()` method SHALL accept `api_duration_ms` when present and default to `None` when absent.

#### Scenario: api_duration_ms and duration_ms coexist on Score
- **WHEN** a fixture run takes 2000ms wall-clock and the API call takes 350ms
- **THEN** `score.duration_ms` is 2000.0 and `score.api_duration_ms` is 350.0

#### Scenario: api_duration_ms defaults to None
- **WHEN** a `Score` is created without specifying `api_duration_ms`
- **THEN** `score.api_duration_ms` is `None`

#### Scenario: to_dict omits None api_duration_ms
- **WHEN** `score.to_dict()` is called on a `Score` with `api_duration_ms=None`
- **THEN** the resulting dict does NOT contain an `api_duration_ms` key

#### Scenario: to_dict includes non-None api_duration_ms
- **WHEN** `score.to_dict()` is called on a `Score` with `api_duration_ms=350.2`
- **THEN** the resulting dict contains `"api_duration_ms": 350.2`

#### Scenario: from_dict handles missing api_duration_ms
- **WHEN** `Score.from_dict()` is called with a dict that has no `api_duration_ms` key
- **THEN** the returned `Score` has `api_duration_ms=None`
