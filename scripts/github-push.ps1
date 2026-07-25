$token = $env:GITHUB_TOKEN
$owner = "cn766"
$repo = "yichong-site"
$baseRef = "main"

$headers = @{
    Authorization = "Bearer $token"
    Accept = "application/vnd.github+json"
    "X-GitHub-Api-Version" = "2022-11-28"
}

cd 'c:\Users\cn\.trae-cn\work\6a16a760ff8af3f6424fba73\异宠网站\yichong-site'

# 1. Get current HEAD commit
cd 'c:\Users\cn\.trae-cn\work\6a16a760ff8af3f6424fba73\异宠网站\yichong-site'
$headCommit = (git rev-parse HEAD).Trim()
Write-Host "Local HEAD: $headCommit"

# 2. Get current GitHub base commit
try {
    $ref = Invoke-RestMethod -Uri "https://api.github.com/repos/$owner/$repo/git/refs/heads/$baseRef" -Headers $headers -TimeoutSec 30
    $baseCommit = $ref.object.sha
    Write-Host "GitHub base: $baseCommit"
} catch {
    Write-Error "Failed to get ref: $($_.Exception.Message)"
    exit 1
}

if ($headCommit -eq $baseCommit) {
    Write-Host "Already up to date!"
    exit 0
}

# 3. Get files changed in local commit
cd 'c:\Users\cn\.trae-cn\work\6a16a760ff8af3f6424fba73\异宠网站\yichong-site'
$files = git diff --name-only "$baseCommit" HEAD
$deleted = @()
$added = @()

foreach ($f in $files) {
    if (Test-Path $f) {
        $added += $f
    } else {
        $deleted += $f
    }
}

Write-Host "Files to add/update: $($added.Count)"
Write-Host "Files to delete: $($deleted.Count)"

# 4. Create blobs
$treeItems = @()
$count = 0

foreach ($file in $added) {
    $count++
    $content = [System.IO.File]::ReadAllBytes((Resolve-Path $file).Path)
    
    # Check if binary
    $isBinary = $false
    for ($i = 0; $i -lt [Math]::Min(8000, $content.Length); $i++) {
        if ($content[$i] -eq 0) { $isBinary = $true; break }
    }
    
    if ($isBinary) {
        $encoded = [Convert]::ToBase64String($content)
        $body = @{ content = $encoded; encoding = "base64" } | ConvertTo-Json -Compress
    } else {
        $text = [System.Text.Encoding]::UTF8.GetString($content)
        $body = @{ content = $text; encoding = "utf-8" } | ConvertTo-Json -Compress
    }
    
    try {
        $blob = Invoke-RestMethod -Uri "https://api.github.com/repos/$owner/$repo/git/blobs" -Headers $headers -Method POST -Body $body -TimeoutSec 60 -ContentType "application/json"
        $treeItems += @{
            path = $file -replace '\\', '/'
            mode = "100644"
            type = "blob"
            sha = $blob.sha
        }
        Write-Host "  [$count/$($added.Count)] Blob: $file"
    } catch {
        Write-Warning "Failed blob $file`: $($_.Exception.Message)"
    }
}

# 5. Deleted files
foreach ($file in $deleted) {
    $treeItems += @{
        path = $file -replace '\\', '/'
        mode = "100644"
        type = "blob"
        sha = $null
    }
    Write-Host "  Delete: $file"
}

Write-Host "Total tree items: $($treeItems.Count)"

# 6. Create tree
$treeBody = @{
    base_tree = $null
    tree = $treeItems
} | ConvertTo-Json -Depth 10 -Compress

try {
    $newTree = Invoke-RestMethod -Uri "https://api.github.com/repos/$owner/$repo/git/trees" -Headers $headers -Method POST -Body $treeBody -TimeoutSec 120 -ContentType "application/json"
    Write-Host "New tree: $($newTree.sha)"
} catch {
    Write-Error "Failed to create tree: $($_.Exception.Message)"
    # Try with base_tree
    Write-Host "Retrying with base_tree..."
    $treeBody = @{
        base_tree = (Invoke-RestMethod -Uri "https://api.github.com/repos/$owner/$repo/git/commits/$baseCommit" -Headers $headers -TimeoutSec 30).tree.sha
        tree = $treeItems
    } | ConvertTo-Json -Depth 10 -Compress
    $newTree = Invoke-RestMethod -Uri "https://api.github.com/repos/$owner/$repo/git/trees" -Headers $headers -Method POST -Body $treeBody -TimeoutSec 120 -ContentType "application/json"
    Write-Host "New tree (retry): $($newTree.sha)"
}

# 7. Create commit
$commitBody = @{
    message = (git log -1 --format=%B HEAD).Trim()
    tree = $newTree.sha
    parents = @($baseCommit)
} | ConvertTo-Json -Depth 5 -Compress

try {
    $newCommit = Invoke-RestMethod -Uri "https://api.github.com/repos/$owner/$repo/git/commits" -Headers $headers -Method POST -Body $commitBody -TimeoutSec 60 -ContentType "application/json"
    Write-Host "New commit: $($newCommit.sha)"
} catch {
    Write-Error "Failed to create commit: $($_.Exception.Message)"
    exit 1
}

# 8. Update ref
$refBody = @{
    sha = $newCommit.sha
    force = $false
} | ConvertTo-Json -Compress

try {
    $updated = Invoke-RestMethod -Uri "https://api.github.com/repos/$owner/$repo/git/refs/heads/$baseRef" -Headers $headers -Method PATCH -Body $refBody -TimeoutSec 30 -ContentType "application/json"
    Write-Host "SUCCESS: Pushed to $baseRef"
    Write-Host "Commit SHA: $($newCommit.sha)"
} catch {
    Write-Error "Failed to update ref: $($_.Exception.Message)"
    exit 1
}
