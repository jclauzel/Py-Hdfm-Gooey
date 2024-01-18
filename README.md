Py-Hdfm-Gooey by Julien Clauzel based on HDFM-GOOEY - by em00k & based on NextSync by Jari Komppa

Requirements
------------

    - Python 3.7+
    - pyside6
    - CSpect emulator by Mike Dailly installed in local directory please download from http://www.cspect.org
        feel free to support his development efforts & patreon https://www.patreon.com/mikedailly
        - Make sure Spectrum Next roms installed are installed in local directory (they should be provided in the CSpect zip package by default). 
            These two files namely: enNextZX.rom and enNxtMMC.rom -MUST- be placed in the root folder of your #CSpect.
    - You will need Spectrum Next images files that you can download from https://zxspectrumnext.online/cspect/  such as http://www.zxspectrumnext.online/cspect/cspect-next-2gb.zip
    - Download & install hdfmonkey by Matt Westcott https://github.com/gasman/hdfmonkey , on Windows either compile the source manually or download a pre-compiled version at: 
        https://uto.speccy.org/downloads/hdfmonkey_windows.zip
    - On Mac/Linux you will need to install mono-complete

* Additional help pages:
    - https://wiki.specnext.dev/Development_Tools:Linux_setup
       
* First install pyside6 this is required for the UI to render the different controls being used:
    python -m pip install pyside6

* Copy Cspect (with the Spectrum Next roms) and hdfmonkey in the same directory (see above). 

CSpect 
----------
CSpect emulator by Mike Dailly installed in local directory please download from http://www.cspect.org
feel free to support his development efforts & patreon https://www.patreon.com/mikedailly
    
HDF Monkey 
----------
    
    If you are running the app on Windows and hdfmonkey in not present in the same directory, you will see an error message in the main log Windows as it is missing.
       if that is the case you will see a 'Download and Install button' bottom right, once clicked it will try to fetch https://uto.speccy.org/downloads/hdfmonkey_windows.zip 
       and unzip hdfmonkey executable in the same directory. 
           If the above automated install is successful, you should then be able to select an image and navigate it.
            
    On Mac/Linux you will need to install hdfmonkey manually based on the instructions for your platform that can be found at: https://github.com/gasman/hdfmonkey
  
NextSync: 
------- 
Py Hdfm Gooey implements the <Server> side code and protocol of NextSync by Jari Komppa.
It does not require any dot .sync modification and it uses the same very close python logic as nextsync.py.
             
Initial realease on specnext: https://www.specnext.com/forum/viewtopic.php?f=17&t=1715&fbclid=IwAR1njrmr-wEU0DndAxBjO64K_NwY0E2zbqJVaVfiytHE2-A0eL8HWYeDKf8 
As a result you will need to run the dot same .sync command on your Next as with the console version and the same network protocol. 
             
The latest release v1.2 of the .sync command can be found here https://github.com/Threetwosevensixseven/specnext/releases/tag/nextsync_v1.2 . 
             
You may follow the same instructions as the provided in the readme.txt of that release.
On your Spectrum Next, clone or image copy the SYNC command that is located in the above release zip file into your next dot folder.
Navigate to NextSync tab, select the root folder to sync on the left.
Once you have selected the folder hit the 'prepare sync' button, check the Next Sync log Window on the right.
First time you will run .sync on your will be prompter to select the <server> IP address, this machine running NextSync.
From the log window pick the IP address from this machine you want to use and type it on your next.
Then start the sync server on this maching using the Yes, start sync button and then run the .sync command on your Next.
At this point your Spectrum Next will connect to your machine using a network socket and the files will be sent to your next.
As it is your Next that will connect to this machine check your firewall alows inbound calls to this machine on port: 2048 by default." ),

The same syncignore.txt and syncpoint.dat file logic applies and alows you to control the sync (please check Jari documentation).

NextSync source code can be found here: https://github.com/jarikomppa/specnext/tree/master/sync

If you run in any type of issue using the NextSync integration please run first the Jari command line version to see if it works as expected.

* On Mac/Linux: you will also need to install manualy mono-complete package for example using: sudo apt-get install mono-complete
    
* Start py-hdfm-gooey.py
    python py-hdfm-gooey.py
