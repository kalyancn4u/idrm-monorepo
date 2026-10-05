# Wraps each page's header brand as [brand-group] = the brand link + a [ROLE] badge beside "IDRM".
# Role = the page's default/expected user (per FLOW-ANALYSIS-PLAN R8). Idempotent (skips if already applied)
# and only touches the FIRST brand (the header; the home footer brand is left alone). Pure ASCII.
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$dir  = Join-Path $root 'pages'
$roles = @{
  '01-home'='Public'; '02-register'='Public'; '03-login'='Public'; '04-forgot-password'='Public';
  '05-dashboard'='CITIZEN'; '06-create-service'='CITIZEN'; '07-service-detail'='CITIZEN';
  '08-my-services'='CITIZEN'; '09-map'='CITIZEN'; '10-notifications'='CITIZEN'; '11-profile'='CITIZEN';
  '12-provider-dashboard'='PROVIDER'; '13-available-services'='PROVIDER'; '14-active-services'='PROVIDER';
  '15-admin-dashboard'='DM_AUTHORITY'
}
$rx = [regex]'<a href="[^"]*" class="brand">.*?</a>'
$n = 0
Get-ChildItem $dir -Filter *.html | ForEach-Object {
  $role = $roles[$_.BaseName]
  if (-not $role) { return }
  $c = [IO.File]::ReadAllText($_.FullName)
  if ($c.Contains('class="brand-role"') -or $c.Contains('class="brand-group"')) { return }  # already applied
  $cls = if ($role -eq 'Public') { 'brand-role public' } else { 'brand-role' }
  $repl = '<div class="brand-group">$0<span class="' + $cls + '">' + $role + '</span></div>'
  $new = $rx.Replace($c, $repl, 1)   # first match only = the header brand
  if ($new -ne $c) { [IO.File]::WriteAllText($_.FullName, $new, (New-Object System.Text.UTF8Encoding($false))); $n++ }
}
Write-Output ("brand-role badge applied to {0} pages." -f $n)
