+++
title = 'An engineer. Always building.'
type = 'about'
description = 'Prashant Divate: embedded Linux, Yocto, open source, and the systems work that turns hardware into useful products.'
+++

## The work behind the interface

I am Prashant Divate, an embedded Linux engineer with 7+ years of experience across Yocto distro engineering, BSP integration, platform bring-up, secure updates, and production release workflows. My day-to-day thinking usually sits around Yocto, Linux services, OTA, secure boot, containers, board integration, and the automation that makes field work less painful.

I describe myself as an artist by nature and a developer by passion. That shows up in how I work: I like systems that are technically sound, but I also care about clarity, shape, and whether the next person can understand the idea without fighting the explanation.

This site is where I collect blogs, project notes, experiments, and open-source ideas. Some posts are practical guides. Some are diagrams and mental models. Some are simply a way to preserve what I learned while solving a real engineering problem.

## What I Build

At MAD Elevator, I work on Yocto and platform development activities for connected device products, bridging customer needs, product engineering, and field deployment realities. Recent work includes hardware integrations, AWS-backed CI/CD infrastructure, secure device fleet management, and proof-of-concepts for new product ideas.

Before that, at Resideo, I led CoreOS and custom Linux distribution work for next-generation home security devices across NXP i.MX6, i.MX8, i.MX93, and STM32MP157 platforms. That work included multi-architecture distro support, Docker-based build improvements, OSTree updates, Matter integration, Weston/Wayland graphics, release management, and mentoring engineers across global teams.

Earlier at Tata Elxsi, I worked on embedded Linux platforms for NXP i.MX boards using Yocto, with secure boot, OS hardening, RAUC updates, kernel customization, CI/CD, factory flashing automation, and client-facing platform delivery.

## How I Think

**Understand the boundary.** A board, a kernel, a container, and an application see different parts of the same system. Knowing where responsibility changes hands makes debugging more useful.

**Keep the evidence.** A good explanation should help someone repeat the observation, not just repeat the conclusion.

**Automate the boring part.** If a task has to happen across many devices, builds, releases, or deployments, it deserves a repeatable path.

**Make the next change easier.** A small tool, a clean note, or a better build step should reduce the work needed tomorrow.

## Open-source work

I like open source because it turns private problem solving into shared infrastructure. Yocto-Lens focuses on Yocto/OpenEmbedded metadata analysis, style checks, dependency validation, patch auditing, and release-friendly reporting. VulnTrack makes Yocto CVE, SBOM, and vulnerability reports easier to review and share. I have also built helper tooling around Yocto metadata and layer maintenance because I know how much time teams lose to repetitive build-system work.

## What I Write About

Most of my writing comes from real questions: how to make a device reachable in the field, how to reason about update systems, how to keep a Linux image maintainable, how OP-TEE fits into an i.MX boot flow, or how to explain a security boundary without hiding behind buzzwords.

The goal is simple: learn deeply, explain clearly, and leave behind something useful for the next engineer.

## About this site

This is a static website built with Hugo. Posts are Markdown files, and GitHub Actions publishes the generated website to GitHub Pages. There is no analytics service, tracking pixel, or newsletter database in this package.

The animated graphics are conceptual illustrations, not live device telemetry. Theme and motion preferences are stored only in your browser.
