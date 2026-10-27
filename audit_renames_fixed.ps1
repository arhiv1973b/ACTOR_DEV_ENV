 = Get-Content 'C:\Users\arhiv\Downloads\Downolde\all_pdfs.txt' | Where-Object {  -like 'F:\Мой диск\*' }
 = Get-Content 'C:\Users\arhiv\Downloads\Downolde\cloud_id_manifest_full.json' -Raw | ConvertFrom-Json
 = .text.name

foreach ( in ) {
     = [System.IO.Path]::GetFileName()
    if ( -notin ) {
        Write-Output "POTENTIAL_RENAME: "
    }
}
