[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$RootFolder,

    [string]$RemoteName,

    [switch]$CommitLocalChanges,

    [switch]$StashLocalChanges,

    [string]$CommitMessage = "Automated sync: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Invoke-Git {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Repository,

        [Parameter(Mandatory = $true)]
        [string[]]$Arguments
    )

    $output = & git -C $Repository @Arguments 2>&1
    if ($LASTEXITCODE -ne 0) {
        $message = ($output | Out-String).Trim()
        throw "git $($Arguments -join ' ') failed: $message"
    }

    return $output
}

function Get-GitRepositories {
    param([Parameter(Mandatory = $true)][string]$Path)

    $repositories = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)

    if (Test-Path (Join-Path $Path ".git")) {
        [void]$repositories.Add((Resolve-Path $Path).Path)
    }

    Get-ChildItem -Path $Path -Directory -Force -Recurse -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -eq ".git" } |
        ForEach-Object { [void]$repositories.Add($_.Parent.FullName) }

    return $repositories | Sort-Object
}

function Get-GitHubRemote {
    param(
        [Parameter(Mandatory = $true)][string]$Repository,
        [string]$RequestedName
    )

    $remotes = @(Invoke-Git -Repository $Repository -Arguments @("remote")) |
        ForEach-Object { $_.ToString().Trim() } |
        Where-Object { $_ }

    if ($RequestedName) {
        if ($remotes -contains $RequestedName) {
            return $RequestedName
        }

        throw "Remote '$RequestedName' was not found. Available remotes: $($remotes -join ', ')"
    }

    if ($remotes -contains "github") {
        return "github"
    }

    foreach ($remote in $remotes) {
        $url = (Invoke-Git -Repository $Repository -Arguments @("remote", "get-url", $remote)).ToString().Trim()
        if ($url -match "github\.com") {
            return $remote
        }
    }

    throw "No GitHub remote was found. Add one with: git remote add github <GitHub URL>"
}

function Test-RemoteBranch {
    param(
        [Parameter(Mandatory = $true)][string]$Repository,
        [Parameter(Mandatory = $true)][string]$Remote,
        [Parameter(Mandatory = $true)][string]$Branch
    )

    $result = & git -C $Repository ls-remote --exit-code --heads $Remote "refs/heads/$Branch" 2>$null
    return $LASTEXITCODE -eq 0 -and $result
}

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw "Git was not found on PATH. Install Git for Windows and try again."
}

$resolvedRoot = (Resolve-Path -Path $RootFolder -ErrorAction Stop).Path
$repositories = @(Get-GitRepositories -Path $resolvedRoot)

if ($repositories.Count -eq 0) {
    Write-Warning "No Git repositories were found under '$resolvedRoot'."
    return
}

$processed = 0
$succeeded = 0
$skipped = 0
$failed = 0

foreach ($repository in $repositories) {
    $processed++
    Write-Host "`n[$processed/$($repositories.Count)] $repository" -ForegroundColor Cyan

    try {
        $remote = Get-GitHubRemote -Repository $repository -RequestedName $RemoteName
        $branch = (Invoke-Git -Repository $repository -Arguments @("symbolic-ref", "--quiet", "--short", "HEAD")).ToString().Trim()

        if (-not $branch) {
            Write-Warning "Skipped: HEAD is detached."
            $skipped++
            continue
        }

        $status = @(Invoke-Git -Repository $repository -Arguments @("status", "--porcelain"))
        if ($status.Count -gt 0) {
            if (-not $CommitLocalChanges) {
                if (-not $StashLocalChanges) {
                    Write-Warning "Skipped: local changes exist. Re-run with -CommitLocalChanges to include them, or -StashLocalChanges to omit them temporarily."
                    $skipped++
                    continue
                }

                if ($PSCmdlet.ShouldProcess($repository, "Stash local changes temporarily")) {
                    Invoke-Git -Repository $repository -Arguments @("stash", "push", "--include-untracked", "-m", "Temporary sync stash") | Out-Null
                    try {
                        if ($PSCmdlet.ShouldProcess($repository, "Sync while local changes are stashed")) {
                            Invoke-Git -Repository $repository -Arguments @("fetch", $remote, "--prune") | Out-Null

                            if (Test-RemoteBranch -Repository $repository -Remote $remote -Branch $branch) {
                                Invoke-Git -Repository $repository -Arguments @("pull", "--rebase", $remote, $branch) | Out-Null
                            }

                            $pushArguments = if (Test-RemoteBranch -Repository $repository -Remote $remote -Branch $branch) {
                                @("push", $remote, $branch)
                            } else {
                                @("push", "--set-upstream", $remote, $branch)
                            }
                            Invoke-Git -Repository $repository -Arguments $pushArguments | Out-Null
                        }
                    }
                    finally {
                        Invoke-Git -Repository $repository -Arguments @("stash", "pop") | Out-Null
                    }
                }

                Write-Host "Synced branch '$branch' while preserving local changes." -ForegroundColor Green
                $succeeded++
                continue
            }

            if ($PSCmdlet.ShouldProcess($repository, "Commit local changes on '$branch'")) {
                Invoke-Git -Repository $repository -Arguments @("add", "--all") | Out-Null
                Invoke-Git -Repository $repository -Arguments @("commit", "-m", $CommitMessage) | Out-Null
            }
        }

        if ($PSCmdlet.ShouldProcess($repository, "Fetch '$remote'")) {
            Invoke-Git -Repository $repository -Arguments @("fetch", $remote, "--prune") | Out-Null
        }

        if (Test-RemoteBranch -Repository $repository -Remote $remote -Branch $branch) {
            if ($PSCmdlet.ShouldProcess($repository, "Rebase '$branch' onto '$remote/$branch'")) {
                Invoke-Git -Repository $repository -Arguments @("pull", "--rebase", $remote, $branch) | Out-Null
            }
        }

        $pushArguments = if (Test-RemoteBranch -Repository $repository -Remote $remote -Branch $branch) {
            @("push", $remote, $branch)
        } else {
            @("push", "--set-upstream", $remote, $branch)
        }

        if ($PSCmdlet.ShouldProcess($repository, "Push '$branch' to '$remote'")) {
            Invoke-Git -Repository $repository -Arguments $pushArguments | Out-Null
        }

        Write-Host "Synced branch '$branch' with remote '$remote'." -ForegroundColor Green
        $succeeded++
    }
    catch {
        Write-Warning "Failed: $($_.Exception.Message)"
        $failed++
    }
}

Write-Host "`nCompleted. Processed: $processed; synced: $succeeded; skipped: $skipped; failed: $failed." -ForegroundColor White
if ($failed -gt 0) {
    exit 1
}