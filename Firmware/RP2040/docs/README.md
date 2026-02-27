# OGX-Mini RP2040 Firmware

Firmware for the OGX-Mini controller adapter on **RP2040** (e.g. Raspberry Pi Pico, Pico 2 W). The adapter accepts input from Bluetooth controllers (e.g. PS5, Xbox One, Switch Pro) and presents them to a console or PC as a single USB gamepad in the chosen output mode.

## Supported output modes (USB device)

| Mode | Target |
|------|--------|
| **XInput** | Xbox 360 (wired controller + XSM3 auth) |
| **DInput** | PC (DirectInput), legacy |
| **PS3** | PlayStation 3 |
| **Switch** | Nintendo Switch (wired) |
| **Wii U** | Wii U |
| **Xbox OG** | Original Xbox (XID: Gamepad, Steel Battalion, XRemote) |
| **PS Classic** | PlayStation Classic |
| **Web App** | Configuration / profiles over CDC |

On **Pico 2 W**, Bluetooth (Bluepad32) runs on Core1; USB device runs on Core0. You can build with a **fixed** output mode (e.g. XINPUT only) or with **button combos** to switch modes at runtime (e.g. Start + D-pad held ~3 s).

## Xbox 360 (XInput) support

XInput mode works on **Xbox 360** with full **XSM3** authentication:

- Descriptors and XSM3 flow aligned with [joypad-os](https://github.com/joypad-ai/joypad-os) for console compatibility.
- Single configuration; full XSM3 security string; init/verify handled in the main loop.
- USB is initialized before Core1 (BT) so the 360 can enumerate even while Bluetooth firmware loads.

See [XInput_joypad-os_comparison.md](XInput_joypad-os_comparison.md) for technical details.

## Input latency (PS5 / Xbox One over Bluetooth)

- **Always send latest state** — In XInput (and similar) mode, the adapter sends the current gamepad state whenever the USB endpoint is free, instead of only when the BT stack flags “new” data. The host (e.g. 360) gets updates at its poll rate (e.g. 4 ms) with the freshest state.
- **Low-latency default** — The main loop uses **no** added delay by default (`MAIN_LOOP_DELAY_US=0`), so there is no extra delay between reading the controller and sending to USB.

To trade a little latency for lower CPU use, configure with `MAIN_LOOP_DELAY_US=250` (or higher). See [IMPROVEMENTS.md](IMPROVEMENTS.md#latency-reduction).

## Building

Build with **CMake** from the `Firmware/RP2040` directory. Required:

- **Board:** `OGXM_BOARD` (e.g. `PI_PICO2W`, `PI_PICO`, `RP2040_ZERO`).
- **Pico SDK:** `PICO_SDK_PATH` pointing at the SDK (or use the project’s submodule).
- **Optional:** `OGXM_FIXED_DRIVER` to lock output mode (e.g. `XINPUT`, `PS3`); `OGXM_FIXED_DRIVER_ALLOW_COMBOS=ON` to keep combos when a fixed driver is set.
- **Optional:** `MAIN_LOOP_DELAY_US` (default `0`) to set main-loop delay in microseconds.

Outputs (`.elf`, `.uf2`, etc.) are produced in the chosen build directory; flash the `.uf2` to the board.

## Configuration

- **Board and driver:** Set at CMake configure time (`OGXM_BOARD`, `OGXM_FIXED_DRIVER`, `OGXM_FIXED_DRIVER_ALLOW_COMBOS`).
- **Latency:** `MAIN_LOOP_DELAY_US` — default `0` (low latency). Override via CMake (e.g. `-DMAIN_LOOP_DELAY_US=250`) if desired. See [IMPROVEMENTS.md](IMPROVEMENTS.md#latency-reduction).

## Documentation

| Document | Description |
|----------|-------------|
| [IMPROVEMENTS.md](IMPROVEMENTS.md) | Firmware improvements: PS3 fixes, latency, XInput/360. |
| [XInput_joypad-os_comparison.md](XInput_joypad-os_comparison.md) | XInput vs joypad-os (descriptors, XSM3, control handling). |
