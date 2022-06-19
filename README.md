# WinChromeCookieDec

**CLI to extract and decrypt cookies from Google Chrome Browser in Windows.**

It makes a local copy of Cookie sqlite database and Local State file. Generates a new sqlite file and a csv file with decrypted cookie values.

Based in this gist: [Decrypt Chrome Cookies File (Python 3) - Windows](https://gist.github.com/GramThanos/ff2c42bb961b68e7cc197d6685e06f10) from [GramThanos](https://gist.github.com/GramThanos)

Download release [here](https://github.com/privtools/WinChromeCookieDec/releases). Unzip and enjoy.

>**usage:**   
>WinChromeCookieDec.exe [-h] [-c COOKIEDB] [-d LOCALSTATE] [-o OUTPUT] [-w OVERWRITE]
>
>Decrypt Chrome Cookie DB
>
>Optional arguments:  
>- -h, --help  
*Show this help message and exit*  
>
>- -c COOKIEDB, --cookieDB COOKIEDB   
*Path to Chrome Cookie DB file*  
Default: *"C:/Users/user/Appdata/Local/Google/Chrome/User Data/Default/Network/Cookies"*  
>
>- -d LOCALSTATE, --localState LOCALSTATE  
*Path to Chrome Local State file*  
Default: *"C:/Users/user/Appdata/Local/Google/Chrome/User Data/Local State"*  
>
>- -o OUTPUT, --output OUTPUT  
*Path to output*  
Default: *"./output/"*    
>
>- -w OVERWRITE, --overwrite OVERWRITE  
*Overwrite output (true or false)*  
Default: *false*
