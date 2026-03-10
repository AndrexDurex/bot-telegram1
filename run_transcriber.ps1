$uv = "C:\Users\aldri\.local\bin\uv.exe"
$script = "d:\YOP\BioAgent\main_transcriber.py"
$log = "d:\YOP\BioAgent\transcripter_log.txt"

Write-Host "Iniciando transcripción..."
& $uv run --with requests --with yt-dlp --with python-dotenv python $script *> $log
Write-Host "Proceso finalizado (ver log: $log)"
