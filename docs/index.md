# Pyronear Analytics

<div class="analytics-hero">
  <p class="analytics-kicker"></p>
  <p class="analytics-lead">
    Pyronear Analytics is the home for operational analysis built from data produced
    by deployed stations and backend systems. It turns embedded-computer telemetry,
    camera metadata, backend records, and platform usage signals into reviewable
    artifacts that can support monitoring, product decisions, and public-facing
    tools.
  </p>
</div>

<div class="analytics-card-grid analytics-card-grid-three">
  <a class="analytics-card" href="quickstart.html">
    <span class="analytics-card-label">Guide</span>
    <strong>Quickstart</strong>
    <span>Install the workspace, run checks, and publish a fixture artifact.</span>
  </a>
  <a class="analytics-card" href="pyronear-api.html">
    <span class="analytics-card-label">Source</span>
    <strong>Pyronear API</strong>
    <span>Review the implemented dlt source boundary and camera resource contract.</span>
  </a>
  <a class="analytics-card" href="pyromap.html">
    <span class="analytics-card-label">Workflow</span>
    <strong>Pyromap</strong>
    <span>Understand the camera map workflow, contracts, and runbooks.</span>
  </a>
</div>

Guides are hands-on paths, Sources describe ingestion contracts, Workflows
explain end-to-end applications, and Package Reference is generated from the
Python modules.

```{toctree}
:maxdepth: 2
:hidden:

Home <self>
```

```{toctree}
:maxdepth: 2
:caption: GUIDES
:hidden:

Quickstart <quickstart>
```

```{toctree}
:maxdepth: 2
:caption: SOURCES
:hidden:

Overview <sources>
Pyronear API <pyronear-api>
```

```{toctree}
:maxdepth: 2
:caption: WORKFLOWS
:hidden:

Pyromap <pyromap>
```

```{toctree}
:maxdepth: 1
:caption: PACKAGE REFERENCE
:hidden:

Analytics <reference/analytics/analytics>
Sources <reference/sources/sources>
Pyromap <reference/pyromap/pyromap>
```
