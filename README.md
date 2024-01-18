Py-Hdfm-Gooey by Julien Clauzel based on HDFM-GOOEY - by em00k & based on NextSync by Jari Komppa

* Requirements: 
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
    
        - hdfmonkey -
    
    If you are running the app on Windows and hdfmonkey in not present in the same directory, you will see an error message in the main log Windows as it is missing.
       if that is the case you will see a 'Download and Install button' bottom right, once clicked it will try to fetch https://uto.speccy.org/downloads/hdfmonkey_windows.zip 
       and unzip hdfmonkey executable in the same directory. 
           If the above automated install is successful, you should then be able to select an image and navigate it.
            
    On Mac/Linux you will need to install hdfmonkey manually based on the instructions for your platform that can be found at: https://github.com/gasman/hdfmonkey 

* On Mac/Linux: you will also need to install manualy mono-complete package for example using: sudo apt-get install mono-complete
    
* Start py-hdfm-gooey.py
    python py-hdfm-gooey.py
