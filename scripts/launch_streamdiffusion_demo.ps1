# Launch the local StreamDiffusion install (D:\Github\StreamDiffusion).
#
#   .\launch_streamdiffusion_demo.ps1              # TouchDesigner PNG bridge (default)
#   .\launch_streamdiffusion_demo.ps1 -Mode web    # webcam -> browser demo on :8080
#   .\launch_streamdiffusion_demo.ps1 -Mode screen # screen capture -> window
#
# Paths reference the verified install: Python 3.10 venv, torch 2.1.0+cu121.
param(
    [ValidateSet("td", "web", "screen")]
    [string]$Mode = "td",
    [string]$SdRoot = "D:\Github\StreamDiffusion",
    [int]$Webcam = 0
)

$python = Join-Path $SdRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    Write-Error "StreamDiffusion venv not found at $python. See skills/streamdiffusion-windows-install.md."
    exit 1
}

Set-Location $SdRoot
switch ($Mode) {
    "td" {
        Write-Host "TouchDesigner bridge: frames -> td_out\, OSC in :9000 / out :9001"
        & $python touchdesigner\td_bridge.py --config configs\sdturbo_fast.yaml --webcam $Webcam --no-window
    }
    "web" {
        Write-Host "Realtime img2img demo -> http://localhost:8080"
        $env:SD_MODEL = Join-Path $SdRoot "models\sd-turbo"
        Set-Location (Join-Path $SdRoot "demo\realtime-img2img")
        & $python main.py --port 8080 --acceleration xformers
    }
    "screen" {
        & $python examples\screen\main.py
    }
}
