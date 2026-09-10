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
    $initArgs = @(
        "init", "--yes", "--name", "Aero Server", "--author", $cfg["GITHUB_REPO"],
        "--mc-version", $cfg["MC_VERSION"], "--modloader", "neoforge", "--version", "1.0.0"
    )
    if ($cfg["NEOFORGE_VERSION"] -eq "latest") { $initArgs += "--neoforge-latest" }
    else { $initArgs += @("--neoforge-version", $cfg["NEOFORGE_VERSION"]) }
    & $packwiz @initArgs
    if (-not (Test-Path "$pack\pack.toml")) { throw "packwiz init failed (see output above)." }
}

# --- add / update mods ---
$sides = @{}
Get-Content "$root\scripts\modlist.txt" | Where-Object { $_ -match "^\s*(modrinth|curseforge)\s" } | ForEach-Object {
    $parts = ($_ -split "\s+" | Where-Object { $_ })
    $src = $parts[0]; $slug = $parts[1]
    if ($parts.Count -ge 3 -and $parts[2] -match '^(client|server|both)$') { $sides[$slug] = $parts[2] }
    Write-Host "add/update: $src $slug"
    & $packwiz @($src, "add", $slug, "--yes")
    if ($LASTEXITCODE -ne 0) { throw "packwiz failed to add '$slug'." }
}
# packwiz resets `side` to "both" on every re-add — re-apply our overrides.
# CurseForge deps land as their own .pw.toml; match by a normalized name too.
foreach ($slug in $sides.Keys) {
    $candidates = @("$pack\mods\$slug.pw.toml") + (Get-ChildItem "$pack\mods\*.pw.toml" |
        Where-Object { $_.BaseName -replace '[-_]','' -eq ($slug -replace '[-_]','') } | ForEach-Object FullName)
    foreach ($f in ($candidates | Select-Object -Unique)) {
        if (Test-Path $f) {
            $txt = ((Get-Content $f) -replace '^side\s*=\s*".*"$', "side = `"$($sides[$slug])`"") -join "`n"
            [System.IO.File]::WriteAllText($f, $txt + "`n")   # LF only (packwiz + .gitattributes)
            Write-Host "  side: $(Split-Path $f -Leaf) -> $($sides[$slug])"
        }
    }
}
& $packwiz @("update", "--all", "--yes")
& $packwiz @("refresh")

Set-Location $root
Write-Host ""
Write-Host "Pack built. Next:  git add -A; git commit -m 'update pack'; git push"
