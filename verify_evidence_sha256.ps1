# verify_evidence_sha256.ps1
# TI-ULA Evidence Verification with HTTP Headers

$ErrorActionPreference = "SilentlyContinue"

$urls = @(
    "https://raw.githubusercontent.com/arhiv1973b/ACTOR_EVIDENCE_MOLDCELL/main/docs/Молдчелл.privind%20tehnologia%20informaţiei%20Capitalul%20social%20190001000%20Lei.pdf",
    "https://raw.githubusercontent.com/arhiv1973b/ACTOR_EVIDENCE_MOLDCELL/main/docs/Moldcell.pdf",
    "https://raw.githubusercontent.com/arhiv1973b/ACTOR_EVIDENCE_MOLDCELL/main/docs/Stimate%20Judecator%20V.%20Dodon%20si%20ai%20Moldcell.подписан.pdf",
    "https://raw.githubusercontent.com/arhiv1973b/ACTOR_EVIDENCE_MOLDCELL/main/docs/Судье%20Додон%20исполнительные%20листы.html",
    "https://raw.githubusercontent.com/arhiv1973b/ACTOR_EVIDENCE_MOLDCELL/main/docs/Citație%20MACERET%20ALEXEI%20vs.%20CONSILIUL%20PENTRU%20EGALITATE,%20SA%20Moldcell%20-%20Acţiuni%20pri.html",
    "https://raw.githubusercontent.com/arhiv1973b/ACTOR_EVIDENCE_MOLDCELL/main/docs/Macheret%20împotriva%20Consiliului%20pentru%20Egalitate%20și%20Protecție%20Discriminării%20-%20Moldcell_pdf.html",
    "https://raw.githubusercontent.com/arhiv1973b/ACTOR_EVIDENCE_MOLDCELL/main/docs/Moldcell_подписан_pdf.html",
    "https://raw.githubusercontent.com/arhiv1973b/ACTOR_EVIDENCE_MOLDCELL/main/docs/iCloudPhotos_Photos_Pregătirea_declaraţiei_pentru_instanţ.pdf_translated.txt",
    "https://raw.githubusercontent.com/arhiv1973b/ACTOR_EVIDENCE_MOLDCELL/main/docs/Донос.pdf_translated.txt"
)

$workDir = Join-Path $PWD "verification"
New-Item -ItemType Directory -Path $workDir -Force | Out-Null

$result = @()

foreach ($url in $urls) {

    Write-Host ""
    Write-Host "CHECKING: $url"

    $httpStatus = ""
    $contentLength = ""
    $contentType = ""
    $lastModified = ""
    $etag = ""
    $fileName = [System.IO.Path]::GetFileName([System.Uri]::UnescapeDataString($url))
    $sha256 = ""
    $size = ""
    $status = "ERROR"

    try {
        $request = [System.Net.HttpWebRequest]::Create($url)
        $request.Method = "HEAD"
        $response = $request.GetResponse()
        $httpStatus = [int]$response.StatusCode
        $contentLength = $response.ContentLength
        $contentType = $response.ContentType
        $lastModified = $response.LastModified.ToString("o")
        $etag = $response.Headers["ETag"]
        $response.Close()

        if ($httpStatus -eq 200) {
            $localFile = Join-Path $workDir $fileName
            Invoke-WebRequest -Uri $url -OutFile $localFile -UseBasicParsing
            $hash = Get-FileHash -Path $localFile -Algorithm SHA256
            $sha256 = $hash.Hash
            $size = (Get-Item $localFile).Length
            $status = "OK"
            Write-Host "[OK] $fileName (Status: $httpStatus)"
        } else {
            $status = "HTTP_$httpStatus"
            Write-Host "[WARN] Status $httpStatus for $fileName"
        }
    }
    catch {
        if ($_.Exception.Response) {
            $httpStatus = [int]$_.Exception.Response.StatusCode
            $status = "HTTP_$httpStatus"
        } else {
            $status = "ERROR"
        }
        Write-Warning $_.Exception.Message
    }

    $result += [PSCustomObject]@{
        STATUS         = $status
        HTTP_STATUS    = $httpStatus
        CONTENT_LENGTH = $contentLength
        CONTENT_TYPE   = $contentType
        LAST_MODIFIED  = $lastModified
        ETAG           = $etag
        FILE           = $fileName
        SIZE           = $size
        SHA256         = $sha256
        URL            = $url
    }
}

$jsonPath = Join-Path $workDir "ti_ula_manifest.json"
$csvPath  = Join-Path $workDir "ti_ula_report.csv"

$result | ConvertTo-Json -Depth 4 | Set-Content $jsonPath -Encoding UTF8
$result | Export-Csv $csvPath -NoTypeInformation -Encoding UTF8

Write-Host ""
Write-Host "========================================="
Write-Host "TI-ULA ENHANCED VERIFICATION COMPLETE"
Write-Host "========================================="
Write-Host "JSON: $jsonPath"
Write-Host "CSV : $csvPath"
Write-Host ""

$result | Format-Table STATUS, HTTP_STATUS, FILE, CONTENT_LENGTH, ETAG -AutoSize
