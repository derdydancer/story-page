echo "Calculating total duration of all MP3 files in the current directory and subdirectories..."

Get-ChildItem -Recurse -Filter *.mp3 | ForEach-Object {
    $shell = New-Object -ComObject Shell.Application
    $folder = $shell.Namespace($_.DirectoryName)
    $file = $folder.ParseName($_.Name)
    $duration = $folder.GetDetailsOf($file, 27) # Column 27 is typically the duration
    [timespan]::Parse("0:$duration")
} | Measure-Object -Property TotalSeconds -Sum | ForEach-Object {
    [timespan]::FromSeconds($_.Sum)
}

echo "Calculating total number of MP3 files in the current directory and subdirectories..."

Get-ChildItem -Recurse -Filter *.mp3 | Measure-Object | ForEach-Object {
    $_.Count
    
}

echo "Calculating total file size of all MP3 files in the current directory and subdirectories..."

Get-ChildItem -Recurse -Filter *.mp3 | Measure-Object -Property Length -Sum | ForEach-Object {
    [math]::Round($_.Sum / 1MB, 2) 
}


echo "Calculating total number of .html files in the current directory and subdirectories..."

Get-ChildItem -Recurse -Filter *.html | Measure-Object | ForEach-Object {
    $_.Count -1
}