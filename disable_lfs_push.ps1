git config --local --unset filter.lfs.smudge -ErrorAction SilentlyContinue
git config --local --unset filter.lfs.clean -ErrorAction SilentlyContinue
git config --local --unset filter.lfs.process -ErrorAction SilentlyContinue
git config --local --unset filter.lfs.required -ErrorAction SilentlyContinue

git reset --soft HEAD~1
Remove-Item -LiteralPath ".gitattributes" -Force -ErrorAction SilentlyContinue
git add EVIDENCE_REGISTRY_INDEX.json
git commit -m "chore: add EVIDENCE_REGISTRY_INDEX.json (68.16 MB) as regular git file without LFS"
git push origin udhr-audit-rebuild-2026 --force
