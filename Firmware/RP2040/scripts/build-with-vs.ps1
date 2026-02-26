# Build OGX-Mini firmware for Pico 2 W, using Visual Studio's host compiler for SDK tools (pioasm, picotool).
# Run from RP2040 folder: .\scripts\build-with-vs.ps1

param(
    [string] $BuildDir = "build_pico2w",
    [string] $Config = "Release",
    [string] $FixedDriver = "",       # e.g. PS3, XINPUT to lock output mode (no combos)
    [switch] $FixedDriverAllowCombos  # if -FixedDriver set: allow combos to change mode
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RP2040Dir = Split-Path -Parent $ScriptDir
$VsPath = "${env:ProgramFiles}\Microsoft Visual Studio\2022\Community"
if (-not (Test-Path $VsPath)) {
    $VsPath = "${env:ProgramFiles}\Microsoft Visual Studio\2022\Professional"
}
if (-not (Test-Path $VsPath)) {
    $VsPath = "${env:ProgramFiles}\Microsoft Visual Studio\2022\Enterprise"
}
$Vcvars = "$VsPath\VC\Auxiliary\Build\vcvars64.bat"
if (-not (Test-Path $Vcvars)) {
    Write-Error "Visual Studio 2022 not found (no vcvars64.bat). Install VS 2022 with 'Desktop development with C++' workload."
}

$PicoSdkPath = Join-Path $RP2040Dir "..\external\pico-sdk"
$ConfigureArgs = @(
    "-G", "Ninja",
    "-DCMAKE_BUILD_TYPE=$Config",
    "-DOGXM_BOARD=PI_PICO2W",
    "-DPICO_SDK_PATH=$($PicoSdkPath -replace '\\','/')"
)
# Always pass OGXM_FIXED_DRIVER so the output filename matches the built mode (avoids reusing cached PS3/XINPUT name)
if ($FixedDriver) {
    $ConfigureArgs += "-DOGXM_FIXED_DRIVER=$FixedDriver"
    if ($FixedDriverAllowCombos) { $ConfigureArgs += "-DOGXM_FIXED_DRIVER_ALLOW_COMBOS=ON" }
} else {
    $ConfigureArgs += "-DOGXM_FIXED_DRIVER="
}
$ConfigureArgsStr = $ConfigureArgs -join " "

& cmd /c "call `"$Vcvars`" && cd /d `"$RP2040Dir`" && cmake -B `"$BuildDir`" $ConfigureArgsStr && cmake --build `"$BuildDir`" --config $Config"
exit $LASTEXITCODE
