# Overview

`packages/sources` owns reusable dlt source definitions. It is the ingestion
boundary for external systems that analytics workflows consume.

Use this package when adding or changing how Pyronear Analytics reads from an
external system. Keep workflow-specific decisions in workflow packages such as
`pyromap`; `sources` should only describe how to extract source records.

## What Is dlt?

[dlt](https://dlthub.com/docs/intro) is the Python library this repository uses
for ingestion. In dlt terms, a source groups one or more resources, and a
resource describes data that can be loaded into a destination table. dlt handles
common ingestion concerns such as REST API extraction, authentication,
normalization, schema inference, loading, and access to the loaded dataset.

## Why Use dlt?

In this repository, dlt stops at ingestion. A dlt pipeline loads private source
records into a configured destination such as DuckDB. Workflow packages then read
those loaded rows and perform their own validation, transformation, privacy
checks, serialization, and publication outside dlt.

That boundary keeps source definitions reusable. The same backend source can be
used by Pyromap today and by future workflows later without importing map
privacy rules, GeoJSON serialization, or publisher settings.

## Package Boundary

The package is responsible for:

- define dlt sources and resources
- describe backend API access
- keep credentials and runtime destination choices outside package code

The package must not contain:

- workflow-specific transformation logic
- privacy or public-artifact policy
- GeoJSON serialization
- local or S3 publication logic

The currently implemented source is `sources.backend.backend_source`, which
exposes the Pyronear backend `cameras` resource.

For the implemented source contract, see [Pyronear API](pyronear-api.md).
