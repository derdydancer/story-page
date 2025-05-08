# Get all .txt files in the .\temp directory
$files = Get-ChildItem -Path .\temp -Filter *.txt
$totalFiles = $files.Count
$startTime = Get-Date
$fileCounter = 0

# Process each file
foreach ($file in $files) {
    $fileCounter++
    $fileName = $file.FullName
    $storyName = $file.BaseName

    # Start timing for this file
    $fileStartTime = Get-Date

    # Run the Python script with the file name and story name as arguments
    python .\generate_seed_temp.py "$fileName" "$storyName" | Out-Null

    # Calculate elapsed time for this file
    $fileEndTime = Get-Date
    $fileElapsedTime = $fileEndTime - $fileStartTime

    # Calculate total elapsed time
    $currentTime = Get-Date
    $totalElapsedTime = $currentTime - $startTime

    # Calculate average time per file
    $averageTimePerFile = $totalElapsedTime.TotalSeconds / $fileCounter

    # Estimate remaining time
    $remainingFiles = $totalFiles - $fileCounter
    $estimatedRemainingTime = [timespan]::FromSeconds($averageTimePerFile * $remainingFiles)

    # Display progress
    Write-Host "Processed file $fileCounter of ${totalFiles}: $storyName"
    Write-Host "Time for this file: $($fileElapsedTime.ToString('hh\:mm\:ss'))"
    Write-Host "Total elapsed time: $($totalElapsedTime.ToString('hh\:mm\:ss'))"
    Write-Host "Estimated remaining time: $($estimatedRemainingTime.ToString('hh\:mm\:ss'))"
    Write-Host "---------------------------------------------"
}

Write-Host "All files processed. Total time: $((Get-Date) - $startTime)."