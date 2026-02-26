#!/usr/bin/env python3
"""
Test XSM3 (Xbox 360 Security Method 3) vendor requests on Windows.

Sends control transfers 0x81 (get serial/ID) and 0x86 (get auth state) to verify
the OGX-Mini XInput device responds correctly. Full auth (0x82/0x83/0x87) requires
an Xbox 360 console or a host that can generate valid challenge data.

Requirements:
  pip install pyusb

On Windows you may need to replace the Xbox 360 driver with WinUSB so libusb can
claim the device: use Zadig (https://zadig.akeo.ie/) and select the "Xbox 360 Controller"
then "Replace Driver" with WinUSB. The controller will stop working as a gamepad
until you restore the original driver (Zadig can do that too).

Usage:
  python scripts/test_xsm3_windows.py
  # or from RP2040 folder:
  python test_xsm3_windows.py
"""

import sys

try:
    import usb.core
    import usb.util
except ImportError:
    print("Install pyusb: pip install pyusb")
    sys.exit(1)

# Microsoft Xbox 360 Controller
VID, PID = 0x045E, 0x028E

# Vendor control: bmRequestType, bRequest
# 0x81 = GET serial/ID (0x1D bytes), 0x86 = GET state (2 bytes)
REQ_GET_SERIAL = 0x81
REQ_GET_STATE  = 0x86
SERIAL_LEN     = 0x1D
STATE_LEN      = 2


def find_device():
    dev = usb.core.find(idVendor=VID, idProduct=PID)
    if dev is None:
        print("No Xbox 360 controller (045E:028E) found.")
        return None
    return dev


def main():
    dev = find_device()
    if dev is None:
        sys.exit(1)

    try:
        if dev.is_kernel_driver_active(0):
            try:
                dev.detach_kernel_driver(0)
                print("Detached kernel driver for interface 0.")
            except usb.core.USBError as e:
                print("Could not detach kernel driver:", e)
                print("Try using Zadig to install WinUSB for this device.")
                sys.exit(1)
        dev.set_configuration()
    except usb.core.USBError as e:
        print("USB error:", e)
        print("If the device is in use by the Xbox 360 driver, use Zadig to replace it with WinUSB.")
        sys.exit(1)

    print("Device found. Testing XSM3 vendor requests...")
    ok = True

    # 0x81: Get serial/identification (29 bytes)
    try:
        data = dev.ctrl_transfer(
            0xC0,  # bmRequestType: Vendor, Device, IN
            REQ_GET_SERIAL,
            0, 0,
            SERIAL_LEN,
            timeout=1000,
        )
        if len(data) == SERIAL_LEN:
            print("  0x81 (GET_SERIAL): OK, 29 bytes")
            print("    First 8 bytes (hex):", " ".join(f"{b:02X}" for b in data[:8]))
        else:
            print("  0x81 (GET_SERIAL): unexpected length", len(data))
            ok = False
    except usb.core.USBError as e:
        print("  0x81 (GET_SERIAL): FAIL -", e)
        ok = False

    # 0x86: Get auth state (2 bytes; 2 = ready)
    try:
        data = dev.ctrl_transfer(
            0xC0,
            REQ_GET_STATE,
            0, 0,
            STATE_LEN,
            timeout=1000,
        )
        if len(data) >= 2:
            state = data[0] | (data[1] << 8)
            print("  0x86 (GET_STATE): OK, state =", state, "(2 = ready)")
            if state != 1 and state != 2:
                print("    (unexpected value; 1=processing, 2=ready)")
        else:
            print("  0x86 (GET_STATE): unexpected length", len(data))
            ok = False
    except usb.core.USBError as e:
        print("  0x86 (GET_STATE): FAIL -", e)
        ok = False

    if ok:
        print("\nXSM3 vendor requests succeeded. Device is responding to auth commands.")
        print("Full auth (0x82/0x83/0x87) is only run by an Xbox 360 console;")
        print("to verify that, plug the controller into a 360.")
    else:
        print("\nOne or more requests failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
