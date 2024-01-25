Py-Hdfm-Gooey by Julien Clauzel based on HDFM-GOOEY - by em00k & based on NextSync by Jari Komppa

The first tab of Py Hdfm Gooey is aimed at CSpect emulator users and developers. In that section you can mount an HDF image used by CSpect and upload download content using a built simple file explorer. Once the content is uploaded to the image you can then start CSpect directly from it and therefore exposes a simple to use frontend interface to the emulator. Key settings such as screen size can be directly adjusted, it avoids the need to know command line options to start using your emulated Spectrum Next.

The second tab is designed for real hardware owners such as KS1, KS2 or other clones that also has an ESP (WIFI module). Jari designed a while back a custom protocol called NextSync that allows to synchronize an entire folder that resides on a remote machine back to the Spectrum Next over the network. This utility implements the “server” side the program that will ‘listen’ and waits for incoming connections from your Next. On your Next machine you will run the custom dot “.sync” command that connects to the server here Py-Hdfm-Gooey. To set this up you will need first to download Jari zip package. The latest release v1.2 of the dot .sync command can be found here https://github.com/Threetwosevensixseven/specnext/releases/tag/nextsync_v1.2 . 

Download Jari latest release and inside the zip dot folder you will find a file called “SYNC”. Extract and copy that file in the /dot folder located on the root of your Spectrum Next SD card and boot it up as usual. Make sure WIFI is fully setup normally, that you can access the internet and your machine that will be running Py Hdfm gooey are on the same IP network and that no firewall blocks incoming communication on your “receiving” machine. By default, the custom protocol works on TCP port 2048.
Start, python py-hdfm-gooey.py and navigate to NextSync tab. On the built in Explorer select the root folder you’d like to sync and hit the “Prepare NextSync server” button. At this point the server is ready to go but not running yet, this allows you to review the above log. The first time I recommend that you select the “Sync once” option so the server will stop after the first .sync run. 
Since this is the first time you will run the .sync command on your Spectrum Next, the command will ask you to input what IP address it needs to connect to. In the log Window you should the machine Primary IP address (on non Windows system you may need to run ipconfig/ifconfig to see all available IPs). Your machine DHCP address usually starting by 10.0.x.y or 192.168.x.y, select the 4x digit IP address digit you are going to use for the upcoming step below.

On your Spectrum Next, select “Command Line” option and then simply type .sync and press enter. At this point as mentioned above it will request what IP address to connect to, so input the ip address selected above and press enter. 
On the next this configuration will be retained into C:/sys/config/nextsync.cfg if you need to change it later either edit the config file or type: .sync followed by the new IP address you wish to use to connect to for example: .sync 10.0.0.15

That’s it you should now be all go to go.

When ready hit the “Yes, start NextSync server” button and on your next type “.sync” again. If everything is set up properly you should now see your next downloading all the files and once done the .sync command will exit.

There are many other option & features in the tool for example once the first full sync has been done it will create a SyncPoint file so it knows only what needs to be done and synced the next time you run the .sync command. If such a file exists, a button will appear that allows you to delete it in order that you can perform a full new sync if need be. A create SyncIgnore button will appear if such a file is not present. These file types allow you to control what file extensions will not be synced and send to the remote machine.

For more information, please check the “Help” tab in the tool or below.

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

* Install Python from: https://www.python.org/downloads/
  
* Install pyside6 this is required for the UI to render the different controls being used:

    python -m pip install pyside6

* Copy Cspect (with the Spectrum Next roms) and hdfmonkey in the same directory (see above). 


CSpect 
----------

CSpect emulator by Mike Dailly installed in local directory please download from http://www.cspect.org
feel free to support his development efforts & patreon https://www.patreon.com/mikedailly

Other Mike CSpect sites and links:
https://mdf200.itch.io/cspect
https://dailly.blogspot.com/

    
HDF Monkey 
----------
    
If you are running the app on Windows and hdfmonkey in not present in the same directory, you will see an error message in the main log Windows as it is missing.
If that is the case you will see a 'Download and Install button' bottom right, once clicked it will try to fetch from
https://uto.speccy.org/downloads/hdfmonkey_windows.zip and unzip hdfmonkey executable in the same directory. 
If the above automated install is successful, you should then be able to select an image and navigate it.
          
On Mac/Linux you will need to install hdfmonkey manually based on the instructions for your platform that can be found at: https://github.com/gasman/hdfmonkey
  
NextSync 
--------

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

Mono (on Linux & MacOS Only)             
-----------------------------              
You will also need to install manualy mono-complete package for example using: sudo apt-get install mono-complete 

Enjoy!
    python py-hdfm-gooey.py
