@echo off
chcp 65001 > nul
echo ================================================================================
echo КРИПТОГРАФИЧЕСКИЙ АУДИТ ТОПОЛОГИИ (ERGA OMNES)
echo ================================================================================
.venv_test\Scripts\python -c "import hashlib, os; [print(f'[-] ОТСУТСТВУЕТ: {f[1]}') if not os.path.exists(p := f[1].lstrip('*').strip() if os.path.isabs(f[1].lstrip('*').strip()) else os.path.join(r'H:\ACTOR_DEV_ENV', f[1].lstrip('*').strip())) else print(f'[+] ZERO-COLLISION: {f[1]}') if hashlib.sha256(open(p,'rb').read()).hexdigest() == f[0].lower() else print(f'[!] КОМПРОМЕТАЦИЯ: {f[1]}') for l in open(r'H:\ACTOR_DEV_ENV\05_CRYPTO_MANIFESTS\CHECKSUMS_SHA256.txt', 'r', encoding='utf-8') if (f := l.strip().split()) and len(f)>=2 and not l.startswith('#')]"
echo ================================================================================
pause
