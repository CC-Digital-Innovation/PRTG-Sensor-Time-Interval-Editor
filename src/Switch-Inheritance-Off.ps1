. ".\Get-IniFile-Function.ps1"

$CONFIG = Get-IniFile .\..\config.ini

Import-Module PrtgAPI

$server = $CONFIG.PRTG_Info.server_url
$username = $CONFIG.PRTG_Info.username
$password = $CONFIG.PRTG_Info.password

Connect-PrtgServer $server (New-Credential $username $password)

$target_sensor = Get-Sensor -Id $args[0]

$target_sensor | Set-ObjectProperty InheritInterval False

$target_sensor | Refresh-Object

Disconnect-PrtgServer
