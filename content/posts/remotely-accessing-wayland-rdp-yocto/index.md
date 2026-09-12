+++
title = "Remotely Accessing Wayland-based Applications using RDP client in Yocto Image"
date = 2026-09-12T00:02:00+05:30
draft = false
description = "Configure Weston, FreeRDP, TLS keys, and RDP clients to remotely access Wayland applications running in a Yocto image."
tags = ["Yocto", "Wayland", "Weston", "RDP", "Remote Access"]
art = "wayland-rdp"
+++

Originally published on Medium: [Remotely Accessing Wayland-based Applications using RDP client in Yocto Image](https://medium.com/@prashant-divate/remotely-accessing-wayland-based-applications-using-rdp-client-in-yocto-image-55f38b67e0aa)

Get more detailed information of this topic on the [official website](https://thepenguintech.com/) with working demo.

Remote access to graphical applications running on embedded systems can be a valuable tool for developers and administrators. In this article, we'll explore how to remotely access Wayland applications in a Yocto image using RDP (Remote Desktop Protocol). This method leverages the Wayland display server, specifically Weston, and the FreeRDP library to achieve remote access.

![Wayland RDP setup](/images/blogs/remotely-accessing-wayland-rdp-yocto/image-01.webp)

## Before You Begin

Ensure that:

1. Your Yocto image includes Weston with RDP compositor and screen sharing enabled. You can find the Yocto integration [here](https://github.com/prashantdivate/meta-sirius/blob/master/recipes-graphics/wayland/weston_%25.bbappend).
2. FreeRDP is a dependency of the RDP compositor and should be included in your Yocto image.
3. On your target device, make sure the FreeRDP package is installed, and TLS certificates and keys (`server.crt` and `server.key`) are in the `/etc/freerdp/keys` directory.

## Generating TLS Certificates

To generate TLS certificates for RDP, use the `winpr-makecert` tool in the `/etc/freerdp/keys` directory:

```bash
winpr-makecert -rdp -path $PWD
```

## Configuring Weston

Add these lines in the `weston.ini` configuration file:

```ini
[core]
modules=systemd-notify.so

[screen-share]
command=/usr/bin64/weston --backend=rdp-backend.so --shell=fullscreen-shell.so --rdp-tls-cert=/etc/freerdp/keys/server.crt --rdp-tls-key=/etc/freerdp/keys/server.key --no-clients-resize
start-on-startup=true
```

## Launching Weston

Start Weston with this command to enable RDP access:

```bash
weston --debug --ttty=1 --backend=fbdev-backend.so --modules=systemd-notify.so,screen-share.so --use-gl=1 --log=${XDG_RUNTIME_DIR}/weston.log $OPTARGS
```

## Accessing the Target Remotely

To remotely access Wayland applications, launch the RDP client on your host machine.

For Wayland:

```bash
wlfreerdp /v:<target_ip> /log-level:TRACE
```

For X11:

```bash
xfreerdp /v:<target_ip>
```

Additionally, Remmina can also be used for access.

![Weston desktop shell RDP connection](/images/blogs/remotely-accessing-wayland-rdp-yocto/image-02.png)

As shown in the image above, we can control the remote device and pass commands from the host machine.

Configuring Weston with the RDP compositor and FreeRDP allows easy access to Wayland applications on Yocto-based systems. Remote access enhances the flexibility and utility of embedded systems for a wide range of applications. This method is powerful for development and troubleshooting headless devices in Yocto Project-based environments.

## Reference

To integrate this in a Yocto image, I already did it in the `meta-sirius` layer. Check out my GitHub repo: [prashantdivate/meta-sirius](https://github.com/prashantdivate/meta-sirius)
