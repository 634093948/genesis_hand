# MelBandRoformer Model Setup Script
# Run as Administrator

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "MelBandRoformer Model Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Set paths
$GenesisRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$ModelsDir = Join-Path $GenesisRoot "models"
$AudioModelsDir = Join-Path $ModelsDir "audio_encoders"

# Possible ComfyUI paths
$ComfyUIPaths = @(
    "e:\liliyuanshangmie\ComfyUI",
    "e:\liliyuanshangmie\twodog\ComfyUI",
    "$env:USERPROFILE\ComfyUI"
)

Write-Host "[1/4] Checking audio_encoders directory..." -ForegroundColor Yellow
if (-not (Test-Path $AudioModelsDir)) {
    Write-Host "[Create] $AudioModelsDir" -ForegroundColor Green
    New-Item -ItemType Directory -Path $AudioModelsDir -Force | Out-Null
} else {
    Write-Host "[Exists] $AudioModelsDir" -ForegroundColor Green
}

Write-Host ""
Write-Host "[2/4] Searching for MelBandRoformer model..." -ForegroundColor Yellow

$MelModel = $null

foreach ($ComfyPath in $ComfyUIPaths) {
    if (Test-Path $ComfyPath) {
        Write-Host "[Check] $ComfyPath\models" -ForegroundColor Gray
        $ModelsPath = Join-Path $ComfyPath "models"
        if (Test-Path $ModelsPath) {
            $Found = Get-ChildItem -Path $ModelsPath -Filter "MelBandRoformer*.safetensors" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
            if ($Found) {
                $MelModel = $Found.FullName
                Write-Host "[Found] $MelModel" -ForegroundColor Green
                break
            }
        }
    }
}

Write-Host ""
if (-not $MelModel) {
    Write-Host "[Error] MelBandRoformer model not found" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please ensure the model file exists in one of these locations:" -ForegroundColor Yellow
    foreach ($path in $ComfyUIPaths) {
        Write-Host "  - $path\models" -ForegroundColor Gray
    }
    Write-Host ""
    Write-Host "Model filename should be like: MelBandRoformer_fp32.safetensors" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[3/4] Creating symbolic link..." -ForegroundColor Yellow
$TargetFile = Join-Path $AudioModelsDir "MelBandRoformer_fp32.safetensors"

if (Test-Path $TargetFile) {
    Write-Host "[Skip] Symbolic link already exists: $TargetFile" -ForegroundColor Yellow
} else {
    Write-Host "[Create] mklink `"$TargetFile`" `"$MelModel`"" -ForegroundColor Gray
    
    # Use cmd to create symbolic link
    $cmd = "mklink `"$TargetFile`" `"$MelModel`""
    $result = cmd /c $cmd 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[Success] Symbolic link created" -ForegroundColor Green
    } else {
        Write-Host "[Error] Failed to create symbolic link" -ForegroundColor Red
        Write-Host "[Hint] Please run this script as Administrator" -ForegroundColor Yellow
        Write-Host ""
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host ""
Write-Host "[4/4] Verification..." -ForegroundColor Yellow
if (Test-Path $TargetFile) {
    Write-Host "[OK] MelBandRoformer model is ready" -ForegroundColor Green
    Write-Host "[Path] $TargetFile" -ForegroundColor Gray
} else {
    Write-Host "[Failed] Verification failed" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Read-Host "Press Enter to exit"
