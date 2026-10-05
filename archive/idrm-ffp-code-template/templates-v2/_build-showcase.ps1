# Assembles idrm-rbac-showcase.html from the parts in templates-v2/.
# Mirror of templates/_build-showcase.ps1, adapted for the role-organised subfolders.
# Pure ASCII per R2 (non-ASCII emitted as HTML entities); output is UTF-8 with no BOM.
# Re-run after editing any page, the shared CSS/JS, or _showcase-intro.html.
$ErrorActionPreference = 'Stop'
$root  = Split-Path -Parent $MyInvocation.MyCommand.Path
$out   = Join-Path $root 'idrm-rbac-showcase.html'

$css   = [IO.File]::ReadAllText((Join-Path $root 'assets\idrm-design-system.css'))
$js    = [IO.File]::ReadAllText((Join-Path $root 'assets\idrm-templates.js'))
$intro = [IO.File]::ReadAllText((Join-Path $root '_showcase-intro.html'))
$ctlcss  = [IO.File]::ReadAllText((Join-Path $root 'assets\showcase-controls.css'))
$ctlhtml = [IO.File]::ReadAllText((Join-Path $root '_showcase-controls.html'))
$ctljs   = [IO.File]::ReadAllText((Join-Path $root 'assets\showcase-controls.js'))

# Ordered manifest: relative path under pages/, the render tier code, and a short label.
$manifest = @(
  @{ p = 'shared/home.html';                          tier = 'B'; label = 'Public landing' },
  @{ p = 'shared/login.html';                         tier = 'B'; label = 'Sign in' },
  @{ p = 'shared/register.html';                      tier = 'B'; label = 'Create account' },
  @{ p = 'map/public.html';                           tier = 'B'; label = 'Public map (view-only)' },
  @{ p = 'role-dashboard/citizen.html';               tier = 'F'; label = 'Dashboard - CITIZEN' },
  @{ p = 'role-dashboard/volunteer.html';             tier = 'F'; label = 'Dashboard - VOLUNTEER' },
  @{ p = 'role-dashboard/organizer.html';             tier = 'F'; label = 'Dashboard - ORGANIZER' },
  @{ p = 'role-dashboard/provider.html';              tier = 'F'; label = 'Dashboard - PROVIDER' },
  @{ p = 'role-dashboard/manager.html';               tier = 'F'; label = 'Dashboard - MANAGER' },
  @{ p = 'role-dashboard/event-manager.html';         tier = 'F'; label = 'Dashboard - EVENT_MANAGER' },
  @{ p = 'role-dashboard/dm-authority.html';          tier = 'F'; label = 'Dashboard - DM_AUTHORITY' },
  @{ p = 'role-dashboard/auditor.html';               tier = 'F'; label = 'Dashboard - AUDITOR (read-only)' },
  @{ p = 'role-dashboard/admin.html';                 tier = 'F'; label = 'Dashboard - ADMIN' },
  @{ p = 'role-dashboard/executive-reserved.html';    tier = 'F'; label = 'Dashboard - EXECUTIVE (Post-MVP)' },
  @{ p = 'requests-list/provider-type.html';          tier = 'F'; label = 'Requests list - Provider (Type+Area)' },
  @{ p = 'requests-list/authority-jurisdiction.html'; tier = 'F'; label = 'Requests list - Authority (Jurisdiction)' },
  @{ p = 'service-detail/requestor.html';             tier = 'F'; label = 'Service detail - Requestor' },
  @{ p = 'service-detail/provider.html';              tier = 'F'; label = 'Service detail - Provider' },
  @{ p = 'service-detail/dm-authority.html';          tier = 'F'; label = 'Service detail - Authority' },
  @{ p = 'service-detail/auditor.html';               tier = 'F'; label = 'Service detail - Auditor (read-only)' },
  @{ p = 'map/dm-authority-zone.html';                tier = 'H'; label = 'Declare event + draw zone' },
  @{ p = 'admin-console/admin-system.html';           tier = 'F'; label = 'Admin system console' },
  @{ p = 'shared/profile.html';                       tier = 'F'; label = 'Profile and settings' },
  @{ p = 'shared/notifications.html';                 tier = 'F'; label = 'Notifications' }
)

$tierName = @{ B = 'Bun edge'; F = 'FastAPI'; H = 'Hybrid' }

