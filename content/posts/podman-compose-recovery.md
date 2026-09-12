---
title: "Recovering a Podman Compose Stack Without Making Things Worse"
date: 2026-08-22T10:00:00+05:30
description: "A practical pattern for reviving missing, exited or unhealthy containers on an embedded device."
tags: ["Podman", "systemd", "Containers", "Reliability"]
categories: ["Containers"]
featured: true
reading: "7 min"
---

A watchdog that blindly removes every container can turn a recoverable fault into a full application outage.

The safer pattern is to compare the desired compose services with the runtime state and repair only what is missing or unhealthy.

```bash
podman-compose ps
systemctl restart mad-matisse-gen3-containers.service
```

The systemd service remains the source of truth. The watcher observes health; it does not try to become a second orchestrator.

## Principle

Recovery logic should be **idempotent, targeted and observable**. If the repair path is more destructive than the failure, the watchdog itself becomes the incident source.
