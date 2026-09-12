+++
title = "Security starts before the application"
date = 2026-09-05T09:00:00+05:30
draft = false
description = "Boot integrity, runtime isolation, and credential handling solve different problems. Draw the boundaries before choosing the mechanism."
tags = ["Security", "Embedded"]
art = "security"
sample = true
+++

Security features are easier to reason about when the question comes before the mechanism.

"Can I trust the software that booted?" is different from "which component may read a credential?" Both matter, but answering one does not automatically answer the other.

## Start with the asset

Identify what needs protection: software integrity, an authentication credential, a configuration value, or user data. Then identify which access paths are relevant to that asset.

A diagram should include operational details such as provisioning, rotation, recovery, and decommissioning. These are not administrative extras; they affect how a security mechanism works over its lifetime.

## Keep mechanisms distinct

Boot verification is about deciding what code may be loaded under a platform's trust policy. Runtime isolation is about limiting access while the system executes. Secure storage is about protecting data under a particular access and threat model.

A trusted execution environment can form part of a design, but it is not an automatic solution to every threat. Integration, key ownership, update policy, and the surrounding operating system still need explicit decisions.

## Describe the boundary you rely on

A useful design record names the component enforcing the boundary and the assumptions behind it. For example: where does verification happen, which key is trusted, who can change that trust configuration, and what happens when verification fails?

Avoid statements such as "the key is encrypted, therefore safe" without explaining where the decryption key lives and who can invoke the operation.

## Design the lifecycle

Think through a lost device, an expired credential, a failed update, and a device that must be retired. A mechanism that works only at first boot may not match the lifetime of the product.

This note intentionally contains no fuse-programming instructions or board-specific provisioning commands. Those operations require the exact hardware documentation and a reviewed recovery plan.

## References

- [OP-TEE documentation](https://optee.readthedocs.io/en/latest/)
- [OP-TEE architecture](https://optee.readthedocs.io/en/latest/architecture/index.html)
