Write-Host "Отключение LFS для этого файла и фиксация как обычного файла..."
git lfs untrack "EVIDENCE_REGISTRY_INDEX.json"
git add .gitattributes
git add EVIDENCE_REGISTRY_INDEX.json
git commit -m "chore: add EVIDENCE_REGISTRY_INDEX.json (68.16 MB) as regular git file under 100MB limit"

Write-Host "Отправка в удаленный репозиторий..."
git push origin udhr-audit-rebuild-2026
