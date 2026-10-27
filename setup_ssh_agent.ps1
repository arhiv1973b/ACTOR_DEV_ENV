# [SYSTEM DIRECTIVE: STRICT LEGAL SCOPE & AGENT BOUNDARIES]
# SUBJECT OF LAW: A©tor (A©t0r) | CASE-MACHERET-1997-2026
# ALLOWED SCOPE: ВДПЧ 1948, Jus Cogens, Erga Omnes, ст. 4 Конституции РМ.

$SshDir = Join-Path -Path $env:USERPROFILE -ChildPath ".ssh"
$ConfigFile = Join-Path -Path $SshDir -ChildPath "config"
$KeyName = "id_ed25519" 
$KeyPath = Join-Path -Path $SshDir -ChildPath $KeyName

Write-Host "=== НАСТРОЙКА SSH-АГЕНТА И КОНФИГУРАЦИИ ДЛЯ GITHUB ===" -ForegroundColor Cyan

if (!(Test-Path $SshDir)) {
    New-Item -ItemType Directory -Path $SshDir -Force | Out-Null
    Write-Host "Создана директория: $SshDir" -ForegroundColor Green
}

$AgentService = Get-Service -Name ssh-agent -ErrorAction SilentlyContinue
if ($AgentService) {
    if ($AgentService.Status -ne 'Running') {
        Set-Service -Name ssh-agent -StartupType Automatic
        Start-Service -Name ssh-agent
        Write-Host "Служба ssh-agent запущена и переведена в автоматический режим." -ForegroundColor Green
    } else {
        Write-Host "Служба ssh-agent уже активна." -ForegroundColor Gray
    }
} else {
    Write-Host "ВНИМАНИЕ: Служба ssh-agent не найдена в системе Windows." -ForegroundColor Red
    return
}

if (Test-Path $KeyPath) {
    & ssh-add $KeyPath
    Write-Host "Ключ '$KeyName' успешно добавлен в ssh-agent." -ForegroundColor Green
} else {
    Write-Host "ОШИБКА: Файл ключа не найден по пути: $KeyPath" -ForegroundColor Red
    return
}

$ConfigHostBlock = @"

# TI-ULA GitHub Configuration for A©tor
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/$KeyName
    IdentitiesOnly yes
"@

$ConfigExists = Test-Path $ConfigFile
$ExistingContent = if ($ConfigExists) { [System.IO.File]::ReadAllText($ConfigFile) } else { "" }

if ($ExistingContent -notmatch "Host github.com") {
    $Utf8NoBom = New-Object System.Text.UTF8Encoding $false
    $NewContent = $ExistingContent + "`n" + $ConfigHostBlock
    [System.IO.File]::WriteAllText($ConfigFile, $NewContent, $Utf8NoBom)
    
    icacls $ConfigFile /inheritance:r /grant "$env:USERNAME:(R,W)" | Out-Null
    
    Write-Host "Файл конфигурации ~/.ssh/config успешно создан и настроен!" -ForegroundColor Green
} else {
    Write-Host "Конфигурация для github.com уже присутствует в файле ~/.ssh/config." -ForegroundColor Yellow
}
