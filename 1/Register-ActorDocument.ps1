function Register-ActorDocument {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true, Position = 0)]
        [ValidateScript({ Test-Path $_ -PathType Leaf })]
        [string]$FilePath
    )

    # 1. Принудительная UTF-8 среда (исключаем влияние CP866 / OEM)
    [Console]::InputEncoding  = [System.Text.Encoding]::UTF8
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    $OutputEncoding           = [System.Text.Encoding]::UTF8

    # 2. Правовой токен декларации
    $signatureKey = "# [⚖ A©tor Declaration]"

    # 3. Криптография
    $fullPath   = (Resolve-Path -LiteralPath $FilePath).Path
    $fileName   = [System.IO.Path]::GetFileName($fullPath)
    $fileBytes  = [System.IO.File]::ReadAllBytes($fullPath)
    $sha256     = [System.Security.Cryptography.SHA256]::Create()
    $hashBytes  = $sha256.ComputeHash($fileBytes)
    $hashHex    = [System.BitConverter]::ToString($hashBytes).Replace("-", "").ToLowerInvariant()

    # 4. Манифест
    $manifest = [ordered]@{
        filename    = $fileName
        timestamp   = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
        sha256      = $hashHex
        author      = "A©t0r"
        signature   = $signatureKey
        source_path = $fullPath
    }

    # 5. Чистый JSON-вывод (без лишнего текста)
    $manifest | ConvertTo-Json -Compress:$false -Depth 5
}
