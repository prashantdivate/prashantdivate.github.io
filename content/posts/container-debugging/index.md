+++
title = "Debugging containers without losing the evidence"
date = 2026-09-09T09:00:00+05:30
draft = false
description = "Before restarting everything, capture the state that explains what happened. A small, read-only starting point for an investigation."
tags = ["Containers", "Linux"]
art = "containers"
sample = true
+++

The temptation is familiar: a container stops responding, so restart the stack and see whether the problem disappears. That may restore service, but it can also make the original failure harder to understand.

This starter note suggests a read-only first pass. Adjust the commands to the Podman version and permissions on your device. It does not prescribe a recovery action.

## Ask three separate questions

**Does the container exist?** A missing container is different from a stopped one.

**What does the runtime report?** State, exit code, and configured health checks give different pieces of evidence.

**What did the application report?** Runtime state alone does not explain a failed socket connection, unavailable service, or unexpected application exit.

Keep the host timestamp and the relevant application timestamps together when building a timeline.

## Capture a small snapshot

The following commands inspect state without removing or restarting containers. The example uses a container named `my-app`; replace it with a real name.

```bash
# Record host context and list all containers, including stopped ones.
date -Is
uname -r
podman ps -a

# Inspect the selected container and read its recent log output.
podman inspect my-app
podman logs --timestamps --tail 200 my-app
```

`podman inspect` provides detailed object information. `podman logs` reads the logs available to the runtime. Available log history depends on the logging setup and retention settings; no command can recover output that was never stored.

## Look outside the container

Check the prerequisites the application expects. Is its persistent directory mounted? Is the required socket present? Did its upstream service start? Does the host have enough free storage?

```bash
# Read-only host checks.
df -h
free -h
```

A process failure and an environment failure can produce similar symptoms. Avoid changing several things at once before recording the initial conditions.

## Separate restoration from explanation

Operational urgency may require a restart. Record what you captured, what you changed, and whether the symptom disappeared. A successful restart is an observation, not proof of a root cause.

A useful incident note distinguishes the visible symptom, the available evidence, the immediate restoration, and the follow-up test needed to confirm a cause.

## References

- [Podman inspect documentation](https://docs.podman.io/en/latest/markdown/podman-inspect.1.html)
- [Podman logs documentation](https://docs.podman.io/en/latest/markdown/podman-logs.1.html)
