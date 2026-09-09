# Builds dist\AeroServer-Prism.zip  ->  friends do "Add Instance > Import from zip"
# Run AFTER build-pack.ps1 and after you've pushed the pack to GitHub.
$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
Set-Location $root

$cfg = @{}
Get-Content "$root\aero.config" | Where-Object { $_ -match "^\s*[^#].*=" } | ForEach-Object {
    $k, $v = $_ -split "=", 2; $cfg[$k.Trim()] = $v.Trim()
}
if (-not (Test-Path "$root\pack\pack.toml")) { throw "Run build-pack.ps1 first." }

# resolved NeoForge version from the pack
$nf = (Select-String -Path "$root\pack\pack.toml" -Pattern 'neoforge\s*=\s*"([^"]+)"').Matches.Groups[1].Value
if (-not $nf) { throw "Could not read neoforge version from pack\pack.toml" }
$packUrl = "https://raw.githubusercontent.com/$($cfg['GITHUB_REPO'])/$($cfg['GITHUB_BRANCH'])/pack/pack.toml"

$build = "$root\dist\_prism\Aero Server"
if (Test-Path "$root\dist\_prism") { Remove-Item "$root\dist\_prism" -Recurse -Force }
New-Item -ItemType Directory -Force -Path "$build\.minecraft" | Out-Null

@"
{
  "components": [
    { "uid": "net.minecraft", "version": "$($cfg['MC_VERSION'])", "important": true },
    { "uid": "net.neoforged", "version": "$nf" }
  ],
  "formatVersion": 1
}
"@ | Set-Content -Encoding utf8 "$build\mmc-pack.json"

@"
InstanceType=OneSix
name=Aero Server
iconKey=default
OverrideCommands=true
PreLaunchCommand="`$INST_JAVA" -jar "`$INST_MC_DIR/packwiz-installer-bootstrap.jar" "$packUrl"
OverrideMemory=true
MinMemAlloc=2048
MaxMemAlloc=4096
"@ | Set-Content -Encoding utf8 "$build\instance.cfg"

Write-Host "Downloading packwiz-installer-bootstrap.jar..."
Invoke-WebRequest -Uri "https://github.com/packwiz/packwiz-installer-bootstrap/releases/latest/download/packwiz-installer-bootstrap.jar" `
    -OutFile "$build\.minecraft\packwiz-installer-bootstrap.jar"

$zip = "$root\dist\AeroServer-Prism.zip"
if (Test-Path $zip) { Remove-Item $zip }
Compress-Archive -Path "$root\dist\_prism\Aero Server" -DestinationPath $zip
Remove-Item "$root\dist\_prism" -Recurse -Force

Write-Host ""
Write-Host "Built: $zip"
Write-Host "Send that file + PLAYER_SETUP.md to your friends."
