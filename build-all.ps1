# 聚合 书源/ 目录下所有书源 JSON 为根目录 all.json (书源订阅唯一入口)
# 由 GitHub Actions 在 push 时自动运行; 本地手动执行: powershell -File build-all.ps1
$ErrorActionPreference = 'Stop'
$dir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $dir
$srcDir = Join-Path $dir '书源'

if (-not (Test-Path $srcDir)) { Write-Host '书源/ 目录不存在'; exit 1 }

$files = Get-ChildItem -Path $srcDir -Filter '*.json' -File
Write-Host "发现书源文件: $($files.Count) 个"
$files | ForEach-Object { Write-Host "  - $($_.Name)" }
if ($files.Count -eq 0) { Write-Host '没有可聚合的文件'; exit 1 }

# 合并: 每个文件可以是单对象或数组, 统一展开; 按 bookSourceUrl 去重 (先到先得)
$all = New-Object System.Collections.Generic.List[object]
$seen = @{}
foreach ($f in $files) {
    $raw = Get-Content $f.FullName -Raw -Encoding UTF8
    $json = $raw | ConvertFrom-Json
    $items = if ($json -is [array]) { $json } else { @($json) }
    foreach ($item in $items) {
        $key = "$($item.bookSourceUrl)"
        if (-not $key -or $key -eq '') { Write-Host "  跳过无效项 (无 bookSourceUrl): $($item.bookSourceName)"; continue }
        if ($seen.ContainsKey($key)) { Write-Host "  跳过重复源: $($item.bookSourceName) ($key)"; continue }
        $seen[$key] = $true
        $all.Add($item)
    }
}
Write-Host "聚合完成: $($all.Count) 个书源"

# 校验: 每个源必须有名称与 URL
foreach ($s in $all) {
    if (-not $s.bookSourceName -or -not $s.bookSourceUrl) { throw "校验失败: 缺少 bookSourceName/bookSourceUrl" }
}

# 输出 (UTF-8 无 BOM; 单源也要是数组)
$out = $all | ConvertTo-Json -Depth 20
if ($all.Count -eq 1) { $out = "[$out]" }
[System.IO.File]::WriteAllText("$dir\all.json", $out, (New-Object System.Text.UTF8Encoding($false)))
$size = [Math]::Round((Get-Item "$dir\all.json").Length / 1KB, 1)
Write-Host "已生成 all.json ($size KB, $($all.Count) 源)"
