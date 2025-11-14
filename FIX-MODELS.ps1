# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "Requesting administrator privileges..." -ForegroundColor Yellow
    Start-Process powershell.exe -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

Write-Host "================================" -ForegroundColor Cyan
Write-Host "  Fixing Model Directory Links" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

$genesisRoot = "E:\liliyuanshangmie\genesis_hand"
$fuxkcomfyModels = "E:\liliyuanshangmie\Fuxkcomfy_lris_kernel_gen2-4_speed_safe\FuxkComfy\models"

Set-Location $genesisRoot

# Create diffusion_models link
$targetDir = Join-Path $genesisRoot "genesis\models\diffusion_models"
$sourceDir = Join-Path $fuxkcomfyModels "diffusion_models"

Write-Host "[1/2] Creating diffusion_models link..." -ForegroundColor Yellow
if (Test-Path $targetDir) {
    Write-Host "  Already exists, skipping..." -ForegroundColor Gray
} else {
    try {
        New-Item -ItemType SymbolicLink -Path $targetDir -Target $sourceDir -ErrorAction Stop | Out-Null
        Write-Host "  SUCCESS: diffusion_models linked" -ForegroundColor Green
    } catch {
        Write-Host "  FAILED: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Create unet link
$targetDir2 = Join-Path $genesisRoot "genesis\models\unet"
$sourceDir2 = Join-Path $fuxkcomfyModels "diffusion_models"

Write-Host "[2/2] Creating unet link..." -ForegroundColor Yellow
if (Test-Path $targetDir2) {
    Write-Host "  Already exists, skipping..." -ForegroundColor Gray
} else {
    try {
        New-Item -ItemType SymbolicLink -Path $targetDir2 -Target $sourceDir2 -ErrorAction Stop | Out-Null
        Write-Host "  SUCCESS: unet linked" -ForegroundColor Green
    } catch {
        Write-Host "  FAILED: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "  Done!" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
