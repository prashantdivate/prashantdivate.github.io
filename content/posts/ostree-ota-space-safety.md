---
title: "Designing Space-Safe OSTree Updates on Embedded Devices"
date: 2026-09-05T09:30:00+05:30
description: "How to prevent an OTA update from failing halfway because the device ran out of persistent storage."
tags: ["OSTree", "OTA", "Embedded Linux", "Reliability"]
categories: ["OTA"]
featured: true
reading: "8 min"
---

Embedded devices are often deployed with tightly sized root filesystems. That makes OTA storage planning a reliability problem, not a housekeeping problem.

A robust updater should estimate required space, preserve a safety margin, perform only safe cleanup, and retry the preflight check before touching the active deployment.

## The safety rule

Never delete objects that belong to either the active deployment or the rollback deployment. Cleanup should only target unreachable objects.

```bash
ostree --repo=/sysroot/ostree/repo prune --refs-only
```

The updater can then re-check free space and proceed only if the configured margin is restored.

## Why this matters

A good OTA system fails **before** modifying the system. It should never discover a predictable storage problem after the update has already started.
