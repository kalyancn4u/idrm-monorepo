# Replaces UI/navigation/scope/workflow emoji with inline Lucide SVG icons (ISC-licensed) across the
# v2 page templates (pages/**/*.html) + the showcase intro. Search strings are built at RUNTIME from
# numeric Unicode code points (ConvertFromUtf32) and matched with ordinal String.Replace(), so this
# script is PURE ASCII (Windows PowerShell 5.1 reads .ps1 as ANSI; literal emoji would corrupt - R2).
#
# Intentionally NOT mapped (kept as typographic glyphs, not emoji): status dot U+25CF, flow arrows
# U+2192, matrix marks check/dash/bang, rating star U+2605 (also "4.7*" text). Emoji that cannot be an
# SVG (inside <select><option>: priority dots) are stripped to text in the source instead. The password
# show/hide toggle uses SVG via idrm-templates.js (no emoji). Re-run anytime (idempotent), then rebuild.
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$targets = @(Get-ChildItem (Join-Path $root 'pages') -Recurse -Filter *.html | ForEach-Object { $_.FullName })
$targets += (Join-Path $root '_showcase-intro.html')

# Lucide path data (https://lucide.dev, ISC). CSS class .ic supplies stroke/fill/size/color.
$paths = @{
  'menu'             = '<line x1="4" x2="20" y1="6" y2="6"/><line x1="4" x2="20" y1="12" y2="12"/><line x1="4" x2="20" y1="18" y2="18"/>'
  'life-buoy'        = '<circle cx="12" cy="12" r="10"/><path d="m4.93 4.93 4.24 4.24"/><path d="m14.83 9.17 4.24-4.24"/><path d="m14.83 14.83 4.24 4.24"/><path d="m9.17 14.83-4.24 4.24"/><circle cx="12" cy="12" r="4"/>'
  'home'             = '<path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M9 22V12h6v10"/>'
  'circle-plus'      = '<circle cx="12" cy="12" r="10"/><path d="M8 12h8"/><path d="M12 8v8"/>'
  'clipboard-list'   = '<rect width="8" height="4" x="8" y="2" rx="1" ry="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="M12 11h4"/><path d="M12 16h4"/><path d="M8 11h.01"/><path d="M8 16h.01"/>'
  'map'              = '<path d="M14.106 5.553a2 2 0 0 0 1.788 0l3.659-1.83A1 1 0 0 1 21 4.619v12.764a1 1 0 0 1-.553.894l-4.553 2.277a2 2 0 0 1-1.788 0l-4.212-2.106a2 2 0 0 0-1.788 0l-3.659 1.83A1 1 0 0 1 3 19.381V6.618a1 1 0 0 1 .553-.894l4.553-2.277a2 2 0 0 1 1.788 0z"/><path d="M15 5.764v15"/><path d="M9 3.236v15"/>'
  'map-pin'          = '<path d="M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0"/><circle cx="12" cy="10" r="3"/>'
  'bell'             = '<path d="M10.268 21a2 2 0 0 0 3.464 0"/><path d="M3.262 15.326A1 1 0 0 0 4 17h16a1 1 0 0 0 .74-1.673C19.41 13.956 18 12.499 18 8A6 6 0 0 0 6 8c0 4.499-1.411 5.956-2.738 7.326"/>'
  'user'             = '<circle cx="12" cy="8" r="5"/><path d="M20 21a8 8 0 0 0-16 0"/>'
  'lock'             = '<rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>'
  'search'           = '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>'
  'phone'            = '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>'
  'layout-dashboard' = '<rect width="7" height="9" x="3" y="3" rx="1"/><rect width="7" height="5" x="14" y="3" rx="1"/><rect width="7" height="9" x="14" y="12" rx="1"/><rect width="7" height="5" x="3" y="16" rx="1"/>'
  'inbox'            = '<path d="M22 12h-6l-2 3h-4l-2-3H2"/><path d="M5.45 5.11 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"/>'
  'truck'            = '<path d="M14 18V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v11a1 1 0 0 0 1 1h2"/><path d="M15 18H9"/><path d="M19 18h2a1 1 0 0 0 1-1v-3.65a1 1 0 0 0-.22-.624l-3.48-4.35A1 1 0 0 0 17.52 8H14"/><circle cx="17" cy="18" r="2"/><circle cx="7" cy="18" r="2"/>'
  'users'            = '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>'
  'bar-chart'        = '<path d="M3 3v18h18"/><path d="M18 17V9"/><path d="M13 17V5"/><path d="M8 17v-3"/>'
  'file-text'        = '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M16 13H8"/><path d="M16 17H8"/><path d="M10 9H8"/>'
  'building-2'       = '<path d="M6 22V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18Z"/><path d="M6 12H4a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h2"/><path d="M18 9h2a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2h-2"/><path d="M10 6h4"/><path d="M10 10h4"/><path d="M10 14h4"/><path d="M10 18h4"/>'
  'shield'           = '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/>'
  'target'           = '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>'
  'triangle-alert'   = '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4"/><path d="M12 17h.01"/>'
  'globe'            = '<circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/>'
  'eye'              = '<path d="M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0"/><circle cx="12" cy="12" r="3"/>'
  'eye-off'          = '<path d="M10.733 5.076a10.744 10.744 0 0 1 11.205 6.575 1 1 0 0 1 0 .696 10.747 10.747 0 0 1-1.444 2.49"/><path d="M14.084 14.158a3 3 0 0 1-4.242-4.242"/><path d="M17.479 17.499a10.75 10.75 0 0 1-15.417-5.151 1 1 0 0 1 0-.696 10.75 10.75 0 0 1 4.446-5.143"/><path d="m2 2 20 20"/>'
  'key'              = '<path d="m15.5 7.5 2.3 2.3a1 1 0 0 0 1.4 0l2.1-2.1a1 1 0 0 0 0-1.4L21 5"/><path d="m21 2-9.6 9.6"/><circle cx="7.5" cy="15.5" r="5.5"/>'
  'info'             = '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/>'
  'pencil'           = '<path d="M21.174 6.812a1 1 0 0 0-3.986-3.987L3.842 16.174a2 2 0 0 0-.5.83l-1.321 4.352a.5.5 0 0 0 .623.622l4.353-1.32a2 2 0 0 0 .83-.497z"/><path d="m15 5 4 4"/>'
}
function Ic($name) { '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true">' + $paths[$name] + '</svg>' }

