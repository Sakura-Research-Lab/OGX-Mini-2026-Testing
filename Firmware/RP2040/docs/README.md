# OGX-Mini RP2040 Firmware — Documentation

Documentation for the OGX-Mini 2026 RP2040 firmware (controller adapter for OG Xbox, XInput, PS3, Switch, Wii U, etc.).

## Contents

| Document | Description |
|----------|-------------|
| [IMPROVEMENTS.md](IMPROVEMENTS.md) | Improvements and fixes applied to this firmware (PS3 driver, latency, etc.). |

## Building

See the project root and `scripts/build-with-vs.ps1` (or CMake directly) for build instructions. Board is selected via CMake `OGXM_BOARD` (e.g. `PI_PICO`, `PI_PICO2W`, `RP2040_ZERO`).

## Configuration

- **Board / driver:** Set at CMake configure time (`OGXM_BOARD`, fixed driver options).
- **Latency:** `MAIN_LOOP_DELAY_US` in `src/Board/Config.h` (or override via CMake). See [IMPROVEMENTS.md](IMPROVEMENTS.md#latency).
