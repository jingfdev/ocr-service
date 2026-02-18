# OCR Service Test Script
# This script helps you test the OCR service with real health report files

param(
    [Parameter(Mandatory=$true)]
    [string]$FilePath,

    [Parameter(Mandatory=$false)]
    [ValidateSet("en", "khm", "both")]
    [string]$Language = "both"
)

# Check if file exists
if (-not (Test-Path $FilePath)) {
    Write-Host "Error: File not found at path: $FilePath" -ForegroundColor Red
    exit 1
}

# Get the file extension and MIME type
$extension = [System.IO.Path]::GetExtension($FilePath).ToLower()
$mimeType = switch ($extension) {
    ".png" { "image/png" }
    ".jpg" { "image/jpeg" }
    ".jpeg" { "image/jpeg" }
    ".pdf" { "application/pdf" }
    default {
        Write-Host "Error: Unsupported file type. Supported types: .png, .jpg, .jpeg, .pdf" -ForegroundColor Red
        exit 1
    }
}

Write-Host "`n=== OCR Service Test ===" -ForegroundColor Cyan
Write-Host "File: $FilePath" -ForegroundColor Yellow
Write-Host "Type: $mimeType" -ForegroundColor Yellow
Write-Host "Language: $Language" -ForegroundColor Yellow
Write-Host "`nSending request to OCR service..." -ForegroundColor Green

# Create the multipart form data
$uri = "http://localhost:8000/api/v1/ocr/extract"

try {
    # Use Invoke-WebRequest with multipart form data
    $response = Invoke-WebRequest -Uri $uri -Method Post -Form @{
        file = Get-Item -Path $FilePath
        language = $Language
    } -UseBasicParsing

    Write-Host "`n=== Response ===" -ForegroundColor Cyan
    Write-Host "Status Code: $($response.StatusCode)" -ForegroundColor Green

    # Parse and pretty print JSON response
    $jsonResponse = $response.Content | ConvertFrom-Json

    Write-Host "`nSuccess: $($jsonResponse.success)" -ForegroundColor $(if ($jsonResponse.success) { "Green" } else { "Red" })

    if ($jsonResponse.success) {
        Write-Host "Confidence: $($jsonResponse.confidence)" -ForegroundColor Cyan
        Write-Host "Processing Time: $($jsonResponse.processing_time_ms) ms" -ForegroundColor Cyan
        Write-Host "`nExtracted Text:" -ForegroundColor Yellow
        Write-Host "----------------------------------------" -ForegroundColor Gray
        Write-Host $jsonResponse.raw_text
        Write-Host "----------------------------------------" -ForegroundColor Gray

        # Save the result to a file
        $outputFile = "ocr_result_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"
        $jsonResponse.raw_text | Out-File -FilePath $outputFile -Encoding UTF8
        Write-Host "`nResult saved to: $outputFile" -ForegroundColor Green
    } else {
        Write-Host "Error Message: $($jsonResponse.message)" -ForegroundColor Red
    }

    # Save full JSON response
    $jsonFile = "ocr_response_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
    $response.Content | Out-File -FilePath $jsonFile -Encoding UTF8
    Write-Host "Full JSON response saved to: $jsonFile" -ForegroundColor Green

} catch {
    Write-Host "`nError occurred:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red

    if ($_.Exception.Response) {
        $statusCode = $_.Exception.Response.StatusCode.value__
        Write-Host "Status Code: $statusCode" -ForegroundColor Red

        # Try to read error response body
        $stream = $_.Exception.Response.GetResponseStream()
        $reader = New-Object System.IO.StreamReader($stream)
        $errorBody = $reader.ReadToEnd()
        Write-Host "Response Body: $errorBody" -ForegroundColor Red
    }
}

Write-Host "`n=== Test Complete ===" -ForegroundColor Cyan

