function analyze-file {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true, Position = 0, ValueFromPipeline = $true, ValueFromPipelineByPropertyName = $true)]
        [Alias("FullName", "PSPath")]
        [string]$Path,

        [Parameter(Mandatory = $false, Position = 1)]
        [string]$Prompt = "Проанализируй содержимое файла и предложи исправления",

        [Parameter(Mandatory = $false)]
        [int]$ChunkSize = 200,

        [Parameter(Mandatory = $false)]
        [string]$Model = "gemini-3.1-flash-lite"
    )

    process {
        try {
            $resolvedPath = Convert-Path $Path -ErrorAction Stop

            if (-not (Test-Path $resolvedPath -PathType Leaf)) {
                throw "Путь '$Path' не является файлом или не существует."
            }

            Write-Host "`n[Система] Чтение файла: $resolvedPath" -ForegroundColor Cyan

            # Получаем API-ключ: сначала из окружения, затем из файла защищённого DPAPI
            $key = $env:GEMINI_API_KEY
            if (-not $key) {
                $kbPath = Join-Path $HOME ".gemini_key.xml"
                if (Test-Path $kbPath) {
                    try {
                        $xmlRaw = Get-Content -Path $kbPath -Raw -ErrorAction Stop
                        try { $xml = [xml]$xmlRaw } catch { $xml = $null }
                        $enc = $null
                        if ($xml -and $xml.SelectSingleNode('//EncryptedKey')) { $enc = $xml.SelectSingleNode('//EncryptedKey').'#text' }
                        if (-not $enc) { $enc = ($xmlRaw -replace '\s','') }
                        if ($enc) {
                            try {
                                $bytes = [Convert]::FromBase64String($enc)
                                $plainBytes = [System.Security.Cryptography.ProtectedData]::Unprotect($bytes, $null, [System.Security.Cryptography.DataProtectionScope]::CurrentUser)
                                $key = [System.Text.Encoding]::UTF8.GetString($plainBytes)
                            } catch {
                                Write-Verbose ("Не удалось расшифровать ключ DPAPI: " + $_.Exception.Message)
                            }
                        }
                    } catch {
                        Write-Verbose ("Не удалось прочитать " + $kbPath + ": " + $_.Exception.Message)
                    }
                }
            }

            if (-not $key) {
                Write-Error "API-ключ не найден. Установите переменную окружения GEMINI_API_KEY или поместите зашифрованный ключ в $HOME\.gemini_key.xml"
                return
            }

            # Чанкинг по строкам для экономии токенов и предотвращения отправки больших файлов целиком
            $lines = Get-Content -Path $resolvedPath -ErrorAction Stop
            $totalLines = $lines.Count
            if ($totalLines -eq 0) { Write-Warning "Файл пуст."; return }
            $chunks = [Math]::Ceiling($totalLines / [double]$ChunkSize)

            function Invoke-GeminiPrompt {
                param(
                    [string]$Model,
                    [string]$PromptText,
                    [int]$ChunkNumber,
                    [int]$TotalChunks
                )

                $maxRetries = 5
                $attempt = 0
                $delay = 5
                while ($attempt -lt $maxRetries) {
                    try {
                        $prev = $env:GEMINI_API_KEY
                        $env:GEMINI_API_KEY = $key
                        Write-Host "`n[Система] Отправка части $ChunkNumber/$TotalChunks (попытка $($attempt+1))..." -ForegroundColor Yellow

                        # Вызов внешнего CLI. Передаём prompt как аргумент - PowerShell корректно передаёт многострочные строки.
                        $output = & python "H:\ACTOR_DEV_ENV\gemini_cli.py" -m $Model -p $PromptText 2>&1

                        # Проверка на частые ошибки фронтенда/квоты
                        $outText = $output -join "`n"
                        if ($outText -match '429' -or $outText -match 'Quota exceeded' -or $outText -match 'Rate limit') {
                            throw "RATE_LIMIT"
                        }

                        Write-Host "[Gemini ответ — часть $ChunkNumber/$TotalChunks]:`n" -ForegroundColor Cyan
                        Write-Host $outText
                        return $outText
                    }
                    catch {
                        $msg = $_.Exception.Message
                        if ($msg -eq 'RATE_LIMIT' -or $msg -match '429|Quota exceeded|Rate limit') {
                            Write-Warning "[Система] Лимит достигнут или временная ошибка: $msg. Ожидание $delay сек."
                            Start-Sleep -Seconds $delay
                            $delay = [Math]::Min($delay * 2, 120)
                            $attempt++
                            continue
                        } else {
                            Write-Error "Ошибка при вызове Gemini: $msg"
                            return $null
                        }
                    }
                    finally {
                        if ($null -ne $prev) { $env:GEMINI_API_KEY = $prev } else { Remove-Item Env:GEMINI_API_KEY -ErrorAction SilentlyContinue }
                    }
                }
                Write-Error "Не удалось получить ответ от Gemini после $maxRetries попыток."
                return $null
            }

            for ($i = 0; $i -lt $chunks; $i++) {
                $start = $i * $ChunkSize
                $end = [Math]::Min(($start + $ChunkSize - 1), $totalLines - 1)
                $chunkLines = $lines[$start..$end]
                $chunkPrompt = "$Prompt`n`n--- ФАЙЛ: $resolvedPath (часть $($i+1)/$chunks, строки $($start+1)-$($end+1)) ---`n" + ($chunkLines -join "`n")

                # Сокращение: если кусок очень большой, отбросить длинные комменты/бинарные блоки — простая эвристика
                if ($chunkPrompt.Length -gt 20000) { $chunkPrompt = $chunkPrompt.Substring(0,20000) + "`n... (усечено: длина превышала 20k символов)" }

                $res = Invoke-GeminiPrompt -Model $Model -PromptText $chunkPrompt -ChunkNumber ($i+1) -TotalChunks $chunks
                if ($null -eq $res) { Write-Warning "Прерывание обработки из-за ошибки в части $($i+1)."; break }

                # Небольшая пауза между частями, чтобы уменьшить риск троттлинга
                Start-Sleep -Milliseconds 500
            }

            Write-Host "`n[Система] Обработка файла завершена." -ForegroundColor Green
        }
        catch {
            $errorMessage = $_.Exception.Message
            Write-Error "Ошибка при обработке файла: $errorMessage"
        }
    }
}
