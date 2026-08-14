<#
  jspace citation harvester
  Pulls the backward (references) and forward (citations) neighbourhood of a seed
  paper from the Semantic Scholar Graph API and writes raw JSON into data\.

  Usage:  powershell -File harvest.ps1 [-Seed arXiv:2607.15495] [-Depth 2]

  S2's unauthenticated pool is ~1 req/sec and returns 429 aggressively, so every
  call goes through Invoke-S2 which backs off and retries.
#>
param(
  [string]$Seed  = 'arXiv:2607.15495',
  [int]   $Depth = 2,
  [string]$OutDir = "$PSScriptRoot\data"
)

$ErrorActionPreference = 'Stop'
$API = 'https://api.semanticscholar.org/graph/v1/paper'
$PAPER_FIELDS = 'paperId,externalIds,title,abstract,year,venue,authors,citationCount,referenceCount,fieldsOfStudy,publicationTypes'

if (-not (Test-Path $OutDir)) { New-Item -ItemType Directory -Force -Path $OutDir | Out-Null }

function Invoke-S2 {
  param([string]$Url, [int]$MaxTries = 6)
  $delay = 3
  for ($i = 1; $i -le $MaxTries; $i++) {
    try {
      return Invoke-RestMethod -Uri $Url -TimeoutSec 90 -Headers @{ 'User-Agent' = 'jspace-research/0.1' }
    } catch {
      $msg = $_.Exception.Message
      # 404 means S2 genuinely has no record -- do not burn retries on it.
      if ($msg -match '\(404\)') { Write-Host "    404 $Url"; return $null }
      if ($i -eq $MaxTries) { Write-Host "    GIVE UP after $MaxTries tries: $msg"; return $null }
      Write-Host "    retry $i in ${delay}s ($msg)"
      Start-Sleep -Seconds $delay
      $delay = [Math]::Min($delay * 2, 60)
    }
  }
}

function Get-Neighbours {
  # $Kind is 'references' or 'citations'; both paginate at 100.
  param([string]$Id, [string]$Kind)
  $all = @()
  $offset = 0
  do {
    $url = "$API/$Id/$Kind" + "?fields=$PAPER_FIELDS&limit=100&offset=$offset"
    $r = Invoke-S2 -Url $url
    if ($null -eq $r) { break }
    $batch = @($r.data)
    $all += $batch
    $offset += 100
    Start-Sleep -Milliseconds 1200
  } while ($batch.Count -eq 100 -and $offset -lt 1000)
  return $all
}

# ---------------------------------------------------------------- crawl
$papers = @{}   # paperId -> paper object
$edges  = New-Object System.Collections.ArrayList   # @{ from = citing; to = cited }
$seen   = @{}   # paperId -> depth already expanded at

function Add-Paper($p) {
  if ($null -eq $p -or $null -eq $p.paperId) { return }
  if (-not $papers.ContainsKey($p.paperId)) { $papers[$p.paperId] = $p }
}
function Add-Edge($from, $to) {
  if ($from -and $to) { [void]$edges.Add(@{ from = $from; to = $to }) }
}

Write-Host "== seed: $Seed"
$seedUrl = "${API}/${Seed}" + "?fields=${PAPER_FIELDS}"
$seedPaper = Invoke-S2 -Url $seedUrl
if ($null -eq $seedPaper) { throw "could not fetch seed $Seed" }
Add-Paper $seedPaper
$seedId = $seedPaper.paperId
Write-Host "   $($seedPaper.title) [$($seedPaper.year)] refs=$($seedPaper.referenceCount) cites=$($seedPaper.citationCount)"

# Forward edges: everything citing the seed (depth 1 only -- the forward cone
# explodes fast and recent citers are what matter).
Write-Host "== citations of seed"
$citers = Get-Neighbours -Id $seedId -Kind 'citations'
foreach ($c in $citers) {
  $p = $c.citingPaper
  Add-Paper $p
  Add-Edge $p.paperId $seedId
}
Write-Host "   $($citers.Count) citing papers"

# Backward edges: BFS over references to $Depth.
$frontier = @($seedId)
for ($d = 1; $d -le $Depth; $d++) {
  Write-Host "== references, depth $d ($($frontier.Count) nodes to expand)"
  $next = New-Object System.Collections.ArrayList
  $n = 0
  foreach ($id in $frontier) {
    if ($seen.ContainsKey($id)) { continue }
    $seen[$id] = $d
    $n++
    Write-Host ("   [{0}/{1}] {2}" -f $n, $frontier.Count, $papers[$id].title)
    $refs = Get-Neighbours -Id $id -Kind 'references'
    foreach ($r in $refs) {
      $p = $r.citedPaper
      if ($null -eq $p -or $null -eq $p.paperId) { continue }
      Add-Paper $p
      Add-Edge $id $p.paperId
      if ($d -lt $Depth) { [void]$next.Add($p.paperId) }
    }
  }
  $frontier = $next | Select-Object -Unique
}

# ---------------------------------------------------------------- write
$papers.Values      | ConvertTo-Json -Depth 8 | Out-File "$OutDir\papers.json" -Encoding utf8
$edges              | ConvertTo-Json -Depth 4 | Out-File "$OutDir\edges.json"  -Encoding utf8
Write-Host ""
Write-Host "wrote $($papers.Count) papers / $($edges.Count) edges to $OutDir"
