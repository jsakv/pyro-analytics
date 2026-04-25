# Pyronear Station

`station` is the reusable publisher library for Pyronear station map artifacts.

The package owns source adapters, schema validation, location privacy policy, H3 aggregation, GeoJSON serialization, and publication boundaries for station map data. The root `analytics` package owns CLI wiring and may depend on `station`; `station` must not import from `analytics`.

This scaffold intentionally does not implement source fetching, transforms, or uploads yet.