# code point (hex int), has-variation-selector, icon-name  (no emoji literals anywhere - R2)
$map = @(
  @(0x2630,  $false, 'menu'),
  @(0x25C6,  $false, 'life-buoy'),
  @(0x1F3E0, $false, 'home'),
  @(0x1F198, $false, 'circle-plus'),
  @(0x1F4CB, $false, 'clipboard-list'),
  @(0x1F5FA, $true,  'map'),
  @(0x1F4CD, $false, 'map-pin'),
  @(0x1F514, $false, 'bell'),
  @(0x2699,  $true,  'user'),
  @(0x1F512, $false, 'lock'),
  @(0x1F50D, $false, 'search'),
  @(0x1F4DE, $false, 'phone'),
  @(0x1F4CA, $false, 'layout-dashboard'),
  @(0x1F195, $false, 'inbox'),
  @(0x1F690, $false, 'truck'),
  @(0x1F465, $false, 'users'),
  @(0x1F4C8, $false, 'bar-chart'),
  @(0x2705,  $false, 'circle-check'),
  @(0x1F9FE, $false, 'file-text'),
  @(0x1F3E5, $false, 'building-2'),
  @(0x1F6E1, $true,  'shield'),
  @(0x25CE,  $false, 'target'),
  @(0x26A0,  $true,  'triangle-alert'),
  @(0x25C9,  $false, 'globe'),
  @(0x1F441, $true,  'eye'),
  @(0x1F511, $false, 'key'),
  @(0x1F648, $false, 'eye-off'),
  @(0x2139,  $true,  'info'),
  @(0x270F,  $true,  'pencil')
)
# circle-check needs a path (used for U+2705) - add it here so Ic() can resolve it.
$paths['circle-check'] = '<circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/>'
$VS = [char]0xFE0F

$warn = 0
foreach ($f in $targets) {
  $c = [IO.File]::ReadAllText($f)
  foreach ($m in $map) {
    $base = [char]::ConvertFromUtf32([int]$m[0])
    $svg  = Ic $m[2]
    if ($m[1]) { $c = $c.Replace($base + $VS, $svg) }   # variation-selector form first
    $c = $c.Replace($base, $svg)                          # bare form
  }
  # SAFETY NET (R6/R14): an icon SVG must never land inside an HTML attribute value.
  $leak = [regex]::Matches($c, '="[^"]*<svg')
  if ($leak.Count -gt 0) {
    Write-Warning ("{0}: {1} icon(s) leaked INTO an HTML attribute. Move the emoji to a separate element." -f (Split-Path $f -Leaf), $leak.Count)
    $warn += $leak.Count
  }
  [IO.File]::WriteAllText($f, $c, (New-Object System.Text.UTF8Encoding($false)))
}
Write-Output ("Lucide icons applied to {0} files." -f $targets.Count)
if ($warn -gt 0) { Write-Output ("** ATTENTION: {0} attribute-embedded icon(s) detected - fix the source, then re-run. **" -f $warn) }
