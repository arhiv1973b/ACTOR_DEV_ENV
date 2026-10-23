param($Module, $Func, $ParamsJson, $OutFile)
$ErrorActionPreference = 'Stop'
$InformationPreference = 'SilentlyContinue'
$VerbosePreference = 'SilentlyContinue'
$WarningPreference = 'SilentlyContinue'

try {
    # Proper JSON parsing
    $argList = $ParamsJson | ConvertFrom-Json
    
    function Convert-ToHashtable($obj) {
        if ($obj -is [System.Management.Automation.PSCustomObject]) {
            $ht = @{}
            foreach ($prop in $obj.PSObject.Properties) {
                $ht[$prop.Name] = Convert-ToHashtable $prop.Value
            }
            return $ht
        } elseif ($obj -is [System.Array]) {
            $arr = @()
            foreach ($item in $obj) {
                $arr += Convert-ToHashtable $item
            }
            return $arr
        }
        return $obj
    }
    
    $hashtableParams = Convert-ToHashtable $argList
    
    # Load the module
    if (-not (Test-Path $Module)) { throw "Module not found: $Module" }
    Import-Module $Module -DisableNameChecking -Force
    
    # Execute the function
    $result = & $Func @hashtableParams
    
    # Convert result to JSON and save
    if ($null -eq $result) { $result = [PSCustomObject]@{Status="Done"} }
    $result | ConvertTo-Json -Depth 5 -Compress | Set-Content -Path $OutFile -Encoding UTF8
} catch {
    $msg = "ERROR in ${Func}: " + $_.Exception.Message
    $err = [PSCustomObject]@{ Error = $msg; Message = $_.Exception.Message; Stack = $_.ScriptStackTrace }
    $err | ConvertTo-Json -Compress | Set-Content -Path $OutFile -Encoding UTF8
    exit 1
}
