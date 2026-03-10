# Cargar token desde el archivo mcp_config.json
$configPath = "C:\Users\aldri\.gemini\antigravity\mcp_config.json"
$configData = Get-Content $configPath | ConvertFrom-Json
$token = $configData.mcpServers.googledrive.env.GOOGLE_ACCESS_TOKEN

if (-not $token) {
    Write-Host "No se ha encontrado GOOGLE_ACCESS_TOKEN en mcp_config.json"
    exit 1
}

$filepath = "d:\YOP\BioAgent\5omDnw90dVo.m4a"
$title = "NotebookLM_Source_Test"
$mimeType = "audio/m4a"

# Metadatos del archivo a subir
$metadata = @{
    name = $title
    mimeType = $mimeType
}
$metadataJson = $metadata | ConvertTo-Json -Depth 5 -Compress

# Construir el multipart/related payload a mano
$boundary = "-------PshBoundary123"
$crlf = "`r`n"
$bodyLines = @(
    "--$boundary",
    "Content-Type: application/json; charset=UTF-8",
    "",
    $metadataJson,
    "--$boundary",
    "Content-Type: $mimeType",
    ""
)

$bodyHeader = [string]::Join($crlf, $bodyLines) + $crlf
$bodyHeaderBytes = [System.Text.Encoding]::UTF8.GetBytes($bodyHeader)

# Leer bytes raw del audio
$fileBytes = [System.IO.File]::ReadAllBytes($filepath)

$bodyFooter = $crlf + "--$boundary--" + $crlf
$bodyFooterBytes = [System.Text.Encoding]::UTF8.GetBytes($bodyFooter)

$bodyArray = New-Object byte[] ($bodyHeaderBytes.Length + $fileBytes.Length + $bodyFooterBytes.Length)
[System.Buffer]::BlockCopy($bodyHeaderBytes, 0, $bodyArray, 0, $bodyHeaderBytes.Length)
[System.Buffer]::BlockCopy($fileBytes, 0, $bodyArray, $bodyHeaderBytes.Length, $fileBytes.Length)
[System.Buffer]::BlockCopy($bodyFooterBytes, 0, $bodyArray, $bodyHeaderBytes.Length + $fileBytes.Length, $bodyFooterBytes.Length)

Write-Host "Enviando el archivo a Google Drive..."
$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "multipart/related; boundary=$boundary"
}

try {
    $response = Invoke-RestMethod -Uri "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart" `
                                  -Method Post `
                                  -Headers $headers `
                                  -Body $bodyArray

    # Imprimir ID del archivo
    $fileId = $response.id
    Write-Host "Archivo Subido, ID: $fileId"

    # Cambiar los permisos para que sea público (Anyone -> Reader)
    $permHeaders = @{
        "Authorization" = "Bearer $token"
        "Content-Type" = "application/json"
    }
    $permBody = @{
        "role" = "reader"
        "type" = "anyone"
    } | ConvertTo-Json
    
    Invoke-RestMethod -Uri "https://www.googleapis.com/drive/v3/files/$fileId/permissions" `
                      -Method Post `
                      -Headers $permHeaders `
                      -Body $permBody | Out-Null
    
    $publicLink = "https://drive.google.com/uc?export=download&id=$fileId"
    Write-Host "Enlace público disponible: $publicLink"
    
} catch {
    Write-Host "Error subiendo el archivo: $_"
}
