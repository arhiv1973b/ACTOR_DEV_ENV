# A©tor Contour Automated Backup Script
# Created for CASE-MACHERET-1997-2026 Forensic Synchronization

$LogPath = "H:\ACTOR_DEV_ENV\.native\backup_execution.log"
$Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

"[$Timestamp] Starting Actor Contour Backup..." | Out-File -FilePath $LogPath -Append -Encoding UTF8

try {
    Set-Location "H:\ACTOR_DEV_ENV"
    
    # Run git pull/push synchronization for active forensic branch
    git add .
    git commit -m "auto(backup): scheduled contour backup at $Timestamp" --allow-empty
    git push origin udhr-audit-rebuild-2026
    
    "[$Timestamp] Backup and git synchronization completed successfully." | Out-File -FilePath $LogPath -Append -Encoding UTF8
} catch {
    "[$Timestamp] ERROR during backup: $_" | Out-File -FilePath $LogPath -Append -Encoding UTF8
}
