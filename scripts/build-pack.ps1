# Builds/updates the packwiz modpack under ./pack from scripts/modlist.txt
# Run on Windows:  powershell -ExecutionPolicy Bypass -File scripts\build-pack.ps1
$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
Set-Location $root

# --- read aero.config ---
$cfg = @{}
Get-Content "$root\aero.config" | Where-Object { $_ -match "^\s*[^#].*=" } | ForEach-Object {
    $k, $v = $_ -split "=", 2
    $cfg[$k.Trim()] = $v.Trim()
}
if ($cfg["GITHUB_REPO"] -like "REPLACE_ME*") { throw "Edit aero.config: set GITHUB_REPO first." }

# --- get packwiz ---
$bin = "$root\bin"
New-Item -ItemType Directory -Force -Path $bin | Out-Null
$packwiz = "$bin\packwiz.exe"
if (-not (Test-Path $packwiz)) {
    Write-Host "Downloading packwiz..."
    $url = "https://nightly.link/packwiz/packwiz/workflows/go/main/Windows%2064-bit.zip"
    Invoke-WebRequest -Uri $url -OutFile "$bin\packwiz.zip"
    Expand-Archive "$bin\packwiz.zip" -DestinationPath $bin -Force
    Remove-Item "$bin\packwiz.zip"
}

# --- init pack if needed ---
$pack = "$root\pack"
New-Item -ItemType Directory -Force -Path $pack | Out-Null
Set-Location $pack
if (-not (Test-Path "$pack\pack.toml")) {
    & $packwiz init --name "Aero Server" --author "$($cfg['GITHUB_REPO'])" `
        --mc-version $cfg["MC_VERSION"] --modloader neoforge `
        --neoforge-version $cfg["NEOFORGE_VERSION"] --version 1.0.0 -y
}

# --- add / update mods ---
Get-Content "$root\scripts\modlist.txt" | Where-Object { $_ -match "^\s*modrinth\s" } | ForEach-Object {
    $slug = ($_ -split "\s+")[1]
    Write-Host "add/update: $slug"
    & $packwiz modrinth add $slug -y
}
& $packwiz update --all -y
& $packwiz refresh

Set-Location $root
Write-Host ""
Write-Host "Pack built. Next:  git add -A; git commit -m 'update pack'; git push"
