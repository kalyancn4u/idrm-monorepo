# Assembles idrm-templates-showcase.html from the parts in templates/.
# Re-run after editing any page, the shared CSS/JS, or _showcase-intro.html.
$ErrorActionPreference = 'Stop'
$root     = Split-Path -Parent $MyInvocation.MyCommand.Path
$pagesDir = Join-Path $root 'pages'
$out      = Join-Path $root 'idrm-templates-showcase.html'

$css   = [IO.File]::ReadAllText((Join-Path $root 'assets\idrm-design-system.css'))
$js    = [IO.File]::ReadAllText((Join-Path $root 'assets\idrm-templates.js'))
$intro = [IO.File]::ReadAllText((Join-Path $root '_showcase-intro.html'))

# ---- per-page frames ----
$frames = ''
Get-ChildItem $pagesDir -Filter *.html | Sort-Object Name | ForEach-Object {
    $html = [IO.File]::ReadAllText($_.FullName)
    $inner = [regex]::Match($html, '(?s)<body[^>]*>(.*)</body>').Groups[1].Value
    # drop the external script include (JS is inlined once at the end)
    $inner = $inner -replace '(?s)\s*<script src="\.\./assets/idrm-templates\.js"></script>\s*', ''
    # make in-template page links open the matching standalone file from the showcase location
    $inner = $inner -replace 'href="(\d{2}-[^"#]+\.html)"', 'href="pages/$1"'

    $base = $_.BaseName                       # e.g. 01-home
    $num  = ($base -split '-')[0]             # e.g. 01
    $file = $_.Name                           # e.g. 01-home.html

    $frames += "`n<hr color=""skyblue"">`n"
    $frames += "<section class=""tpl-frame"" id=""tpl-$base"">`n"
    $frames += "  <div class=""tpl-label""><span class=""tpl-num"">$num</span> <span class=""tpl-name"">$file</span> <a class=""tpl-open"" href=""pages/$file"" target=""_blank"" rel=""noopener"">Open standalone &#8599;</a></div>`n"
    $frames += "  <div class=""tpl-body"">`n$inner`n  </div>`n"
    $frames += "</section>`n"
}

# ---- showcase-only CSS overrides (neutralize page-level sticky/fixed inside frames) ----
$override = @'
/* ===== showcase-only overrides ===== */
.tpl-frame { max-width: 1180px; margin: 0 auto var(--space-6); border: 1px solid var(--color-border-medium);
  border-radius: var(--radius-xl); overflow: hidden; box-shadow: var(--shadow-md); background: var(--color-bg-page); }
.tpl-label { display: flex; align-items: center; gap: var(--space-3); padding: var(--space-2) var(--space-4);
  background: #0f172a; color: #e2e8f0; font-size: var(--font-size-sm); }
.tpl-num { font-weight: 800; background: var(--color-primary-hover); color: #fff; border-radius: var(--radius-md); padding: 2px 9px; }
.tpl-name { font-family: var(--font-mono); color: #94a3b8; }
.tpl-open { margin-left: auto; color: #6ee7b7; font-weight: 600; }
.tpl-body { background: var(--color-bg-page); }
/* contain sticky/fixed page chrome so frames don't overlap in the long document */
.tpl-frame .navbar { position: static; }
.tpl-frame .app-sidebar { position: static; top: auto; }
.tpl-frame .bottom-nav { position: static; box-shadow: none; }
.tpl-frame .app-layout, .tpl-frame .container, .tpl-frame .hero-inner { padding-top: var(--space-6); padding-bottom: var(--space-6); }
[data-toc] a.active { color: var(--color-primary-strong); font-weight: 700; }
.skip-link { position: absolute; left: -999px; }
.skip-link:focus { left: var(--space-4); top: var(--space-2); background: #fff; padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-md); box-shadow: var(--shadow-md); z-index: 100; }
'@

$head = @'
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>IDRM &mdash; Page Templates &amp; Workflows | Slate + Emerald</title>
<meta name="description" content="Standalone reference: plan, page catalogue, user workflows and 15 responsive IDRM page templates in the Slate + Emerald design system.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>
'@

$footer = @'
<footer class="site-footer">
  <div class="inner text-center">
    <p class="strong">IDRM &mdash; Page Templates &amp; Workflows</p>
    <p class="text-small">Slate + Emerald &middot; WCAG AA/AAA &middot; body line-height 1.75&times; &middot; responsive (360 / 768 / 1280). Self-contained: CSS &amp; JS inlined; Inter font has a system fallback.</p>
    <p class="text-small">Standalone files in <code>templates/pages/</code> &middot; plan in <code>templates/FLOW-ANALYSIS-PLAN.md</code> &middot; &copy; 2026 IDRM.</p>
  </div>
</footer>
'@

$parts = @(
  $head,
  $css,
  $override,
  "</style>`n</head>`n<body>`n",
  '<a href="#plan" class="skip-link">Skip to content</a>',
  $intro,
  $frames,
  $footer,
  "`n<script>`n", $js, "`n</script>`n</body>`n</html>`n"
)
$final = ($parts -join "`n")

[IO.File]::WriteAllText($out, $final, (New-Object System.Text.UTF8Encoding($false)))
$kb = [math]::Round((Get-Item $out).Length / 1KB, 1)
Write-Output "Built $out ($kb KB) from $((Get-ChildItem $pagesDir -Filter *.html).Count) pages."
