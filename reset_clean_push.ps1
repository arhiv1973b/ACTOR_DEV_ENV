git reset --soft HEAD~1
git rm --cached .gitattributes -ErrorAction SilentlyContinue
Remove-Item -LiteralPath ".gitattributes" -Force -ErrorAction SilentlyContinue
git add EVIDENCE_REGISTRY_INDEX.json
git commit -m "chore: add EVIDENCE_REGISTRY_INDEX.json (68.16 MB) as regular git file"
git push origin udhr-audit-rebuild-2026 --force
