# Test upload-media endpoint specifically
$BaseUrl = "https://dino.ft.tc"
$ApiBase = "$BaseUrl/api/v1"
$UploadUrl = "$ApiBase/upload-media"

Write-Host "Testing Upload-Media Endpoint" -ForegroundColor Green
Write-Host "URL: $UploadUrl" -ForegroundColor Yellow
Write-Host "=" * 50

# Find test image
$TestImagePath = $null
$PossiblePaths = @("test-data\test_image.jpg", "test_image.jpg")

foreach ($Path in $PossiblePaths) {
    if (Test-Path $Path) {
        $TestImagePath = $Path
        break
    }
}

if (-not $TestImagePath) {
    Write-Host "❌ Test image not found. Checked:" -ForegroundColor Red
    foreach ($Path in $PossiblePaths) {
        Write-Host "  - $Path" -ForegroundColor Red
    }
    exit 1
}

Write-Host "✓ Found test image: $TestImagePath" -ForegroundColor Green

try {
    # Read file as bytes
    $FileBytes = [System.IO.File]::ReadAllBytes((Resolve-Path $TestImagePath))
    $Boundary = [System.Guid]::NewGuid().ToString()
    $ContentType = "multipart/form-data; boundary=$Boundary"
    
    # Create multipart form data
    $Body = @"
--$Boundary
Content-Disposition: form-data; name="file"; filename="test_image.jpg"
Content-Type: image/jpeg

"@ + [System.Text.Encoding]::GetEncoding("iso-8859-1").GetString($FileBytes) + @"

--$Boundary--
"@
    
    Write-Host "`nUploading test_image.jpg..." -ForegroundColor Yellow
    
    $Response = Invoke-RestMethod -Uri $UploadUrl -Method POST -Body $Body -ContentType $ContentType -TimeoutSec 60
    
    Write-Host "✅ SUCCESS - Upload completed!" -ForegroundColor Green
    Write-Host "Response Data:" -ForegroundColor Cyan
    $Response | ConvertTo-Json -Depth 10 | Write-Host
    
    # Test media retrieval if we got an asset_id
    if ($Response.asset_id) {
        $AssetId = $Response.asset_id
        Write-Host "`n🎯 Asset ID: $AssetId" -ForegroundColor Yellow
        
        Write-Host "`nTesting media retrieval..." -ForegroundColor Yellow
        try {
            $MediaResponse = Invoke-RestMethod -Uri "$ApiBase/media/$AssetId" -Method GET -TimeoutSec 30
            Write-Host "✅ Media retrieval successful!" -ForegroundColor Green
            Write-Host "Media Info:" -ForegroundColor Cyan
            $MediaResponse | ConvertTo-Json -Depth 10 | Write-Host
        } catch {
            Write-Host "❌ Media retrieval failed: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    
    Write-Host "`n🎉 UPLOAD TEST PASSED" -ForegroundColor Green
    
} catch {
    Write-Host "❌ UPLOAD FAILED: $($_.Exception.Message)" -ForegroundColor Red
    
    # Try to get more details from the error
    if ($_.Exception.Response) {
        $StatusCode = $_.Exception.Response.StatusCode
        Write-Host "Status Code: $StatusCode" -ForegroundColor Red
        
        try {
            $ErrorStream = $_.Exception.Response.GetResponseStream()
            $Reader = New-Object System.IO.StreamReader($ErrorStream)
            $ErrorContent = $Reader.ReadToEnd()
            Write-Host "Error Content: $ErrorContent" -ForegroundColor Red
        } catch {
            Write-Host "Could not read error details" -ForegroundColor Red
        }
    }
    
    Write-Host "`n💥 UPLOAD TEST FAILED" -ForegroundColor Red
    exit 1
}
