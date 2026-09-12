+++
title = "Scaling IoT fleets: secure reverse SSH into Yocto"
date = 2026-05-21T09:00:00+05:30
draft = false
description = "How ShellHub can be integrated into a Yocto image so field devices can register automatically and expose secure reverse SSH access without public IPs or port forwarding."
tags = ["Yocto", "IoT", "Security", "ShellHub"]
art = "security"
+++

Field devices rarely live in friendly networks. They sit behind NAT, cellular links, customer firewalls, and deployment environments where direct SSH access is either impossible or unsafe to expose.

This blog walks through a practical pattern for solving that problem: integrate the ShellHub agent directly into a Yocto image, let the device create an outbound connection after first boot, and manage access centrally instead of opening inbound network paths.

Originally published on Medium: [Scaling IoT fleets: Secure Reverse SSH into Yocto for Automated Field Deployment](https://medium.com/@prashant-divate/scaling-iot-fleets-secure-reverse-ssh-into-yocto-for-automated-field-deployment-df27d54be7f3)

## Why Put Remote Access in the Image

For production IoT devices, manual setup does not scale. A field engineer should not need to install remote access tooling one device at a time, and the device should not require a public address just to be reachable later.

Building the agent into the Yocto image gives the fleet a predictable starting point:

- the agent is part of the firmware image
- systemd can start it automatically
- provisioning happens during boot
- devices can appear in the management dashboard without hands-on setup
- remote access works through an outbound connection

That keeps the field workflow closer to zero-touch provisioning: manufacture, flash, ship, connect, approve, and support.

## The Basic Architecture

The device runs `shellhub-agent` as a native service rather than depending on a container runtime. That matters for embedded targets where storage, memory, and boot complexity are tightly controlled.

At build time, the image receives the tenant or namespace information needed by the agent. At runtime, systemd starts the service, the agent reads its configuration, connects to the ShellHub server, and registers the device for approval.

The important detail is direction: the device initiates the connection outward. That avoids exposing SSH directly to the public internet and avoids asking customers to configure port forwarding.

## Yocto Configuration

The fleet identifier needs to be known before the image is built. In a Yocto setup, that can live in a distro or local configuration file:

```conf
SHELLHUB_TENANT_ID = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
SHELLHUB_SERVER_ADDRESS = "http://your-ec2-public-ip-or-domain"
```

For ShellHub Cloud, the custom server address may not be needed. For a self-hosted setup, the address points devices at your own server.

After deployment, the generated configuration can be checked on the target:

```bash
cat /etc/default/shellhub-agent
```

## Approval and Fleet Scale

ShellHub keeps newly registered devices pending until they are accepted. That is a useful security checkpoint, but it becomes tedious when devices are produced or deployed in large batches.

For mass onboarding, a small script can run on the management server, query pending devices through the ShellHub API, and approve the devices that match your deployment policy. The exact policy belongs to your environment: manufacturing batch, expected hostname, serial number, asset record, or another trusted source.

The key is to automate the approval path deliberately instead of training people to click through hundreds of devices by hand.

## Accessing the Device

Once approved, the device receives an SSH identity in ShellHub. Engineers can connect with a normal terminal client through the ShellHub gateway, or use the browser console for quick diagnostics.

The workflow gives embedded teams a support path that does not depend on VPN setup, static public IPs, or direct inbound SSH exposure.

## Takeaway

For Yocto-based IoT fleets, reverse SSH is most useful when it is part of the product image and lifecycle. ShellHub provides the access layer; Yocto provides repeatable image integration; systemd keeps the agent alive; and an approval workflow keeps onboarding controlled.

That combination turns remote access from an emergency workaround into a planned part of field deployment.
