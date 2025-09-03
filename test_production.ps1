# Test DINOv3 Production Service Endpoints
$BaseUrl = "https://dino.ft.tc"
$ApiBase = "$BaseUrl/api/v1"

Write-Host "Testing DINOv3 Production Service at: $BaseUrl" -ForegroundColor Green
Write-Host "=" * 60

$Results = @()

function Test-Endpoint {
    param(
        [string]$Method,
        [string]$Url,
        [hashtable]$Body = $null,
        [string]$ContentType = "application/json"
    )
    
    try {
        $StartTime = Get-Date
        
        if ($Method -eq "GET") {
            $Response = Invoke-RestMethod -Uri $Url -Method $Method -TimeoutSec 30
        } elseif ($Body) {
            $JsonBody = $Body | ConvertTo-Json -Depth 10
            $Response = Invoke-RestMethod -Uri $Url -Method $Method -Body $JsonBody -ContentType $ContentType -TimeoutSec 30
        } else {
            $Response = Invoke-RestMethod -Uri $Url -Method $Method -TimeoutSec 30
        }
        
        $Duration = ((Get-Date) - $StartTime).TotalMilliseconds
        Write-Host "✓ PASS $Method $Url ($([math]::Round($Duration))ms)" -ForegroundColor Green
        
        return @{
            Status = "PASS"
            Method = $Method
            Url = $Url
            Duration = $Duration
            Response = $Response
        }
    }
    catch {
        $Duration = ((Get-Date) - $StartTime).TotalMilliseconds
        Write-Host "✗ FAIL $Method $Url - $($_.Exception.Message)" -ForegroundColor Red
        
        return @{
            Status = "FAIL"
            Method = $Method
            Url = $Url
            Duration = $Duration
            Error = $_.Exception.Message
        }
    }
}

# Test 1: Root endpoint
Write-Host "`n1. Testing Service Availability" -ForegroundColor Yellow
$Results += Test-Endpoint -Method "GET" -Url $BaseUrl

# Test 2: Health endpoint
Write-Host "`n2. Testing Health Endpoint" -ForegroundColor Yellow
$Results += Test-Endpoint -Method "GET" -Url "$ApiBase/health"

# Test 3: Model info
Write-Host "`n3. Testing Model Info" -ForegroundColor Yellow
$Results += Test-Endpoint -Method "GET" -Url "$ApiBase/model-info"

# Test 4: Configuration
Write-Host "`n4. Testing Configuration" -ForegroundColor Yellow
$Results += Test-Endpoint -Method "GET" -Url "$ApiBase/config"

# Test 5: Upload test image
Write-Host "`n5. Testing Media Upload" -ForegroundColor Yellow
$TestImagePath = "test-data\test_image.jpg"
$UploadedAssetId = $null

if (Test-Path $TestImagePath) {
    try {
        $FileBytes = [System.IO.File]::ReadAllBytes((Resolve-Path $TestImagePath))
        $Boundary = [System.Guid]::NewGuid().ToString()
        $ContentType = "multipart/form-data; boundary=$Boundary"
        
        $Body = @"
--$Boundary
Content-Disposition: form-data; name="file"; filename="test_image.jpg"
Content-Type: image/jpeg

"@ + [System.Text.Encoding]::GetEncoding("iso-8859-1").GetString($FileBytes) + @"

--$Boundary--
"@
        
        $Response = Invoke-RestMethod -Uri "$ApiBase/upload-media" -Method POST -Body $Body -ContentType $ContentType -TimeoutSec 60
        $UploadedAssetId = $Response.asset_id
        Write-Host "✓ PASS POST $ApiBase/upload-media - Asset ID: $UploadedAssetId" -ForegroundColor Green
        
        $Results += @{
            Status = "PASS"
            Method = "POST"
            Url = "$ApiBase/upload-media"
            Response = $Response
        }
    }
    catch {
        Write-Host "✗ FAIL POST $ApiBase/upload-media - $($_.Exception.Message)" -ForegroundColor Red
        $Results += @{
            Status = "FAIL"
            Method = "POST"
            Url = "$ApiBase/upload-media"
            Error = $_.Exception.Message
        }
    }
} else {
    Write-Host "⚠️ Test image not found at $TestImagePath" -ForegroundColor Yellow
}

# Test 6: Feature extraction (if we have an asset)
if ($UploadedAssetId) {
    Write-Host "`n6. Testing Feature Extraction" -ForegroundColor Yellow
    $Results += Test-Endpoint -Method "POST" -Url "$ApiBase/extract-features?asset_id=$UploadedAssetId"
    
    Write-Host "`n7. Testing Quality Analysis" -ForegroundColor Yellow
    $Results += Test-Endpoint -Method "POST" -Url "$ApiBase/analyze-quality" -Body @{ asset_id = $UploadedAssetId }
    
    Write-Host "`n8. Testing Media Retrieval" -ForegroundColor Yellow
    $Results += Test-Endpoint -Method "GET" -Url "$ApiBase/media/$UploadedAssetId"
}

# Test 9: Shot library
Write-Host "`n9. Testing Shot Library" -ForegroundColor Yellow
$Results += Test-Endpoint -Method "GET" -Url "$ApiBase/shot-library"

# Generate summary
Write-Host "`n" + "=" * 60 -ForegroundColor Green
Write-Host "TEST SUMMARY" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Green

$TotalTests = $Results.Count
$PassedTests = ($Results | Where-Object { $_.Status -eq "PASS" }).Count
$FailedTests = $TotalTests - $PassedTests
$SuccessRate = [math]::Round(($PassedTests / $TotalTests) * 100, 1)

Write-Host "Total Tests: $TotalTests"
Write-Host "Passed: $PassedTests ✓" -ForegroundColor Green
Write-Host "Failed: $FailedTests ✗" -ForegroundColor Red
Write-Host "Success Rate: $SuccessRate%"

# Save results to file
$ReportContent = @"
# DINOv3 Production Service Test Results

**Test Summary:**
- Total Tests: $TotalTests
- Passed: $PassedTests ✓
- Failed: $FailedTests ✗
- Success Rate: $SuccessRate%

**Test Date:** $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
**Service URL:** $BaseUrl

---

## Test Results

| Endpoint | Method | Status | Notes |
|----------|--------|--------|-------|
"@

foreach ($Result in $Results) {
    $Status = if ($Result.Status -eq "PASS") { "✓ PASS" } else { "✗ FAIL" }
    $Notes = if ($Result.Error) { $Result.Error } else { "OK" }
    $ReportContent += "`n| $($Result.Url) | $($Result.Method) | $Status | $Notes |"
}

$ReportContent += @"

---

## Service Status

"@

if ($PassedTests -gt 0) {
    $ReportContent += "✅ **Service is operational** - Basic endpoints are responding correctly.`n`n"
} else {
    $ReportContent += "❌ **Service is not operational** - No endpoints are responding correctly.`n`n"
}

if ($FailedTests -gt 0) {
    $ReportContent += "⚠️ **$FailedTests endpoints failed** - Check service logs for details.`n`n"
}

# Save report
$ReportPath = "service-test-results.md"
$ReportContent | Out-File -FilePath $ReportPath -Encoding UTF8
Write-Host "`nReport saved to: $(Resolve-Path $ReportPath)" -ForegroundColor Green
