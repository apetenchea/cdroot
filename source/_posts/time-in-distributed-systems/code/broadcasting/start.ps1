param (
    [string[]]$ports
)

foreach ($port in $ports) {
    Start-Process powershell.exe -ArgumentList "-Command","& {python main.py --port $port --ports $ports}"
}