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

$build = "$root\dist\_prism"
if (Test-Path $build) { Remove-Item $build -Recurse -Force }
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

$instName = if ($cfg["SERVER_NAME"]) { $cfg["SERVER_NAME"] } else { "Aero Server" }
@"
InstanceType=OneSix
name=$instName
iconKey=default
OverrideCommands=true
PreLaunchCommand="`$INST_JAVA" -jar "`$INST_MC_DIR/packwiz-installer-bootstrap.jar" "$packUrl"
OverrideMemory=true
MinMemAlloc=2048
MaxMemAlloc=4096
"@ | Set-Content -Encoding utf8 "$build\instance.cfg"

# Pre-add the server to this instance's Multiplayer list (uncompressed NBT servers.dat)
if ($cfg["SERVER_ADDRESS"]) {
    $ms = New-Object System.IO.MemoryStream
    function W([byte[]]$b) { $ms.Write($b, 0, $b.Length) }
    function WShort([int]$v) { W @([byte](($v -shr 8) -band 0xFF), [byte]($v -band 0xFF)) }
    function WInt([int]$v) { W @([byte](($v -shr 24) -band 0xFF), [byte](($v -shr 16) -band 0xFF), [byte](($v -shr 8) -band 0xFF), [byte]($v -band 0xFF)) }
    function WStr([string]$s) { $b = [Text.Encoding]::UTF8.GetBytes($s); WShort $b.Length; W $b }
    function WNamedStr([string]$n, [string]$v) { W @([byte]8); WStr $n; WStr $v }
    W @([byte]10); WShort 0                    # root TAG_Compound, name ""
      W @([byte]9); WStr "servers"             # TAG_List "servers"
      W @([byte]10); WInt 1                    #   of 1 TAG_Compound
        WNamedStr "name" $instName
        WNamedStr "ip" $cfg["SERVER_ADDRESS"]
        W @([byte]0)                           #   end element
    W @([byte]0)                               # end root
    [IO.File]::WriteAllBytes("$build\.minecraft\servers.dat", $ms.ToArray())
}

# Sane one-time video defaults for weak laptops (friends can change these freely later)
@"
version:3465
renderDistance:12
simulationDistance:8
maxFps:120
enableVsync:false
graphicsMode:0
renderClouds:"false"
entityShadows:false
ao:true
mipmapLevels:2
gamma:1.0
guiScale:0
"@ | Set-Content -Encoding ascii "$build\.minecraft\options.txt"

Write-Host "Downloading packwiz-installer-bootstrap.jar..."
Invoke-WebRequest -Uri "https://github.com/packwiz/packwiz-installer-bootstrap/releases/latest/download/packwiz-installer-bootstrap.jar" `
    -OutFile "$build\.minecraft\packwiz-installer-bootstrap.jar"

$zip = "$root\dist\AeroServer-Prism.zip"
if (Test-Path $zip) { Remove-Item $zip }
# Use bsdtar (tar.exe, bundled with Windows 10+) — it writes spec-compliant "/" separators,
# unlike Compress-Archive / .NET Framework ZipFile which write "\".
Push-Location $build
& tar.exe -a -c -f $zip -- instance.cfg mmc-pack.json .minecraft
$tarExit = $LASTEXITCODE
Pop-Location
$LASTEXITCODE = $tarExit
if ($LASTEXITCODE -ne 0) { throw "tar failed to build the zip." }
Remove-Item $build -Recurse -Force

Write-Host ""
Write-Host "Built: $zip"
Write-Host "Send that file + PLAYER_SETUP.md to your friends."
