# AGENTS.md

## Purpose

This file defines **persistent project guidance** for OpenAI Codex.  
Codex must read and follow these instructions when generating, modifying, or reviewing code in this repository.

If instructions in this file conflict with ad-hoc user prompts, **this file takes precedence unless explicitly overridden**.

---

## Project Overview

**Project name:** Feature Class Profiler – test data generator (fc_profiler_create_testdata.py)
**Primary domain:** GIS / data audit
**Primary language:** Python
**Target runtime:** Python 3.13.7 (ArcGIS Pro 3.6)

**High-level goals:**
- Script creation of geodatabase(s), feature class, fields, rows
- The resulting data is used with unit and integration tests for "fc_profiler"


## Coding Conventions (Must Follow)

### General
- Write **clear, explicit, readable code**
- Prefer **explicit over clever**
- Avoid unnecessary abstraction
- Favor small, composable functions
- Write for ease of reading and maintainability
- Keep the solution to a single file
- If requirements.md specifies hardcoded paths/env, implement exactly; do not generalize to CLI args.

### Python Standards (if applicable)
- Follow **PEP 8**
- Use **type hints** for public functions
- Prefer f-strings over `.format()`
- No global state unless explicitly justified

### Naming
- `snake_case` for variables and functions
- `PascalCase` for classes
- Constants in `UPPER_SNAKE_CASE`
- Avoid ambiguous abbreviations unless domain-standard

### Imports
- Standard library first
- Third-party libraries second
- If importing arcpy, use a library in arcpy where a suitable library exists
- Local imports last
- Avoid wildcard imports except when importing ArcPy extension toolboxes where that is established project practice (e.g., arcpy.sa). Otherwise prefer explicit imports
- Remove unused imports; keep only what is required


### ArcGIS Pro / ArcPy constraints
 - Codex cannot execute ArcPy here; still write ArcPy code as required; include local run instructions and validations
 - Assume ArcGIS Pro is installed; script runs inside the ArcGIS Pro conda env; no third-party deps.
 - Target: Python environment is 3.13.7
 - Use arcpy.management.* tools and arcpy.da.InsertCursor 
 - Use SHAPE@ for geometry and wrap cursors in with blocks
 - Prefer arcpy.SpatialReference(<epsg>) over WKT strings
 - use arcpy.Describe(fc).spatialReference.factoryCode == <epsg> when comparing coordinate systems
 - Prefer arcpy.PointGeometry, arcpy.Array, arcpy.Polyline, arcpy.Polygon patterns for geometry creation
 - Prefer arcpy.ClearWorkspaceCache_management() before delete attempts (when applicable), and log potential lock sources.


---

## Logging & Error Handling

- Use the project’s standard logging configuration. Do not modify setup_logger() / CSV format unless explicitly requested.
- Do not use `print()` for operational logging.  print() is acceptable only as a fallback inside logger setup failure paths (when logging is not yet available).
- Raise meaningful exceptions
- Fail fast on invalid inputs

---
## Validation

Every validation failure must (1) log error with expected vs actual, then (2) raise.

---
## Dependency Management

- Do not introduce new dependencies without justification
- Prefer existing libraries already in use
- Document any new dependency in:
  - `pyproject.toml`
  - `README.md` (if user-facing)

---

## Git & Pull Request (PR) Guidelines

### Commit Messages
- **Use the commit message template defined in `.gitmessages`**
- Keep commits focused and atomic
- Do not mix formatting changes with logic changes

### Branch Naming
```
feature/<short-description>
fix/<short-description>
refactor/<short-description>
```

### Pull Requests Must Include
- Clear description of **what changed and why**
- Reference to related issue/ticket (if applicable)
- Notes on testing performed
- Any known limitations or follow-ups

Codex should **follow these conventions when generating PR descriptions or commit messages**.

---

## What Codex Should NOT Do

- Do not reformat unrelated files
- Do not introduce new architectural patterns unprompted
- Do not remove existing functionality unless explicitly instructed
- Do not assume undocumented behavior

---

## When in Doubt

If requirements are unclear:
1. Ask a clarifying question **before** generating code
2. State assumptions explicitly
3. Prefer the simplest viable solution

---

## End of Instructions
