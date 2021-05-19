# PRTG-Sensor-Time-Interval-Editor

## Summary
Edits the time between sensor refreshes in a given instance of PRTG. Logs
which sensors were edited in log files.

_Note: If you have any questions or comments you can always use GitHub
discussions, or email me at farinaanthony96@gmail.com._

#### Why
There is no way to mass edit sensor intervals in PRTG, so this script does this
programmatically. Tweaking sensor time intervals can improve performance and
enables further customization of a PRTG instance.

## Requirements
- Python >= 3.9.2
- configparser >= 5.0.2
- pandas >= 1.2.2
- pytz >= 2021.1
- requests >= 2.25.1

## Usage
- Add any additional filtering logic to the API URLs to get specific
  sensors if desired.
    - _Make sure you configure filtering options accordingly. Available
      options for filtering can be found on the PRTG API:
      https://www.paessler.com/manuals/prtg/live_multiple_object_property_status#advanced_filtering_

- Add additional logic to fine tune exactly which sensors should be edited in
  PRTG, how many times a connection should be retried, how long to wait before
  a retry occurs, and custom reasons to be logged when the script ends.

- Edit the config.ini file with relevant PRTG access information and the
  timezone for the log file naming.
  
- Make sure the machine running this script has the permission to run an admin-
  privileged PowerShell terminal. This can be done by running the following
  command in an admin PowerShell terminal:
  
  `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`
  
- Make sure the PrtgAPI is installed for PowerShell.
    - This can be done by running the following command in an admin PowerShell
      terminal:
  
      `Install-Package PrtgAPI`

    - Make sure that you answer 'Y' to all prompts.\
      
    - Once PrtgAPI is installed, you must downgrade it to version 0.9.14.
      Download this version of 'PrtgAPI.zip'
      [here](https://github.com/lordmilko/PrtgAPI/releases/tag/v0.9.14).
      
    - Once the .zip file is downloaded, unzip it and place its contents into
      the following folder:
      
      `C:\Program Files\WindowsPowerShell\Modules\PrtgAPI\[version number]` or
    
      `C:\Program Files (x86)\WindowsPowerShell\Modules\PrtgAPI\[version number]`
    
        - Make sure to check where the PrtgAPI was installed first before editing
          its contents!

- Simply run the script using Python:
  
  `python PRTG-Sensor-Time-Interval-Editor.py`

## Compatibility
Should be able to run on any machine with a Python interpreter. This script
was only tested on a Windows machine running Python 3.9.5.

_Note: There would originally be no need to write a part of the script in 
       PowerShell. However, there is currently a bug in the official PRTG API
       that does not allow us to turn off interval inheritance for a PRTG
       sensor. The workaround is to reference a third-party PRTG API made for
       C# and PowerShell, hence the Switch-Inheritance-Off PowerShell script.
       In the future, this script will be rewritten so that there is no need to
       reference the third-party API so that this script will be cleaner._

## Disclaimer
The code provided in this project is an open source example and should not
be treated as an officially supported product. Use at your own risk. If you
encounter any problems, please log an
[issue](https://github.com/CC-Digital-Innovation/PRTG-Sensor-Time-Interval-Editor/issues).

## Contributing
1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request ツ

## History
-  version 1.0.0 - 2021/05/19
    - Initial release

## Credits
Anthony Farina <<farinaanthony96@gmail.com>>

Richard Bocchinfuso <<rbocchinfuso@gmail.com>> for the 
[Get-IniFile-Function.ps1](https://github.com/CC-Digital-Innovation/Get-IniFile-Function)
script.

## License
MIT License

Copyright (c) [2021] [Anthony G. Farina]

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.