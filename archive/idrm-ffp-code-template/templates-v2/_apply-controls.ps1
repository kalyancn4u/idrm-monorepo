# Applies the display controls (font face / size / theme / search) to every standalone page
# under templates-v2/pages/.  Idempotent.  Pure ASCII (R2); writes UTF-8 (no BOM).
#   - expands the Google-Fonts link (Inter + DM Sans + Work Sans + Source Sans 3 + Lato + Lexend)
#   - links assets/showcase-controls.css  (after the design-system stylesheet)
#   - injects the control bar + search modal right after <body> (wrapped in SC-CONTROLS markers
#     so _build-showcase.ps1 can strip them back out of the showcase frames)
#   - links assets/showcase-controls.js   (just before </body>)
# Re-run any time; then rebuild the showcase with _build-showcase.ps1.
$ErrorActionPreference = 'Stop'
$root  = Split-Path -Parent $MyInvocation.MyCommand.Path
$bar   = [IO.File]::ReadAllText((Join-Path $root '_showcase-controls.html'))
$block = "<!-- SC-CONTROLS-START -->`n" + $bar + "`n<!-- SC-CONTROLS-END -->"

$oldFonts = '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">'
$newFonts = '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=DM+Sans:wght@400;500;600;700&family=Work+Sans:wght@400;500;600;700;800&family=Source+Sans+3:wght@400;600;700;800&family=Lato:wght@400;700;900&family=Lexend:wght@400;500;600;700&display=swap" rel="stylesheet">'
$dsLink   = '<link href="../../assets/idrm-design-system.css" rel="stylesheet">'
$cssLink  = '<link href="../../assets/showcase-controls.css" rel="stylesheet">'
$jsTag    = '<script src="../../assets/showcase-controls.js"></script>'
$enc      = New-Object System.Text.UTF8Encoding($false)
$bodyRe   = [regex]'(<body[^>]*>)'

$pages = Get-ChildItem (Join-Path $root 'pages') -Recurse -Filter *.html | Sort-Object FullName
$done = 0; $skip = 0; $warn = 0
foreach ($p in $pages) {
  $c = [IO.File]::ReadAllText($p.FullName); $orig = $c
  if ($c.Contains($oldFonts)) { $c = $c.Replace($oldFonts, $newFonts) }
  if (-not $c.Contains('showcase-controls.css')) {
    if ($c.Contains($dsLink)) { $c = $c.Replace($dsLink, $dsLink + "`n  " + $cssLink) }
    else { Write-Warning ($p.Name + ': design-system stylesheet link not found - controls CSS not linked'); $warn++ }
  }
  if (-not $c.Contains('class="sc-bar"')) {
    $c = $bodyRe.Replace($c, { param($m) $m.Value + "`n" + $block }, 1)
  }
  if (-not $c.Contains('showcase-controls.js')) {
    $c = $c.Replace('</body>', '  ' + $jsTag + "`n</body>")
  }
  if ($c -ne $orig) { [IO.File]::WriteAllText($p.FullName, $c, $enc); $done++ }
  else { $skip++ }
}
Write-Output ("Controls applied to {0} page(s); {1} already current; {2} warning(s)." -f $done, $skip, $warn)
