# Instructions, not evidence of native Windows execution. Does not install dependencies.
param([Parameter(Mandatory=$true)][string]$DknSource,
      [Parameter(Mandatory=$true)][string]$Evidence,
      [string]$Python='python')
$ErrorActionPreference='Stop'
foreach ($Phase in @('tests','workflows','audit','assemble')) {
    & $Python tools/verify_l.py --dkn-source $DknSource --out $Evidence --phase $Phase
    if ($LASTEXITCODE -ne 0) { throw "Qualification failed in $Phase (exit $LASTEXITCODE)" }
}
