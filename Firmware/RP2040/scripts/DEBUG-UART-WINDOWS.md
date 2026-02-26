# Debug build and UART on Windows

## Build Debug XInput firmware (Pico 2 W)

From the `RP2040` folder:

```powershell
.\scripts\build-with-vs.ps1 -Config Debug -FixedDriver XINPUT
```

Output: `build_pico2w\OGX-Mini-v1.0.0a4-PI_PICO2W-XINPUT-Debug.uf2`

Flash this .uf2 to the Pico 2 W. Debug builds enable:

- **UART** for log output (TX = GPIO 0, RX = GPIO 1)
- **OGXM_LOG** / **XSM3** messages (e.g. `XSM3: 0x81 GET_SERIAL`, `XSM3: 0x86 GET_STATE`)

## Reading UART on Windows

### 1. Connect the Pico 2 W UART to the PC

- **Pico 2 W** (and most Pico boards): **GPIO 0 = UART TX** (from Pico), **GPIO 1 = UART RX** (into Pico).
- Use a **USB–serial adapter** (e.g. CP2102, FT232, CH340) or a second Pico in UART mode:
  - Connect adapter **RX** to Pico **GPIO 0 (TX)**.
  - Connect **GND** to **GND**.
  - Do **not** connect adapter TX to Pico unless you need to send data; for log viewing, RX + GND is enough.

### 2. Find the COM port

- Open **Device Manager** → **Ports (COM & LPT)**.
- Note the COM number for your USB–serial device (e.g. **COM4**).

### 3. Open a serial terminal

**Option A – PuTTY (recommended)**

1. Download [PuTTY](https://www.putty.org/).
2. Run PuTTY → **Session**:
   - **Connection type**: Serial.
   - **Serial line**: `COM4` (use your port).
   - **Speed**: **115200** (Pico default).
3. Click **Open**.

**Option B – Windows Terminal / PowerShell (if serial module available)**

```powershell
# List serial ports (PowerShell)
[System.IO.Ports.SerialPort]::getportnames()
```

Then use a terminal that can open a serial port (e.g. PuTTY, or a VS Code serial extension).

**Option C – VS Code**

- Install an extension such as **Serial Monitor** or **Serial Port Utility**.
- Select the correct COM port and **115200** baud.

### 4. Baud rate

Use **115200** unless the firmware is built with a different `PICO_DEFAULT_UART_BAUD_RATE`.

### 5. What you’ll see (XInput debug)

When the controller is used (or the XSM3 test script runs), you should see lines like:

```
OGXM: XSM3: 0x81 GET_SERIAL
OGXM: XSM3: 0x86 GET_STATE
OGXM: XSM3: 0x82 challenge init received, processing
OGXM: XSM3: 0x83 sending init response (0x30 bytes)
...
```

On an **Xbox 360** you’ll see the full auth sequence (0x81 → 0x82 → 0x83 → 0x86 → 0x87 → 0x83). On **Windows**, only 0x81 and 0x86 may appear unless you run the test script.