$frames = ''
$n = 0
foreach ($m in $manifest) {
  $n++
  $rel  = $m.p
  $cat  = ($rel -split '/')[0]
  $full = Join-Path $root ('pages\' + ($rel -replace '/', '\'))
  $html = [IO.File]::ReadAllText($full)
  $inner = [regex]::Match($html, '(?s)<body[^>]*>(.*)</body>').Groups[1].Value
  # drop the external script include (JS is inlined once at the end)
  $inner = $inner -replace '(?s)\s*<script src="\.\./\.\./assets/idrm-templates\.js"></script>\s*', ''
  # drop the per-page display controls (bar + modal + script) — the showcase injects its own at the top
  $inner = $inner -replace '(?s)<!-- SC-CONTROLS-START -->.*?<!-- SC-CONTROLS-END -->\s*', ''
  $inner = $inner -replace '(?s)\s*<script src="\.\./\.\./assets/showcase-controls\.js"></script>\s*', ''
  # rewrite cross-folder links ("../cat/file.html" -> "pages/cat/file.html")
  $inner = $inner -replace 'href="\.\./', 'href="pages/'
  # rewrite same-folder links ("file.html" -> "pages/<cat>/file.html")
  $inner = [regex]::Replace($inner, 'href="([a-z0-9\-]+\.html)"', ('href="pages/' + $cat + '/$1"'))

  $id   = 'tpl-' + ($rel -replace '\.html$', '' -replace '/', '-')
  $num  = '{0:D2}' -f $n

  $frames += "`n<hr color=""skyblue"">`n"
  $frames += "<section class=""tpl-frame"" id=""$id"">`n"
  $frames += "  <div class=""tpl-label""><span class=""tpl-num"">$num</span> <span class=""render-tier tier-$($m.tier)""><span class=""dotc""></span>$($tierName[$m.tier])</span> <span class=""tpl-name"">$($m.label) &middot; pages/$rel</span> <a class=""tpl-open"" href=""pages/$rel"" target=""_blank"" rel=""noopener"">Open standalone &#8599;</a></div>`n"
  $frames += "  <div class=""tpl-body"">`n$inner`n  </div>`n"
  $frames += "</section>`n"
}

$override = @'
/* ===== showcase-only overrides ===== */
.tpl-frame { max-width: 1180px; margin: 0 auto var(--space-6); border: 1px solid var(--color-border-medium);
  border-radius: var(--radius-xl); overflow: hidden; box-shadow: var(--shadow-md); background: var(--color-bg-page); }
.tpl-label { display: flex; align-items: center; gap: var(--space-3); padding: var(--space-2) var(--space-4);
  background: #0f172a; color: #e2e8f0; font-size: var(--font-size-sm); flex-wrap: wrap; }
.tpl-num { font-weight: 800; background: var(--color-primary-hover); color: #fff; border-radius: var(--radius-md); padding: 2px 9px; }
.tpl-name { font-family: var(--font-mono); color: #94a3b8; }
.tpl-open { margin-left: auto; color: #6ee7b7; font-weight: 600; }
.tpl-body { background: var(--color-bg-page); }
/* contain sticky/fixed page chrome so frames don't overlap in the long document */
.tpl-frame .navbar { position: static; }
.tpl-frame .app-sidebar { position: static; top: auto; }
.tpl-frame .bottom-nav { position: static; box-shadow: none; }
.tpl-frame .app-layout, .tpl-frame .container, .tpl-frame .hero-inner { padding-top: var(--space-6); padding-bottom: var(--space-6); }
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
<title>IDRM v2 &mdash; RBAC Page Templates &amp; FastAPI/Bun Render Split</title>
<meta name="description" content="Role-by-role IDRM page templates (Slate + Emerald), the FS 3.3 permission matrix, and the FastAPI-vs-Bun rendering strategy. 24 responsive templates in one standalone file.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=DM+Sans:wght@400;500;600;700&family=Work+Sans:wght@400;500;600;700;800&family=Source+Sans+3:wght@400;600;700;800&family=Lato:wght@400;700;900&family=Lexend:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>
'@

$footer = @'
<footer class="site-footer">
  <div class="inner">
    <div class="footer-grid">
      <div>
        <p class="strong" style="font-size:var(--font-size-base);">IDRM &mdash; Integrated Disaster Response Management</p>
        <p class="text-small" style="margin-top:var(--space-2);">v2 templates &middot; Slate + Emerald &middot; RBAC-driven &middot; Hyderabad + Vijayawada pilot.</p>
        <p class="text-small">Government-backed, map-driven relief coordination &mdash; connecting citizens in crisis with NGOs, hospitals, volunteers and authorities.</p>
      </div>
      <div>
        <h5>Emergency helplines</h5>
        <ul>
          <li><a href="tel:108"><strong>108</strong></a> &mdash; Ambulance</li>
          <li><a href="tel:112"><strong>112</strong></a> &mdash; All-emergency</li>
          <li><a href="tel:1070"><strong>1070</strong></a> &mdash; Disaster cell</li>
        </ul>
      </div>
      <div>
        <h5>Reference</h5>
        <ul>
          <li>24 templates &middot; role &times; capability</li>
          <li>WCAG AA/AAA &middot; line-height 1.75&times;</li>
          <li>Pages: <code>templates-v2/pages/</code></li>
          <li>Plan: <code>FLOW-ANALYSIS-PLAN.md</code> &middot; &copy; 2026 IDRM</li>
        </ul>
      </div>
    </div>
  </div>
</footer>
'@

$parts = @(
  $head,
  $css,
  $override,
  $ctlcss,
  "</style>`n</head>`n<body>`n",
  '<a href="#plan" class="skip-link">Skip to content</a>',
  $ctlhtml,
  $intro,
  $frames,
  $footer,
  "`n<script>`n", $js, "`n</script>`n",
  "<script>`n", $ctljs, "`n</script>`n</body>`n</html>`n"
)
$final = ($parts -join "`n")

[IO.File]::WriteAllText($out, $final, (New-Object System.Text.UTF8Encoding($false)))
$kb = [math]::Round((Get-Item $out).Length / 1KB, 1)
Write-Output "Built $out ($kb KB) from $($manifest.Count) templates."
