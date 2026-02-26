# XInput vs joypad-os comparison

Comparison of OGX-Mini XInput (Xbox 360) with joypad-os for descriptor and runtime behavior, to align with what works on the 360.

## Descriptors

| Item | joypad-os | OGX-Mini (after alignment) |
|------|-----------|-----------------------------|
| **Device** | 0x045E / 0x028E, bcd 0x0114, bNumConfigurations = 1 | Same (byte-identical) |
| **Config** | 153 bytes, 4 interfaces, bConfigurationValue 1, bMaxPower 0xFA | Same (byte-identical) |
| **Config callback** | `tud_descriptor_configuration_cb(uint8_t index)` — ignores `index`, returns mode-specific config | Now return `nullptr` for `index != 0` (single config) |
| **String 4 (XSM3)** | 96-char buffer, **full** security string (no truncation) | Was truncated to 31 chars; now use full length in dedicated buffer |

## Mode / enumeration

| Item | joypad-os | OGX-Mini |
|------|-----------|----------|
| **When XInput is active** | `output_mode` loaded from flash before USB init; device presents XInput descriptors from first enumeration | Fixed XInput driver; always present XInput from first enumeration |
| **Driver registration** | `usbd_app_driver_get_cb()` returns `driver_count = 1`, `tud_xinput_class_driver()` when mode is XINPUT | Single driver from `DeviceManager::get_driver()->get_class_driver()` (XInput) |

## Control transfer handling

| Item | joypad-os | OGX-Mini |
|------|-----------|----------|
| **Vendor callback** | `tud_vendor_control_xfer_cb()` calls `tud_xinput_vendor_control_xfer_cb()` when `output_mode == XINPUT` | `tud_vendor_control_xfer_cb()` forwards to active driver `vendor_control_xfer_cb()` |
| **Class driver control** | `xinput_control_xfer_cb()` returns `true` and does **nothing**; XSM3 is handled only in vendor callback | We forward class `control_xfer_cb` to driver `vendor_control_xfer_cb()` so both paths reach XSM3 |

## XSM3 runtime (already aligned)

- XSM3 init at driver init (not in 0x81 callback).
- 0x82 / 0x87: only set state; crypto in `process()` loop.
- 0x83: 46 bytes init, 22 bytes verify.
- 0x86: state 1 = processing, 2 = ready.

## Changes made from this comparison

1. **Configuration descriptor** — `get_descriptor_configuration_cb(index)`: return `nullptr` when `index != 0` (we have one config).
2. **String descriptor index 4** — Use a 96-element buffer and the **full** XSM3 security string (no 31-character truncation from `get_string_descriptor()`).

If the 360 still does not send XSM3 requests after these fixes, next steps: confirm joypad-os on the same 360 shows XSM3 traffic, and/or add logging of **all** control requests (e.g. in TinyUSB) to see if any vendor/class traffic arrives.
