# Firmware Improvements

Improvements and fixes applied to the OGX-Mini RP2040 firmware in this project.

**Version:** From **v1.0.0a3** the version was bumped to **v1.0.0a4** to reflect Wii U controller fixes, Gamecube USB mode, PS3 driver fixes, and latency improvements (see below).

---

## PS3 mode — input delays and stuck inputs

**Source:** Fixes from [OGX-Mini-Plus](https://github.com/guimaraf/OGX-Mini-Plus) (v1.1.1) — *“PS3 Driver Fixes - Fixed input delays and stuck inputs.”*

**File:** `src/USBDevice/DeviceDriver/PS3/PS3.cpp`

### Changes

1. **L2/R2 axis values**
   - `report_in_.l2_axis` and `report_in_.r2_axis` are now set from `gp_in.trigger_l` and `gp_in.trigger_r`.
   - Previously left at zero, which could cause stuck or incorrect trigger behaviour on PS3. Filling these is required for many PS3 games.

2. **Joystick centre and deadzone**
   - Replaced generic `Scale::int16_to_uint8()` (centre 128) with PS3-specific mapping:
     - Centre **0x7F (127)** and ~5% deadzone (~1640 on a ±32768 scale).
     - In deadzone, sticks report exactly 0x7F so the console does not see drift.
     - Outside deadzone, values are scaled into 0–254 so 127 remains the logical centre.
   - Avoids stick drift and “stuck” stick behaviour caused by wrong centre or jitter.

3. **D-pad in analog mode**
   - When `gamepad.analog_enabled()` is true, D-pad axes (`up_axis`, `down_axis`, `left_axis`, `right_axis`) are now derived from the **digital** D-pad bits instead of `gp_in.analog[ANALOG_OFF_*]`.
   - Prevents noisy analog D-pad values from causing stuck or wrong D-pad input on PS3.

4. **Face button axes (digital / non-analog branch)**
   - Corrected mapping so that:
     - `circle_axis` = BUTTON_B (was BUTTON_X)
     - `cross_axis` = BUTTON_A (was BUTTON_B)
     - `square_axis` = BUTTON_X (was BUTTON_A)
   - Circle / Cross / Square now match the intended face buttons.

---

## Latency reduction

**Goal:** Reduce input-to-output latency in the device (Core0) main loop.

### Main loop delay

- **Before:** The device loop used `sleep_ms(1)` every iteration, limiting the loop to ~1000 Hz and adding up to ~1 ms before the next read/send.
- **After:** Configurable delay in **microseconds** via `MAIN_LOOP_DELAY_US` in `src/Board/Config.h`:
  - **Default: 250 µs** — loop runs at ~4000 Hz; average extra delay reduced (e.g. from ~0.5 ms to ~0.125 ms).
  - **0** — no delay; loop runs as fast as possible for minimum latency (higher CPU use).
  - **1000** — 1 ms (same as original behaviour).

**Files changed:**

- `src/Board/Config.h` — added `MAIN_LOOP_DELAY_US` and comment (override via CMake documented).
- `src/OGXMini/Board/Standard.cpp` — use `sleep_us(MAIN_LOOP_DELAY_US)` when `> 0`, and `#include <pico/time.h>`.
- `src/OGXMini/Board/PicoW.cpp` — same.
- `src/OGXMini/Board/Four_Channel_I2C.cpp` — same.

### How to use

| Goal | Setting |
|------|--------|
| Lower latency (default) | Leave `MAIN_LOOP_DELAY_US` at **250** (already set). |
| Minimum latency | Set `MAIN_LOOP_DELAY_US=0`, e.g. in CMake: `add_compile_definitions(MAIN_LOOP_DELAY_US=0)` or `-DCMAKE_CXX_FLAGS="-DMAIN_LOOP_DELAY_US=0"`. |
| Slightly lower CPU use | Use e.g. `MAIN_LOOP_DELAY_US=500`. |

### Notes

- Core1 (USB host / gamepad polling) already runs with no sleep in its loop.
- USB full-speed has a 1 ms frame; reports are still limited by that; the improvement is that each report uses the **latest** input.
- For lowest end-to-end latency, use a **wired** controller and a USB host board; Bluetooth (e.g. Pico W) adds more latency.

---

## Summary

| Area | Improvement |
|------|-------------|
| **PS3** | Stuck inputs and input delays addressed via L2/R2 axes, joystick centre/deadzone, D-pad handling, and face button mapping. |
| **Latency** | Main loop delay reduced from 1 ms to 250 µs by default, with option for 0 µs for minimum latency. |
