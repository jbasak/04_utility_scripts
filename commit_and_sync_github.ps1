[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$RootFolder,

    [string]$RemoteName,

    [string]$CommitMessage = "Automated sync: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$syncScript = Join-Path $PSScriptRoot "sync_local_with_github.ps1"
if (-not (Test-Path -LiteralPath $syncScript -PathType Leaf)) {
    throw "The sync script was not found: $syncScript"
}

$arguments = @{
    RootFolder = $RootFolder
    CommitLocalChanges = $true
    CommitMessage = $CommitMessage
}

if ($RemoteName) {
    $arguments.RemoteName = $RemoteName
}

if ($WhatIfPreference) {
    $arguments.WhatIf = $true
}

& $syncScript @arguments
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
