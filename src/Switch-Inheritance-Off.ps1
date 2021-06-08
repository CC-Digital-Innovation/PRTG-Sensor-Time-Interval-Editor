. ".\Get-IniFile-Function.ps1"

$CONFIG = Get-IniFile .\..\configs\PRTG-Sensor-Time-Interval-Editor-config.ini

Import-Module PrtgAPI

$server = $CONFIG.PRTGInfo.server_url
$username = $CONFIG.PRTGInfo.username
$password = $CONFIG.PRTGInfo.password

Connect-PrtgServer $server (New-Credential $username $password)

$target_sensor = Get-Sensor -Id $args[0]

$target_sensor | Set-ObjectProperty InheritInterval False

$target_sensor | Refresh-Object

Disconnect-PrtgServer
