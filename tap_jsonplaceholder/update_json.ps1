
$scriptPath = "C:\Users\yosef\OneDrive\Desktop\Singer SDK\tap_jsonplaceholder"
Set-Location $scriptPath

function Write-Log {
    param($Message)
    $logMessage = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss'): $Message"
    $logMessage | Out-File -FilePath "update_log.txt" -Append
    Write-Host $logMessage
}

try {
   
    if (Test-Path output.json) {
        Remove-Item output.json
        Write-Log "Deleted existing output.json"
    }
    
 
    $result = poetry run tap-jsonplaceholder --config config.json > output.json 2>&1
    
  
    if (Test-Path output.json) {
        $fileSize = (Get-Item output.json).Length
        Write-Log "Successfully created output.json (Size: $fileSize bytes)"
    } else {
        Write-Log "ERROR: Failed to create output.json"
    }
} catch {
    Write-Log "ERROR: $($_.Exception.Message)"
}