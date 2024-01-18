
#!/usr/bin/env python3

""" 
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
        
"""



import sys, os, string, subprocess, platform, datetime, fnmatch, socket, struct, time, glob
from PySide6.QtCore import QSize, Qt, QSortFilterProxyModel, QModelIndex, QDir, QRunnable, Slot, Signal, QObject, QThreadPool, QRect
from PySide6.QtGui import QIcon, QColor
from PySide6.QtWidgets import QApplication, QComboBox, QDialogButtonBox, QLabel, QMainWindow, QPushButton, QTableWidget, QVBoxLayout, QWidget, QFileSystemModel, QTreeView, QFormLayout, QHBoxLayout, QLineEdit, QListWidgetItem, QListWidget, QFileDialog, QTableWidgetItem, QAbstractItemView, QDialog, QGridLayout, QTabWidget, QProgressBar, QCheckBox
import urllib.request
import zipfile, traceback


PY_HDFM_GOOEY_VERSION = "2.2.25"
PY_HDFM_GOOEY_ICON_IMAGE_FILE = "py-hdfm-gooey.png"
PY_HDFM_GOOEY_VERBOSE_LOG_MODE = False
PY_HDFM_GOOEY_UI_WIDTH = 900
PY_HDFM_GOOEY_UI_HEIGTH = 650
PY_HDFM_GOOEY_CONFIG_FILE_NAME =  "hdfg.cfg"
PY_HDFM_GOOEY_TAB_TITLE_GOOEY =  "HDFM Gooey"
PY_HDFM_GOOEY_TAB_TITLE_NEXTSYNC = "NextSync"
PY_HDFM_GOOEY_TAB_TITLE_NEXTSYNC_SYNCON = "NextSync - Sync ON"

HDF_MONKEY_WINDOWS_URL = "https://uto.speccy.org/downloads/hdfmonkey_windows.zip"

SETTING_HDDFILE = "hddffile"
SETTING_EXPLORERPATH = "explorerpath"
SETTING_SCREENSIZE = "screensize"
SETTING_SOUND = "sound"
SETTING_VSYNC = "vsync"
SETTING_HERTZ = "hertz"
SETTING_JOYSTICK = "joy"
SETTING_CSPECT = "cspect"
SETTING_CUSTOM = "custom"
SETTING_ESC = "esc"
SETTING_NEXTSYNC_EXPLORERPATH = "nextsync_explorerpath"
SETTING_NEXTSYNC_SYNCONCE = "nextsync_synconce"
SETTING_NEXTSYNC_ALWAYSSYNC = "nextsync_alwayssync"
SETTING_NEXTSYNC_SLOWTRANSFER = "nextsync_slowtransfer"

PORT = 2048    # Port to listen on (non-privileged ports are > 1023)
VERSION3 = "NextSync3"
VERSION = "NextSync4"
IGNOREFILE = "syncignore.txt"
SYNCPOINT = "syncpoint.dat"
MAX_PAYLOAD = 1024
NEXTSYNC_UI_HEIGTH = 300
IGNOREFILE_DEFAULT_CONTENT = (("syncignore.txt"), ("syncpoint.dat"), ("py-hdfm-gooey.png"),("*.bak"), ("*.py"))

INIT_LOG = (("NextSync - by Jari Komppa"), ("HDF Monkey - by Matt Westcott"), ("CSpect - by Mike Dailly http://cspect.org"), ("Inspired by HDFM-GOOEY - by em00k"), ("Py-Hdfm-Gooey - by Julien Clauzel 2024"))
INIT_HELP = (("Welcome to Py Hdfm Gooey help"), 
             (""), 
             ("History:"), 
             ("--------"), 
             ("Hdfm Gooey was oginaly created by emOOk back and NextSync by Jari Komppa."), 
             ("A while back I came back with the idea of an all in one bootstrapper, transfer tool for the Next and that was the initial idea of the tool."), 
             ("Last but not the least some source code was lost from HDFM Gooey and the tool was stuck back in that time, so with the agreement of emOOk I started a rewrite in Python that would also provide MacOS and Linux portability."), 
             (""),
             ("hdfmonkey:"), 
             ("-------"),
             ("Is a required external component developped by Matt Westcott  that allows to browse the image."),
             ("You will need to install it to get this application up and fully running."),
             (""),             
             ("If you are running the app on Windows and hdfmonkey in not present in the same directory,"),
             ("you will see an error message in the main log Windows as it is missing."),
             (""),             
             ("If that is the case you will see a 'Download and Install button' bottom right,"),
             ("once clicked it will try to fetch https://uto.speccy.org/downloads/hdfmonkey_windows.zip "),
             ("and unzip hdfmonkey executable in the same directory."),
             ("If the above automated install is successful, you should then be able to select an image and navigate it."),
             (""),
             ("On Mac/Linux you will need to install hdfmonkey manually based on the instructions for your platform that can be found at: https://github.com/gasman/hdfmonkey"),
             (""),             
             ("NextSync:"), 
             ("-------"), 
             ("Py Hdfm Gooey implements the <Server> side code and protocol of NextSync by Jari Komppa."),
             ("It does not require any dot .sync modification and it uses the same very close python logic as nextsync.py."),
             (""),             
             ("Initial realease on specnext: https://www.specnext.com/forum/viewtopic.php?f=17&t=1715&fbclid=IwAR1njrmr-wEU0DndAxBjO64K_NwY0E2zbqJVaVfiytHE2-A0eL8HWYeDKf8"), 
             ("As a result you will need to run the dot same .sync command on your Next as with the console version and the same network protocol."), 
             (""),             
             ("The latest release v1.2 of the .sync command can be found here https://github.com/Threetwosevensixseven/specnext/releases/tag/nextsync_v1.2 ."), 
             (""),             
             ("You may follow the same instructions as the provided in the readme.txt of that release."),
             ("On your Spectrum Next, clone or image copy the SYNC command that is located in the above release zip file into your next dot folder."),
             ("Navigate to NextSync tab, select the root folder to sync on the left."),
             ("Once you have selected the folder hit the 'prepare sync' button, check the Next Sync log Window on the right."),
             ("First time you will run .sync on your will be prompter to select the <server> IP address, this machine running NextSync."),
             ("From the log window pick the IP address from this machine you want to use and type it on your next."),
             ("Then start the sync server on this maching using the Yes, start sync button and then run the .sync command on your Next."),
             ("At this point your Spectrum Next will connect to your machine using a network socket and the files will be sent to your next."),
             ("As it is your Next that will connect to this machine check your firewall alows inbound calls to this machine on port: 2048 by default." ),
             (""),
             ("The same syncignore.txt and syncpoint.dat file logic applies and alows you to control the sync (please check Jari documentation)."),
             (""),
             ("NextSync source code can be found here: https://github.com/jarikomppa/specnext/tree/master/sync"),
             (""),
             ("If you run in any type of issue using the NextSync integration please run first the Jari command line version to see if it works as expected."),
             (""),
             ("Mono (on Linux & MacOS Only)"),             
             ("-------"),              
             ("You will also need to install manualy mono-complete package for example using: sudo apt-get install mono-complete"), 
             ("Enjoy!"),
             ("")
            )
CONFIG_FILE_SETTINGS = (SETTING_HDDFILE, SETTING_EXPLORERPATH, SETTING_SCREENSIZE, SETTING_SOUND, SETTING_VSYNC, SETTING_HERTZ, SETTING_JOYSTICK, SETTING_CSPECT, SETTING_CUSTOM, SETTING_ESC, SETTING_NEXTSYNC_EXPLORERPATH, SETTING_NEXTSYNC_SYNCONCE, SETTING_NEXTSYNC_ALWAYSSYNC, SETTING_NEXTSYNC_SLOWTRANSFER)
IMAGE_BUTTONS_SIZE = 190
DISK_ARROWS_BUTTONS_SIZE = 30

CSPECT_SCREEN_SIZES = (("Screen Size X1", "-w1"),("Screen Size X2", "-w2"),("Screen Size X3", "-w3"), ("Screen Size X4", "-w4"), ("Fullscreen", "-fullscreen"))
CSPECT_SOUND = (("Sound On", ""),("Sound Off", "-sound"))
CSPECT_SCREEN_SYNC = (("VSync On", "-vsync"),("VSync Off", ""))
CSPECT_JOYSTICK = (("Joystick On", "-vsync"),("Joystick Off", ""))
CSPECT_FREQUENCY = (("50Hz", ""),("60Hz", "-60"))
CSPECT_BASE_ARGUMENTS = "-basickeys -zxnext -nextrom"

FONT_GREEN = QColor(0, 255, 0)
FONT_BLUE = QColor(0, 0, 255)
FONT_RED = QColor(255, 0, 0)

UP_DIRECTORY = "[Up Directory..]"
DIRECTORY_CREATION_NOT_ALLOWED_CHARACTERS = ('"', '<', '>', ':', '\\', '/', '|', '?', '*', '!', '(',')', '.', "'", '$', '@')
HDFMONKEY_EXECUTABLE = "hdfmonkey"
FILTER_LABEL_TEXT = "Filter: "
FILTER_TEXT_WIDTH = 320
# NextSync static variables



assert sys.version_info >= (3, 6) # We need 3.6 for f"" strings.

class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        tuple (exctype, value, traceback.format_exc() )

    result
        object data returned from processing, anything

    progress
        int indicating % progress

    '''
    finished = Signal()
    error = Signal(tuple)
    result = Signal(object)
    progress = Signal(int)




class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
     
        global right_disk_image_explorer_content
        
        right_disk_image_explorer_path = []
        right_disk_image_explorer_content = []
        right_disk_image_path = ""
        right_disk_image_selected_files = []
        configuration_dictionary = {}
        
        self.left_file_explorer_selection_file_name = ""
        self.left_file_explorer_selection_full_filename_path = ""
        self.left_file_nextsync_explorer_selection_file_name = ""
        self.left_file_nextsync_explorer_selection_full_filename_path = ""
        
        self.image_explorer_item_list = QListWidget()
        
        self.threadpool = QThreadPool()
        
        class Worker(QRunnable):
            '''
            Worker thread

            Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

            :param callback: The function callback to run on this worker thread. Supplied args and
                             kwargs will be passed through to the runner.
            :type callback: function
            :param args: Arguments to pass to the callback function
            :param kwargs: Keywords to pass to the callback function

            '''

            def __init__(self, fn, *args, **kwargs):
                super(Worker, self).__init__()

                # Store constructor arguments (re-used for processing)
                self.fn = fn
                self.args = args
                self.kwargs = kwargs
                self.signals = WorkerSignals()

                # Add the callback to our kwargs
                self.kwargs['progress_callback'] = self.signals.progress

            @Slot()
            def run(self):
                '''
                Initialise the runner function with passed args, kwargs.
                '''

                # Retrieve args/kwargs here; and fire processing using them
                try:
                    result = self.fn(*self.args, **self.kwargs)
                except:
                    traceback.print_exc()
                    exctype, value = sys.exc_info()[:2]
                    self.signals.error.emit((exctype, value, traceback.format_exc()))
                else:
                    self.signals.result.emit(result)  # Return the result of the processing
                finally:
                    self.signals.finished.emit()  # Done        
        
        def get_tuple_value(tuple_type, text_value):
            for v in tuple_type:
                if v[0] == text_value:
                    return v[1]
        
        def get_int_value(str_value:str):
            
            try:
                value = int(str_value)
                return value
            except:
                return 0

        def progress_fn(n):
                # print("%d%% done" % n)
                # add_nextsync_log_window ("Progress: " + str(n))
                self.nextsync_progressbar.setValue(n)

        # def execute_this_fn(progress_callback):
        #     for n in range(0, 5):
        #         time.sleep(1)
        #         progress_callback.emit(n*100/4)

        #     return "Done."

        # def print_output(s):
        #     print(s)

        def thread_complete():
            add_nextsync_log_window("Sync Complete!")
            nextsync_hide_start_cancel_buttons()
            self.nextsync_prepare_server.setVisible(True)
            
        def nextsync_server_exception_occured(ex):
            add_nextsync_log_window ("NextSync exception occured while syncing: " + str(ex))

        def nextsync_hide_start_cancel_buttons():
            self.nextsync_start_server.setVisible(False)
            self.nextsync_cancel_server.setVisible(False)            
        
        def nextsync_show_start_cancel_buttons():
            self.nextsync_start_server.setVisible(True)
            self.nextsync_cancel_server.setVisible(True)            

        
        def set_all_buttons_disabled():
            
            self.imageinput.setDisabled(True)
            self.selectimage.setDisabled(True)
            self.hdfm_gooey_diskdrive.setDisabled(True)
            self.filterlabel.setDisabled(True)
            self.filtertext.setDisabled(True)
            self.treeview.setDisabled(True)
            self.button_to_disk.setDisabled(True)
            self.button_to_image.setDisabled(True)
            self.TableWidgetImage.setDisabled(True)
            self.button_to_disk.setDisabled(True)
            self.button_new_folder.setDisabled(True)
            self.button_delete_files.setDisabled(True)
            self.button_cancel.setDisabled(True)
            self.button_confirm_deletion.setDisabled(True)
            self.new_folder_input.setDisabled(True)
            self.button_create_directory.setDisabled(True)
            self.button_start_cspect.setDisabled(True)
            self.cspect_screensize.setDisabled(True)
            self.cspect_sound.setDisabled(True)
            self.cspect_vsync.setDisabled(True)
            self.cspect_joystick.setDisabled(True)
            self.cspect_frequency.setDisabled(True)
            self.button_open_config_file.setDisabled(True)
        
        def set_all_buttons_enabled():
            self.imageinput.setDisabled(False)
            self.selectimage.setDisabled(False)
            self.hdfm_gooey_diskdrive.setDisabled(False)
            self.filterlabel.setDisabled(False)
            self.filtertext.setDisabled(False)
            self.treeview.setDisabled(False)
            self.button_to_disk.setDisabled(False)
            self.button_to_image.setDisabled(False)
            self.TableWidgetImage.setDisabled(False)
            self.button_to_disk.setDisabled(False)
            self.button_new_folder.setDisabled(False)
            self.button_delete_files.setDisabled(False)
            self.button_cancel.setDisabled(False)
            self.button_confirm_deletion.setDisabled(False)
            self.new_folder_input.setDisabled(False)
            self.button_create_directory.setDisabled(False)
            self.button_start_cspect.setDisabled(False)
            self.cspect_screensize.setDisabled(False)
            self.cspect_sound.setDisabled(False)
            self.cspect_vsync.setDisabled(False)
            self.cspect_joystick.setDisabled(False)
            self.cspect_frequency.setDisabled(False)
            self.button_open_config_file.setDisabled(False)
        
        def enable_image_selection():
            self.imageinput.setDisabled(False)
            self.selectimage.setDisabled(False)  
            
        def disable_image_selection():
            self.imageinput.setDisabled(True)
            self.selectimage.setDisabled(True)           
            
        def download_and_install_hdflonkey():
            try:
                zip_path, _ = urllib.request.urlretrieve(HDF_MONKEY_WINDOWS_URL)
                with zipfile.ZipFile(zip_path, "r") as f:
                    f.extractall()
                self.button_new_folder.setVisible(True)
                self.button_delete_files.setVisible(True) 
                self.download_and_install_hdfmonkey_button.setVisible(False)
                add_main_log_window("Successfully installed hdfmonkey.")
                
                if is_hdfmonkey_present():
                    load_image()                
                    set_all_buttons_enabled()
                    
                return True
            except Exception as ex:
                add_main_log_window("Failed downloading & installing hdfmonkey: " + str(ex))
                #set_all_buttons_enabled()
                return False
    
        def show_hdf_monkey_download_and_install_buttons():
            self.download_and_install_hdfmonkey_button.setVisible(True)
            self.button_new_folder.setVisible(False)
            self.button_delete_files.setVisible(False)
            
        
        def load_configuration_file():
            
            try:
                
                # Load configuration dictionary
                config_file = open(PY_HDFM_GOOEY_CONFIG_FILE_NAME, "r")
                content = config_file.readlines()
                
                for line in content:
                    setting = line.split("=")
                    config_setting_name = setting[0].strip()
                    config_setting_value= setting[1].strip()
                    
                    for cs in CONFIG_FILE_SETTINGS:
                        if cs == config_setting_name:
                            configuration_dictionary[cs] = config_setting_value
                            break
                
                config_file.close()


                        
                
                #  Now set the settings back to the application SETTING_SCREENSIZE

                self.imageinput.setText(configuration_dictionary[SETTING_HDDFILE])
                self.cspect_sound.setCurrentIndex(get_int_value(configuration_dictionary[SETTING_SOUND]))
                self.cspect_screensize.setCurrentIndex(get_int_value(configuration_dictionary[SETTING_SCREENSIZE]))
                self.cspect_vsync.setCurrentIndex(get_int_value(configuration_dictionary[SETTING_VSYNC]))
                self.cspect_joystick.setCurrentIndex(get_int_value(configuration_dictionary[SETTING_JOYSTICK]))
                self.cspect_frequency.setCurrentIndex(get_int_value(configuration_dictionary[SETTING_HERTZ]))
                
                if configuration_dictionary[SETTING_EXPLORERPATH] != "":
                    if not os.path.isdir(configuration_dictionary[SETTING_EXPLORERPATH]):
                        # if the path is a file instead of a directory point explorer path to the root folder instead
                        splited_path = str.split(configuration_dictionary[SETTING_EXPLORERPATH], "/")
                        root_folder = ""
                        for rf in range (0,len(splited_path)-1):
                            root_folder += splited_path[rf] + "/"
                        configuration_dictionary[SETTING_EXPLORERPATH] = root_folder
                        

                    self.model.setRootPath(configuration_dictionary[SETTING_EXPLORERPATH])
                    self.treeview.setRootIndex(self.model.index(configuration_dictionary[SETTING_EXPLORERPATH]))
                    self.left_file_explorer_selection_full_filename_path = configuration_dictionary[SETTING_EXPLORERPATH]
                    self.file_explorer_path.setText(self.left_file_explorer_selection_full_filename_path)

                if configuration_dictionary[SETTING_NEXTSYNC_EXPLORERPATH] != "":
                    if not os.path.isdir(configuration_dictionary[SETTING_NEXTSYNC_EXPLORERPATH]):
                        # if the path is a file instead of a directory point explorer path to the root folder instead
                        splited_path = str.split(configuration_dictionary[SETTING_NEXTSYNC_EXPLORERPATH], "/")
                        root_folder = ""
                        for rf in range (0,len(splited_path)-1):
                            root_folder += splited_path[rf] + "/"
                        configuration_dictionary[SETTING_NEXTSYNC_EXPLORERPATH] = root_folder
                        

                    self.nextsync_model.setRootPath(configuration_dictionary[SETTING_NEXTSYNC_EXPLORERPATH])
                    self.nextsync_treeview.setRootIndex(self.nextsync_model.index(configuration_dictionary[SETTING_NEXTSYNC_EXPLORERPATH]))
                    self.left_file_nextsync_explorer_selection_full_filename_path = configuration_dictionary[SETTING_NEXTSYNC_EXPLORERPATH]
                    self.nextsync_file_explorer_path.setText(self.left_file_nextsync_explorer_selection_full_filename_path)
                
                if configuration_dictionary[SETTING_NEXTSYNC_SYNCONCE] != "":
                    if configuration_dictionary[SETTING_NEXTSYNC_SYNCONCE] == "1" or configuration_dictionary[SETTING_NEXTSYNC_SYNCONCE].lower() == "true":
                        self.nextsync_synconce_checkbox.setChecked(True)
                    else:
                        self.nextsync_synconce_checkbox.setChecked(False)
                        
                if configuration_dictionary[SETTING_NEXTSYNC_ALWAYSSYNC] != "":
                    if configuration_dictionary[SETTING_NEXTSYNC_ALWAYSSYNC] == "1" or configuration_dictionary[SETTING_NEXTSYNC_ALWAYSSYNC].lower() == "true":
                        self.nextsync_alwayssync_checkbox.setChecked(True)
                    else:
                        self.nextsync_alwayssync_checkbox.setChecked(False)
                        
                if configuration_dictionary[SETTING_NEXTSYNC_SLOWTRANSFER] != "":
                    if configuration_dictionary[SETTING_NEXTSYNC_SLOWTRANSFER] == "1" or configuration_dictionary[SETTING_NEXTSYNC_SLOWTRANSFER].lower() == "true":
                        self.nextsync_slowtransfer_checkbox.setChecked(True)
                    else:
                        self.nextsync_slowtransfer_checkbox.setChecked(False)
                                
                        
                add_main_log_window("Loaded configuration file.")

                return True
            
            except:
                return False

        def save_configuration_file():
            
            try:
                config_file = open(PY_HDFM_GOOEY_CONFIG_FILE_NAME, "w")
                config_array = [];   
                for cs in CONFIG_FILE_SETTINGS:
                    config_array.append(cs + "=" + str(configuration_dictionary[cs]) + '\n') 

                config_file.writelines(config_array)
                config_file.close()
                if PY_HDFM_GOOEY_VERBOSE_LOG_MODE:
                    add_main_log_window("Saved configuration file.")
                    
            except Exception as e:
                add_main_log_window("Failed saving configuration file. Exception:" + str(e))

        def is_filetype_a_directory(file_type:str):
            if file_type == "b'[DIR]" or file_type == 'b"[DIR]':
                return True
            else:
                return False  
       
        def set_cspect_screen_size():
            configuration_dictionary[SETTING_SCREENSIZE] = self.cspect_screensize.currentIndex()
            save_configuration_file()

        def set_cspect_sound_on_off():
            configuration_dictionary[SETTING_SOUND] = self.cspect_sound.currentIndex()
            save_configuration_file()

        def set_cspect_vsync_on_off():
            configuration_dictionary[SETTING_VSYNC] = self.cspect_vsync.currentIndex()
            save_configuration_file()
        
        def set_cspect_joystick_on_off():
            configuration_dictionary[SETTING_JOYSTICK] = self.cspect_joystick.currentIndex()
            save_configuration_file()

        def set_cspect_display_frequency():
            configuration_dictionary[SETTING_HERTZ] = self.cspect_frequency.currentIndex()
            save_configuration_file()
        
        def open_cspect_configuration_file():
            if platform.system() == "Windows":
                execute_shell_command("notepad", PY_HDFM_GOOEY_CONFIG_FILE_NAME)
            else:
                execute_shell_command("vim", "./" + PY_HDFM_GOOEY_CONFIG_FILE_NAME)
            return
        
        def launch_cspect():
            if len(right_disk_image_explorer_content) !=0: # check that we have an image content first
                
                set_all_buttons_disabled()
                
                cspect_arguments = " " + CSPECT_BASE_ARGUMENTS + " "
                cspect_screensize_text = self.cspect_screensize.currentText()
                cspect_sound_text = self.cspect_sound.currentText()
                cspect_vsync_text = self.cspect_vsync.currentText()
                cspect_joystick_text = self.cspect_joystick.currentText()
                cspect_frequency_text = self.cspect_frequency.currentText()
            
                cspect_arguments += get_tuple_value(CSPECT_SCREEN_SIZES, cspect_screensize_text) + " "
                cspect_arguments += get_tuple_value(CSPECT_SOUND, cspect_sound_text) + " "
                cspect_arguments += get_tuple_value(CSPECT_SCREEN_SYNC, cspect_vsync_text) + " "
                cspect_arguments += get_tuple_value(CSPECT_JOYSTICK, cspect_joystick_text) + " "
                cspect_arguments += get_tuple_value(CSPECT_FREQUENCY, cspect_frequency_text) + " "
            
                if configuration_dictionary[SETTING_ESC] != "":
                    cspect_arguments += " -esc "

                if configuration_dictionary[SETTING_CUSTOM] != "":
                    cspect_arguments += " " + configuration_dictionary[SETTING_CUSTOM] + " "                
            
                cspect_arguments += " -mmc=" + self.right_disk_image_path + " "

                print (f"Cspect start with arguments: {cspect_arguments}")
                add_main_log_window("CSpect start: " + "CSpect.exe" + cspect_arguments)
                try:
                    if platform.system() == "Windows":
                        execute_shell_command ("CSpect.exe", cspect_arguments)
                        #execute_shell_command_no_wait ("CSpect.exe", cspect_arguments)
                    else:
                        execute_shell_command ("mono CSpect.exe", cspect_arguments)
                except subprocess.CalledProcessError as ex:
                    if ex.returncode == 1:
                        add_main_log_window("ERROR: CSpect.exe is not present in the same local directory as Py Hdfm Gooey.Please install it from http://cspect.org")
                    else:
                        add_main_log_window("ERROR: Unknown shell execute error: " + str(ex.returncode) + " - :" + str(ex))
                                                
                    if platform.system() != "Windows":
                        add_main_log_window("On MacOS and Linux mono is required as it runs under it. Please make sure mono ")
                    
                set_all_buttons_enabled()
                

        def delete_files_button_show_confirmation_buttons():
            self.button_confirm_deletion.setVisible(True)
            self.button_cancel.setVisible(True)
            self.button_new_folder.setVisible(False)
            self.button_delete_files.setVisible(False)            
           

        def button_confirm_directory_deletion():
            image_delete_files()
            self.button_confirm_deletion.setVisible(False)
            self.button_cancel.setVisible(False)
            self.button_new_folder.setVisible(True)
            self.button_delete_files.setVisible(True)            
            
        def button_cancel_deletion():
            self.button_confirm_deletion.setVisible(False)
            self.button_cancel.setVisible(False)
            self.button_new_folder.setVisible(True)
            self.button_delete_files.setVisible(True)        
            
        def is_hdfmonkey_present():

            hdfmonkeyexecresult = execute_hdf_monkey("", "")
            
            try:
                if hdfmonkeyexecresult.returncode == 0:
                    command_execution = hdfmonkeyexecresult.stdout
                    if "hdfmonkey help" not in str(command_execution):
                        add_main_log_window("Failed executing hdfmonkey, please make sure it is installed in the same local directory as Py-Hdfm-Gooey.") 
                        return False
                    else:
                        return True
            except Exception as ex:
                add_main_log_window("Failed executing hdfmonkey, please make sure it is installed in the same local directory as Py-Hdfm-Gooey...." + str(ex)) 
                return False
 
        def load_image():

            global right_disk_image_explorer_content

            # Populate right impage path content
            self.right_disk_image_path = self.imageinput.text()
            
            right_disk_image_explorer_content = []
            self.TableWidgetImage.clear()
            self.TableWidgetImage.setRowCount(0)
            set_table_image_properties()
        
            if len(self.right_disk_image_path) != 0 and self.right_disk_image_path != '""':
                hdfmonkeyexecresult = execute_hdf_monkey("ls", self.right_disk_image_path)

                if hdfmonkeyexecresult.returncode == 0:
                    command_execution = hdfmonkeyexecresult.stdout
                    update_disk_manager_widget_table(command_execution)
                    self.diskimageexplorerlabelpath.setText(generate_disk_file_path().replace('//', '/'))
                    set_all_buttons_enabled()
                    return True
                else:
                    add_main_log_window("Failed loading image :" + self.right_disk_image_path + "  - hdfmonkey result code: " + str(hdfmonkeyexecresult.returncode) )  

            set_all_buttons_disabled()
            enable_image_selection()

            return False

        def apply_file_extension_filter():
            self.model.setNameFilters([self.filtertext.text()])
            set_treeview_properties()
            self.treeview.show()

        def apply_file_extension_filter_nextsync():
            self.nextsync_model.setNameFilters([self.nextsync_filtertext.text()])
            set_treeview_properties()
            self.nextsync_treeview.show()        

        def add_main_log_window(string_to_log:str):

            newItem = QListWidgetItem()
            newItem.setText(string_to_log)
            self.listWidgetLog.insertItem(0, newItem)

        def add_nextsync_log_window(string_to_log:str, from_top:bool = True):

            newItem = QListWidgetItem()
            newItem.setText(string_to_log)
            if from_top:
                self.nextsync_log.insertItem(0, newItem)
            else:
                self.nextsync_log.insertItem(self.nextsync_log.count(), newItem)          
            
        def add_help_content(string_to_log:str, from_top:bool = True):

            newItem = QListWidgetItem()
            newItem.setText(string_to_log)
            if from_top:
                self.listWidgetHelp.insertItem(0, newItem)
            else:
                self.listWidgetHelp.insertItem(self.listWidgetHelp.count(), newItem)
            
        def set_table_image_properties():
            self.TableWidgetImage.setHorizontalHeaderLabels(["Name", "Type", "Size"])
            # self.TableWidgetImage.setSortingEnabled(True)
            # self.TableWidgetImage.sortItems(0, Qt.SortOrder.AscendingOrder)  

        def set_treeview_properties():
            self.treeview.setSortingEnabled(True)
            self.treeview.sortByColumn(0, Qt.SortOrder.AscendingOrder)
            self.treeview.setSelectionMode(QAbstractItemView.SingleSelection)
            self.nextsync_treeview.setSortingEnabled(True)
            self.nextsync_treeview.sortByColumn(0, Qt.SortOrder.AscendingOrder)
            self.nextsync_treeview.setSelectionMode(QAbstractItemView.SingleSelection)            

            
        def image_newfolder():
            
            global right_disk_image_explorer_content
            
            if len(right_disk_image_explorer_content) !=0: # check that we have an image content first
                # hide create folder and delete folder buttons
                self.button_new_folder.setVisible(False)
                self.button_delete_files.setVisible(False)
                self.new_folder_input.setVisible(True)
                self.button_create_directory.setVisible(True)
                self.button_create_directory_cancel.setVisible(True)
            else:
                add_main_log_window("Please load an image file first !")
                
        def image_newfolder_cancel():
            
            global right_disk_image_explorer_content
            
            if len(right_disk_image_explorer_content) !=0: # check that we have an image content first
                # hide create folder and delete folder buttons
                self.button_new_folder.setVisible(True)
                self.button_delete_files.setVisible(True)
                self.new_folder_input.setVisible(False)
                self.button_create_directory.setVisible(False)
                self.button_create_directory_cancel.setVisible(False)
            else:
                add_main_log_window("Please load an image file first !")

        def image_newfolder_create():

            directory_to_create = self.new_folder_input.text()
            
            for not_allowed_chars in DIRECTORY_CREATION_NOT_ALLOWED_CHARACTERS:
                if not_allowed_chars in directory_to_create:
                    nachars = ""
                    for n in DIRECTORY_CREATION_NOT_ALLOWED_CHARACTERS:
                        nachars += n
                    add_main_log_window("Do not use any of the forbiden characters :" + nachars + " when creating directories!")
                    return
            
            directory_to_create = generate_disk_file_path() + "/" + directory_to_create
            directory_to_create = directory_to_create.replace("//", "/")
            
            self.button_new_folder.setVisible(True)
            self.button_delete_files.setVisible(True)
            self.new_folder_input.setVisible(False)
            self.button_create_directory.setVisible(False)
            self.button_create_directory_cancel.setVisible(False)

            hdfmonkeyexecresult = execute_hdf_monkey("mkdir", self.right_disk_image_path, directory_to_create)
            
            if hdfmonkeyexecresult.returncode != 0:
                add_main_log_window("Failed creating directory - hdfmonkey result code: " + str(hdfmonkeyexecresult.returncode) )
                
            hdfmonkeyexecresult = execute_hdf_monkey("ls", self.right_disk_image_path, generate_disk_file_path())
            
            if hdfmonkeyexecresult.returncode != 0:
                add_main_log_window("Failed browsing directory after creating it - hdfmonkey result code: " + str(hdfmonkeyexecresult.returncode) )            

            command_execution = hdfmonkeyexecresult.stdout
            update_disk_manager_widget_table(command_execution)
            
        def select_image():

            global right_disk_image_explorer_path
            global right_disk_image_explorer_content
            global right_disk_image_path
            global right_disk_image_selected_files 

            dialog = QFileDialog(self) # https://doc.qt.io/qtforpython-6.2/PySide6/QtWidgets/QFileDialog.html
            dialog.setFileMode(QFileDialog.AnyFile)
            dialog.setViewMode(QFileDialog.Detail)
            fileName = QFileDialog.getOpenFileName(self,"Open File","/home/", "Images (*.img *.hdf)" )
            self.imageinput.setText('"' + str(fileName[0]) + '"')
            configuration_dictionary[SETTING_HDDFILE] = self.imageinput.text()
            
            right_disk_image_explorer_path = []
            right_disk_image_explorer_content = []
            right_disk_image_path = ""
            right_disk_image_selected_files = []
            self.TableWidgetImage.clear()
            self.TableWidgetImage.setRowCount(0)
            
            set_table_image_properties()
            
            # Now try to load it
            if load_image():
                save_configuration_file()
        
        def execute_hdf_monkey(command_to_execute, image_path, additional_args = ""):
            exec_process = subprocess.CompletedProcess 
            try:
                execution_cmd = HDFMONKEY_EXECUTABLE + " " + command_to_execute + " " + image_path + " " + additional_args
                exec_process = subprocess.run(execution_cmd, shell=True, check=True, stdout=subprocess.PIPE)
            except subprocess.CalledProcessError as ex:

                    exec_process.returncode = ex.returncode

                    if ex.returncode == 1:

                        add_main_log_window("ERROR: Once hdfmonkey is installed in the same directory close the application and restart it.")
                        
                        if platform.system() == "Windows":
                            add_main_log_window("ERROR: hdfmonkey is required and likely not present in local directory, please install a pre-compiled version from https://uto.speccy.org/downloads/hdfmonkey_windows.zip or compile it from https://github.com/gasman/hdfmonkey .")
                        else:
                            add_main_log_window("ERROR: hdfmonkey execution failed:" + str(ex) + ", please make sure it is installed from https://github.com/gasman/hdfmonkey and working properly.")
                            
                            
                    elif ex.returncode == 255:
                        add_main_log_window("ERROR: hdfmonkey failed - A file can't be opened: " + execution_cmd + " this is commonly caused by strange characters such as quotes and signs")
                    else:
                        add_main_log_window("ERROR: hdfmonkey " + HDFMONKEY_EXECUTABLE + " execution failed with unknown error: " + execution_cmd + " - :" + str(ex))
                    #pass
                            
            return exec_process
        
        def execute_shell_command(command_to_execute, additional_args = ""):
            execution_cmd = command_to_execute + " " + additional_args
            return subprocess.run(execution_cmd, shell=True, check=True, stdout=subprocess.PIPE)
        
        def execute_shell_command_no_wait(command_to_execute, additional_args = ""):
            execution_cmd = command_to_execute + " " + additional_args
            return subprocess.run(execution_cmd, shell=False, stdin=None, stdout=None, stderr=None,close_fds=True, start_new_session=True, capture_output=False, timeout=None)        
        
        def update_root_drive():
            self.treeview.setRootIndex(self.model.index(self.hdfm_gooey_diskdrive.itemText(0)))
            set_treeview_properties()
            self.treeview.show()
            
        def nextsync_update_root_drive():
            self.nextsync_treeview.setRootIndex(self.nextsync_model.index(self.nextsync_diskdrive.itemText(0)))
            self.nextsync_treeview.show()
        
        # recursively delete all files in sub directories
        def delete_sub_directory_content(image_path, destination):
            
            # list and delete all files in that directory
            hdfmonkeyexecresult = execute_hdf_monkey("ls", image_path, '"' + destination + '"')
            if hdfmonkeyexecresult.returncode == 0:
                command_execution = hdfmonkeyexecresult.stdout
                
                results_lines = command_execution.splitlines()
                
                if len(command_execution) > 0:
                
                    for files in results_lines:
                
                        directory_result_table = str.split(str(files), '\\t')

                        file_type = directory_result_table[0]
                        file_name = directory_result_table[1].replace("'", "").replace('"', "")
                        #file_name = directory_result_table[1].replace('"', "")
                
                        if not is_filetype_a_directory(file_type):
                            hdfmonkeyexecresult = execute_hdf_monkey("rm", self.right_disk_image_path,'"' + destination + "/" + file_name + '"')
                            if hdfmonkeyexecresult.returncode != 0:
                                add_main_log_window("Failed deleting file " + self.right_disk_image_path + '"' + destination + "/" + file_name + '"' + " - hdfmonkey result code: " + str(hdfmonkeyexecresult.returncode) )            

                        else:
                            delete_sub_directory_content(image_path, destination + "/" + file_name)
                            # delete the directory in then end
                            hdfmonkeyexecresult = execute_hdf_monkey("rm", self.right_disk_image_path,'"' + destination + "/" + file_name + '"')
                            if hdfmonkeyexecresult.returncode != 0:
                                add_main_log_window("Failed deleting file " + self.right_disk_image_path + '"' + destination + "/" + file_name + '"' + " - hdfmonkey result code: " + str(hdfmonkeyexecresult.returncode) )            
            
        # recursively get all files in sub directories from image and copy to disj
        def get_directory_content(image_path, image_source, disk_source, folder_name):
            
            image_source += "/" + folder_name

            image_source = image_source.replace("//", "/") # on root drive remove double slashes
            
            if platform.system() == "Windows":
                disk_source += "\\" + folder_name
            else:
                disk_source += "/" + folder_name
            image_source = image_source.replace('"', '')
            
            if is_directory(image_path, image_source):

                # list and get all files in that directory
                hdfmonkeyexecresult = execute_hdf_monkey("ls", image_path, '"' + image_source + '"')
                if hdfmonkeyexecresult.returncode == 0:
                    command_execution = hdfmonkeyexecresult.stdout
                
                    results_lines = command_execution.splitlines()
                
                    if len(command_execution) > 0:
                
                        for files in results_lines:
                
                            directory_result_table = str.split(str(files), '\\t')

                            file_type = directory_result_table[0]
                            file_name = directory_result_table[1].rstrip("'")

                            if platform.system() == "Windows":
                                disk_destination = disk_source + "\\" + file_name
                            else:
                                disk_destination = disk_source + "/" + file_name                        
                
                            if not is_filetype_a_directory(file_type):
                            
                                get_source = '"' + image_source + "/" + file_name + '" "' + disk_destination + '"'
                                get_source = get_source.replace('""', '"')
                            
                                hdfmonkeyexecresult = execute_hdf_monkey("get", self.right_disk_image_path, get_source)
                                if hdfmonkeyexecresult.returncode != 0:
                                    add_main_log_window("Failed getting file: " + self.right_disk_image_path + '"' + image_source + "/" + file_name + '"' + " - hdfmonkey result code: " + str(hdfmonkeyexecresult.returncode))            

                            else:

                                disk_destination = disk_destination.replace('"', '')
                                # create the directory 

                                try:
                                    os.makedirs(disk_destination)
                                except FileExistsError:
                                    pass
                                except Exception as ex:
                                    add_main_log_window("Failed creating directory: " + disk_destination + " - " + str(ex))            
                                    
                                # execresult = execute_shell_command("mkdir" , '"' + disk_destination + '"')
                                # if execresult.returncode != 0:
                                #     add_main_log_window("Failed creating directory: " + disk_destination + " - hdfmonkey result code: " + str(execresult.returncode) + " - " + str(execresult.stderr))            

                                get_directory_content (image_path, image_source, disk_source,  file_name)

        
        #First returned value is the root parent directory full path second variable is the last path or filename
        def get_parent_root_directory_splited(file_name:str):
            
            token_path = file_name.split("/")
            
            result_path = ""
            row = 1
            for i in token_path:
                result_path += token_path[row-1]
                row +=1
                if row == len(token_path):
                    break
                if len(token_path) != row:
                    result_path += "/"                
            return result_path , token_path[row-1]         
        
        def is_directory(image_path, source):
            
            root_folder , file_name_from_source = get_parent_root_directory_splited (source)

            hdfmonkeyexecresult = execute_hdf_monkey("ls", image_path, root_folder)

            if hdfmonkeyexecresult.returncode == 0:
                command_execution = hdfmonkeyexecresult.stdout
                
                results_lines = command_execution.splitlines()

                for line in results_lines:                
                    directory_result_table = str.split(str(line), '\\t')

                    file_type = directory_result_table[0]
                    file_name = str(directory_result_table[1].rstrip("'"))
                    file_name = file_name.replace('\\', "")
                
                    if file_name == file_name_from_source:
                        if is_filetype_a_directory(file_type):
                            return True
                        else:
                            return False
                        
            return False

        def image_delete_files():
            
            if len(right_disk_image_explorer_content) !=0:
                set_all_buttons_disabled()
                
                for f in right_disk_image_selected_files:
                    try:
                        if f != UP_DIRECTORY:
                            file_or_directory_to_delete = generate_disk_file_path() + "/" + f
                            file_or_directory_to_delete = file_or_directory_to_delete.replace("//", "/") # if we are on root we get double slashes

                            if is_directory(self.right_disk_image_path, generate_disk_file_path() + "/" + f ):
                                
                                delete_sub_directory_content(self.right_disk_image_path, file_or_directory_to_delete)
                            
                            hdfmonkeyexecresult = execute_hdf_monkey("rm", self.right_disk_image_path, file_or_directory_to_delete )
                            
                            if hdfmonkeyexecresult.returncode == 0:
                                hdfmonkeyexecresult = execute_hdf_monkey("ls", self.right_disk_image_path,generate_disk_file_path())
                                command_execution = hdfmonkeyexecresult.stdout
                                                            

                    except Exception as ex:
                        
                        add_main_log_window("Failed deleting file: " + f + " ! - " + str(ex))
                        set_all_buttons_enabled()
 
                hdfmonkeyexecresult = execute_hdf_monkey("ls", self.right_disk_image_path,generate_disk_file_path())
                command_execution = hdfmonkeyexecresult.stdout
                                
                update_disk_manager_widget_table(command_execution)
            else:
                add_main_log_window("Please select an image file or folder first to delete!")

            set_all_buttons_enabled()

            hdfmonkeyexecresult = execute_hdf_monkey("ls", self.right_disk_image_path,generate_disk_file_path())
            
            if hdfmonkeyexecresult.returncode == 0:
                command_execution = hdfmonkeyexecresult.stdout
                update_disk_manager_widget_table(command_execution)
            else:
                add_main_log_window("Failed executing hdfmonkey to list file.")      

        def nextsync_perform_checks_and_prepare_server_start():
            nextsync_warnings()


        def nextsync_start_server():
             # Pass the function to execute
            try:
                worker = Worker(nextsync_do_server_job) # Any other args, kwargs are passed to the run function
                #worker.signals.result.connect(print_output)
                worker.signals.finished.connect(thread_complete)
                worker.signals.progress.connect(progress_fn)
                worker.signals.error.connect(nextsync_server_exception_occured)
                # Execute
                self.threadpool.start(worker)
                nextsync_hide_start_cancel_buttons()

            except Exception as ex:
                print (str(ex))           
       
        # Copies the selected file to image
        def on_treeview_clicked():
            for ix in self.treeview.selectedIndexes():
                if self.model.fileName(ix) == "..":
                    self.left_file_explorer_selection_file_name = ""
                    self.left_file_explorer_selection_full_filename_path = self.model.filePath(ix)
                    
                    splitted_filepath = self.left_file_explorer_selection_full_filename_path.split('/')
                    selected_explorer_item_directory_destination = ""
                    for file_dest_token in range (0, len(splitted_filepath)-2):
                        selected_explorer_item_directory_destination += splitted_filepath[file_dest_token] + "/"
                        
                    self.treeview.setRootIndex(self.model.index(selected_explorer_item_directory_destination,0))
                    set_treeview_properties()
                    self.treeview.show()
                    
                    self.file_explorer_path.setText(selected_explorer_item_directory_destination)
                    
                    configuration_dictionary[SETTING_EXPLORERPATH] = selected_explorer_item_directory_destination
                    save_configuration_file()
                    break
                
                else:
                    
                    self.left_file_explorer_selection_file_name = self.model.fileName(ix)
                    self.left_file_explorer_selection_full_filename_path = self.model.filePath(ix)
                    if platform.system() != "Windows":
                        self.left_file_explorer_selection_full_filename_path.replace("\\", '/')                
                
                    self.file_explorer_path.setText(self.left_file_explorer_selection_full_filename_path)
                    configuration_dictionary[SETTING_EXPLORERPATH] = self.left_file_explorer_selection_full_filename_path
                    save_configuration_file()
                
                    break

        def on_treeview_double_clicked():
            # if the user clicks on ".." to go a level up in directory structure set the root path a level up
            nextsync_hide_start_cancel_buttons()
            self.nextsync_prepare_server.setVisible(True)

            for ix in self.treeview.selectedIndexes():
                if self.model.fileName(ix) == "..":
                    self.left_file_explorer_selection_file_name = ""
                    self.left_file_explorer_selection_full_filename_path = self.model.filePath(ix)
                    
                    splitted_filepath = self.left_file_explorer_selection_full_filename_path.split('/')
                    selected_explorer_item_directory_destination = ""
                    for file_dest_token in range (0, len(splitted_filepath)-2):
                        selected_explorer_item_directory_destination += splitted_filepath[file_dest_token] + "/"
                        
                    self.treeview.setRootIndex(self.model.index(selected_explorer_item_directory_destination,0))
                    set_treeview_properties()
                    self.treeview.show()
                    
                    self.file_explorer_path.setText(selected_explorer_item_directory_destination)
                    
                    configuration_dictionary[SETTING_EXPLORERPATH] = selected_explorer_item_directory_destination
                    save_configuration_file()
             
                break         
        
        def nextsync_get_fileexplorer_root_selection():
              if self.left_file_nextsync_explorer_selection_full_filename_path != "":
                selected_explorer_item_directory_destination = ""
                if not os.path.isdir(self.left_file_nextsync_explorer_selection_full_filename_path):
                    # we are pointing to a file not a directory
                    splitted_filepath = self.left_file_nextsync_explorer_selection_full_filename_path.split('/')
                    for file_dest_token in range (0, len(splitted_filepath)-2):
                        selected_explorer_item_directory_destination += splitted_filepath[file_dest_token] + "/"
                else:
                    selected_explorer_item_directory_destination = self.left_file_nextsync_explorer_selection_full_filename_path
                    if not self.left_file_nextsync_explorer_selection_full_filename_path.endswith("/"):
                        selected_explorer_item_directory_destination = selected_explorer_item_directory_destination + "/"
              
                return selected_explorer_item_directory_destination
              else:
                return ""
                
        def nextsync_show_sync_buttons_based_on_fileexplorer_content_selection():
            
            if self.left_file_nextsync_explorer_selection_full_filename_path != "":
                selected_explorer_item_directory_destination = nextsync_get_fileexplorer_root_selection()
                if selected_explorer_item_directory_destination == "":
                    return
                
                # first hide all buttons
                self.nextsync_button_create_syncignore.setVisible(False)
                self.nextsync_button_delete_syncignore.setVisible(False)
                self.nextsync_button_delete_syncpointfile.setVisible(False)
                    
                if os.path.exists(selected_explorer_item_directory_destination + IGNOREFILE) and os.path.isfile(selected_explorer_item_directory_destination + IGNOREFILE):
                    # ignore file exists offer to delete it
                    self.nextsync_button_delete_syncignore.setVisible(True)
                else:
                    # ignore file does not exist offer to create it
                    self.nextsync_button_create_syncignore.setVisible(True)
                    
                if os.path.exists(selected_explorer_item_directory_destination + SYNCPOINT) and os.path.isfile(selected_explorer_item_directory_destination + SYNCPOINT):
                    # SYNCPOINT file exists offer to delete it
                    self.nextsync_button_delete_syncpointfile.setVisible(True)
             
                    
                
        def nextsync_create_sample_ignorefile(file):
            try:
                config_file = open(file, "w")
                config_array = [];   
                for cs in IGNOREFILE_DEFAULT_CONTENT:
                    config_array.append(cs + '\n') 

                config_file.writelines(config_array)
                config_file.close()            
            except Exception as e:
                add_nextsync_log_window("Failed creating :" + str(file) + " Exception:" + str(e))
                
        def nextsync_create_syncingore_button():
            nextsync_create_sample_ignorefile(nextsync_get_fileexplorer_root_selection() + IGNOREFILE)
            nextsync_show_sync_buttons_based_on_fileexplorer_content_selection()

        def nextsync_delete_syncingore_button():
            try:
                os.remove(nextsync_get_fileexplorer_root_selection() + IGNOREFILE)
            except Exception as e:
                add_nextsync_log_window("Failed deleting:" + str(nextsync_get_fileexplorer_root_selection() + IGNOREFILE) + " Exception:" + str(e))   
                
            nextsync_show_sync_buttons_based_on_fileexplorer_content_selection()
            
        def nextsync_delete_syncpoint_button():
            try:
                os.remove(nextsync_get_fileexplorer_root_selection() + SYNCPOINT)
            except Exception as e:
                add_nextsync_log_window("Failed deleting:" + str(nextsync_get_fileexplorer_root_selection() + SYNCPOINT) + " Exception:" + str(e))   
                
            nextsync_show_sync_buttons_based_on_fileexplorer_content_selection()
        
            
        def nextsync_synconce_checkbox_statechanged():
            if self.nextsync_synconce_checkbox.isChecked():
                configuration_dictionary[SETTING_NEXTSYNC_SYNCONCE] = "true"
            else:
                configuration_dictionary[SETTING_NEXTSYNC_SYNCONCE] = "false"
                
            save_configuration_file()

        def nextsync_alwayssync_checkbox_statechanged():
            if self.nextsync_alwayssync_checkbox.isChecked():
                configuration_dictionary[SETTING_NEXTSYNC_ALWAYSSYNC] = "true"
            else:
                configuration_dictionary[SETTING_NEXTSYNC_ALWAYSSYNC] = "false"
                
            save_configuration_file()
            
        def nextsync_slowtransfer_checkbox_statechanged():
            if self.nextsync_slowtransfer_checkbox.isChecked():
                configuration_dictionary[SETTING_NEXTSYNC_SLOWTRANSFER] = "true"
                MAX_PAYLOAD = 256
            else:
                configuration_dictionary[SETTING_NEXTSYNC_SLOWTRANSFER] = "false"
                MAX_PAYLOAD = 1024
                
            save_configuration_file()               

        def nextsync_on_treeview_clicked():
            
            nextsync_hide_start_cancel_buttons()
            self.nextsync_prepare_server.setVisible(True)
            
            for ix in self.nextsync_treeview.selectedIndexes():
                if self.nextsync_model.fileName(ix) == "..":
                    self.left_file_nextsync_explorer_selection_file_name = ""
                    self.left_file_nextsync_explorer_selection_full_filename_path = self.nextsync_model.filePath(ix)
                    
                    splitted_filepath = self.left_file_nextsync_explorer_selection_full_filename_path.split('/')
                    selected_explorer_item_directory_destination = ""
                    for file_dest_token in range (0, len(splitted_filepath)-2):
                        selected_explorer_item_directory_destination += splitted_filepath[file_dest_token] + "/"
                        
                    self.nextsync_treeview.setRootIndex(self.nextsync_model.index(selected_explorer_item_directory_destination,0))
                    set_treeview_properties()
                    self.nextsync_treeview.show()
                    
                    self.nextsync_file_explorer_path.setText(selected_explorer_item_directory_destination)
                    
                    configuration_dictionary[SETTING_NEXTSYNC_EXPLORERPATH] = selected_explorer_item_directory_destination
                    save_configuration_file()
                    
                    nextsync_show_sync_buttons_based_on_fileexplorer_content_selection()
                    break
                
                else:
                    
                    self.left_file_nextsync_explorer_selection_file_name = self.nextsync_model.fileName(ix)
                    self.left_file_nextsync_explorer_selection_full_filename_path = self.nextsync_model.filePath(ix)
                    if platform.system() != "Windows":
                        self.left_file_nextsync_explorer_selection_full_filename_path.replace("\\", '/')                
                
                    self.nextsync_file_explorer_path.setText(self.left_file_nextsync_explorer_selection_full_filename_path)
                    configuration_dictionary[SETTING_NEXTSYNC_EXPLORERPATH] = self.left_file_nextsync_explorer_selection_full_filename_path
                    save_configuration_file()
                    
                    nextsync_show_sync_buttons_based_on_fileexplorer_content_selection()
                    break
                
        def image_explorer_selection_changed():
            
            global right_disk_image_explorer_content
            
            if len(right_disk_image_explorer_content) !=0: # check that we have an image content first
                right_disk_image_selected_files.clear()
                for idx in self.TableWidgetImage.selectionModel().selectedIndexes():
                    row_number = idx.row()
                    column_number = idx.column()
                    right_disk_image_selected_files.append(right_disk_image_explorer_content[row_number][0])
        
        def transfert_content_from_image_to_disk():
            
            global right_disk_image_explorer_content
            
            if len(right_disk_image_explorer_content) !=0: # check that we have an image content first
                
                set_all_buttons_disabled()
                        
                selected_explorer_item_directory_destination = ""

                if len(self.left_file_explorer_selection_full_filename_path) !=0:
                    splitted_filepath = self.left_file_explorer_selection_full_filename_path.split('/')
                    dest_file_content = splitted_filepath[len(splitted_filepath)-1]
                    # last directory should not containt a dot (that indicates it may be a file and we only want to copy to directories)
                    if not os.path.isdir(self.left_file_explorer_selection_full_filename_path):
                    # if '.' in dest_file_content:
                        for file_dest_token in range (0, len(splitted_filepath)-1):
                            selected_explorer_item_directory_destination += splitted_filepath[file_dest_token] + "/"
                    else:
                        selected_explorer_item_directory_destination = self.left_file_explorer_selection_full_filename_path
                else:
                    return
            
                directory_navigation = ""
                if platform.system() == "Windows":
                # Windows...
                    selected_explorer_item_directory_destination = selected_explorer_item_directory_destination.replace("/", "\\")
                    directory_navigation = "\\"
                else:
                    directory_navigation = "/"

            
                if len(right_disk_image_selected_files) !=0:
                    for f in right_disk_image_selected_files:
                        source = str(generate_disk_file_path() + "/" + f)
                        source = source.replace("//","/") # replace double slashes on root
                        #source = source.replace('"',"")
                        if not is_directory(self.right_disk_image_path, source):
                            if '"' not in source:
                                source = '"' + source + '"'
                                
                            hdfmonkeyexecresult = execute_hdf_monkey("get", self.right_disk_image_path, source + ' "' + selected_explorer_item_directory_destination + directory_navigation + f + '"')
                        else:
                            # create the directory
                            if platform.system() == "Windows": 
                                
                                try:
                                    os.makedirs(selected_explorer_item_directory_destination + '\\'+ f)
                                except FileExistsError:
                                    pass
                                except Exception as ex:
                                    add_main_log_window("Failed creating directory: " + '"' + selected_explorer_item_directory_destination + '\\'+ f + '" - ' + str(ex) )   
                                    
                            else:
                                
                                try:
                                    os.makedirs(selected_explorer_item_directory_destination + '/'+ f)
                                except FileExistsError:
                                    pass
                                except:
                                    add_main_log_window("Failed creating directory: " + '"' + selected_explorer_item_directory_destination + '/'+ f + '"' ) 
                            
                            get_directory_content(self.right_disk_image_path, str(generate_disk_file_path()), selected_explorer_item_directory_destination, f)

                set_all_buttons_enabled()
                
            else:
                add_main_log_window("Please load an image file first !")
                
        def transfert_content_from_disk_to_image():
            
            global right_disk_image_explorer_content
            
            if len(right_disk_image_explorer_content) !=0: # check that we have an image content first
                
                set_all_buttons_disabled()

                dest_file_path = generate_disk_file_path() + "/" + self.left_file_explorer_selection_file_name
                dest_file_path = dest_file_path.replace('//', '/') # if on root dirctory we get double slashes
                
                if platform.system() == "Windows":
                    self.left_file_explorer_selection_full_filename_path = self.left_file_explorer_selection_full_filename_path.replace("/","\\")
                    
                try:
                    # try to upload the file
                    hdfmonkeyexecresult = execute_hdf_monkey("put", self.right_disk_image_path, self.left_file_explorer_selection_full_filename_path + " " + dest_file_path)
                except:
                    add_main_log_window("Failed uploading to image: " + str(self.right_disk_image_path) + " file: " + self.left_file_explorer_selection_full_filename_path + " " + str(dest_file_path))
                
                # refresh image explorer view after the upload
                hdfmonkeyexecresult = execute_hdf_monkey("ls", self.right_disk_image_path, generate_disk_file_path())
                
                if hdfmonkeyexecresult.returncode == 0:
                    command_execution = hdfmonkeyexecresult.stdout
                    update_disk_manager_widget_table(command_execution)
                else:
                    add_main_log_window("Failed loading image :" + self.right_disk_image_path + "  - hdfmonkey result code: " + str(hdfmonkeyexecresult.returncode) )  
                    
                set_all_buttons_enabled()
                
            else:
                add_main_log_window("Please load an image first!")  
        
        def generate_disk_file_path():
            result_path = "/"
            row = 1
            for i in right_disk_image_explorer_path:
                result_path += right_disk_image_explorer_path[row-1]
                if len(right_disk_image_explorer_path) != row:
                    result_path += "/"
                row +=1
            return result_path

        def disk_image_explorer_item_double_clicked():
            
            global right_disk_image_explorer_content
            
            if len(right_disk_image_explorer_content) !=0: # check that we have an image content first
                
                set_all_buttons_disabled()

                # Reset all buttons such as Create directory or Delete files if the user suddely tries to navigate instead
                if self.button_confirm_deletion.isVisible() or self.button_create_directory.isVisible():                    
                    button_cancel_deletion()
                    image_newfolder_cancel()
                    

                row_number = 0
                column_number = 0
                for idx in self.TableWidgetImage.selectionModel().selectedIndexes():
                    row_number = idx.row()
                    column_number = idx.column()
                    
                # If user picked to go one directory level up
                if row_number == 0 and right_disk_image_explorer_content[row_number][0] == UP_DIRECTORY and right_disk_image_explorer_content[row_number][1] == "":
                    right_disk_image_explorer_path.pop()
                    hdfmonkeyexecresult = execute_hdf_monkey("ls", self.right_disk_image_path, generate_disk_file_path())
                
                    if hdfmonkeyexecresult.returncode == 0:
                        command_execution = hdfmonkeyexecresult.stdout
                        self.diskimageexplorerlabelpath.setText(generate_disk_file_path().replace('//', '/'))
                        update_disk_manager_widget_table(command_execution)
                        set_all_buttons_enabled()
                        return
            
                if right_disk_image_explorer_content[row_number][1] == 'DIR':
                    right_disk_image_explorer_path.append(right_disk_image_explorer_content[row_number][0])
                    list_source = generate_disk_file_path()
                    
                    if '"' not in list_source:
                        list_source = '"' + list_source + '"'
                    
                    hdfmonkeyexecresult = execute_hdf_monkey("ls", self.right_disk_image_path, list_source )
                
                    if hdfmonkeyexecresult.returncode == 0:
                        command_execution = hdfmonkeyexecresult.stdout
                        update_disk_manager_widget_table(command_execution)
                        self.diskimageexplorerlabelpath.setText(generate_disk_file_path().replace('//', '/'))
                        
                set_all_buttons_enabled()
                
            else:
                add_main_log_window("Please load an image file first !")
                
        def update_disk_manager_widget_table(command_execution_content):

            global right_disk_image_explorer_content
            
            results_lines = command_execution_content.splitlines()
            
            self.TableWidgetImage.clear()
            set_table_image_properties()
            
            self.TableWidgetImage.setRowCount(0)
            self.TableWidgetImage.setRowCount(len(results_lines)+1)
            set_table_image_properties()
            self.TableWidgetImage.verticalHeader().setVisible(False)
            
            row = 0
            
            right_disk_image_explorer_content.clear()
            
            # If we are not at the root add "[Up Directory..]" in order that the user can go back up
            if len(right_disk_image_explorer_path)!=0:

                newItemUpDirectory = QTableWidgetItem(UP_DIRECTORY)
                newItemUpDirectory.setForeground(FONT_RED)
                newItemEmpty1 = QTableWidgetItem("")
                newItemEmpty2 = QTableWidgetItem("")
                newItemUpDirectory.setFlags(newItemUpDirectory.flags() & ~Qt.ItemIsEditable) # make non editable
                newItemEmpty1.setFlags(newItemEmpty1.flags() & ~Qt.ItemIsEditable) # make non editable
                newItemEmpty1.setFlags(~Qt.ItemIsEnabled) # make non editable
                newItemEmpty2.setFlags(newItemEmpty2.flags() & ~Qt.ItemIsEditable) # make non editable
                newItemEmpty2.setFlags(~Qt.ItemIsEnabled)
                self.TableWidgetImage.setItem(row, 0, newItemUpDirectory)                    
                self.TableWidgetImage.setItem(row, 1, newItemEmpty1)
                self.TableWidgetImage.setItem(row, 2, newItemEmpty2) 
                

                right_disk_image_explorer_content.append((UP_DIRECTORY, ""))
                row += 1

            
            self.image_explorer_item_list.clear()
            
            for dirvalues in results_lines:
                
                directory_result_table = str.split(str(dirvalues), '\\t')
                file_type = directory_result_table[0]
                file_name = directory_result_table[1].rstrip("'")
                file_name = file_name.replace('"', '')

                newItemName = QTableWidgetItem(str(file_name))
                
                if is_filetype_a_directory(file_type):
                    file_type = "DIR"
                    newItemFSName = QTableWidgetItem(str(file_type))
                    newItemEmptyDir = QTableWidgetItem("")
                    
                    newItemFSName.setFlags(newItemFSName.flags() & ~Qt.ItemIsEditable) # make non editable
                    newItemName.setForeground(FONT_BLUE)
                    newItemName.setFlags(newItemName.flags() & ~Qt.ItemIsEditable) # make non editable
                    newItemFSName.setForeground(FONT_BLUE)
                    newItemEmptyDir.setFlags(newItemEmptyDir.flags() & ~Qt.ItemIsEditable) # make non editable
                    
                    newItemFSName.setFlags(~Qt.ItemIsEnabled)
                    newItemEmptyDir.setFlags(~Qt.ItemIsEnabled)

                    self.TableWidgetImage.setItem(row, 0, newItemName)                    
                    self.TableWidgetImage.setItem(row, 1, newItemFSName)
                    self.TableWidgetImage.setItem(row, 2, newItemEmptyDir)
                    
                    right_disk_image_explorer_content.append((file_name, "DIR"))
                    

                else:
                    if not is_filetype_a_directory(file_type):
                        try:
                            file_size = str(str.split(file_type,"'")[1])
                        except:
                            file_size = "0"
                    
                    newItemFS = QTableWidgetItem(file_size)
                    
                    if '.' in file_name:
                        newItemExt = QTableWidgetItem(str.split(file_name, '.')[1])
                    else:
                        newItemExt = QTableWidgetItem("")
                        
                    newItemFS.setForeground(FONT_GREEN)
                    newItemName.setForeground(FONT_GREEN)
                    newItemExt.setForeground(FONT_GREEN)
                    
                    newItemFS.setFlags(~Qt.ItemIsEnabled)
                    newItemExt.setFlags(~Qt.ItemIsEnabled)                    
                    

                    newItemFS.setFlags(newItemFS.flags() & ~Qt.ItemIsEditable) # make non editable
                    newItemExt.setFlags(newItemExt.flags() & ~Qt.ItemIsEditable) # make non editable
                    newItemName.setFlags(newItemName.flags() & ~Qt.ItemIsEditable) # make non editable

                    self.TableWidgetImage.setItem(row, 0, newItemName)
                    self.TableWidgetImage.setItem(row, 1, newItemExt)
                    self.TableWidgetImage.setItem(row, 2, newItemFS)
                    

                    
                    if '.' in file_name:
                        right_disk_image_explorer_content.append((file_name, str.split(file_name, '.')[1]))
                    else:
                        right_disk_image_explorer_content.append((file_name, ""))
                        
                    
                self.image_explorer_item_list.addItem (file_name)

                row += 1


        def update_syncpoint(path_to_content, knownfiles):
            with open(path_to_content + SYNCPOINT, 'w') as f:
                for x in knownfiles:
                    f.write(f"{x}\n")

        def agecheck(path_to_content, f):
            if not os.path.isfile(path_to_content + SYNCPOINT):
                return False
            ptime = os.path.getmtime(path_to_content + SYNCPOINT)
            mtime = os.path.getmtime(f)
            if mtime > ptime:
                return False
            return True

        def getFileList(path_to_content):    
            knownfiles = []
            if os.path.isfile(path_to_content + SYNCPOINT):
                with open(path_to_content + SYNCPOINT) as f:
                    knownfiles = f.read().splitlines()
            ignorelist = []
            if os.path.isfile(path_to_content + IGNOREFILE):
                with open(path_to_content + IGNOREFILE) as f:
                    ignorelist = f.read().splitlines()
            r = []
            gf = glob.glob(path_to_content + "**", recursive=True)
            for g in gf:
                if os.path.isfile(g) and os.path.exists(g):
                    ignored = False
                    for i in ignorelist:
                        if fnmatch.fnmatch(g, i):
                            ignored = True
                    if not self.nextsync_alwayssync_checkbox.isChecked():
                        if g in knownfiles:
                            if agecheck(path_to_content, g):
                                ignored = True
                    if not ignored:
                        stats = os.stat(g)
                        r.append([g, stats.st_size])
            return r

        def timestamp():
            return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        def sendpacket(conn, payload, packetno):
            checksum0 = 0 # random.choice([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1]) # 5%
            checksum1 = 0
            # packetno -= random.choice([0]*99+[1]) # 1%
            for x in payload:
                checksum0 = (checksum0 ^ x) & 0xff
                checksum1 = (checksum1 + checksum0) & 0xff
            packet = ((len(payload)+5).to_bytes(2, byteorder="big")
                + payload
                + (checksum0 & 0xff).to_bytes(1, byteorder="big")
                + (checksum1 & 0xff).to_bytes(1, byteorder="big")
                + (packetno & 0xff).to_bytes(1, byteorder="big"))
            conn.sendall(packet)
            
            if PY_HDFM_GOOEY_VERBOSE_LOG_MODE:
                add_nextsync_log_window (str(timestamp()) + " | Packet sent: " + str(len(packet)) + " bytes, payload: " + str(len(payload)) + " bytes, checksums: " + str(checksum0) + ", " + str(checksum1) + ", packetno: " + str(packetno & 0xff) )
          
        def nextsync_warnings():
            add_nextsync_log_window ("")

            selected_nextsync_explorer_sync_root_directory = ""
            
            if len(self.left_file_nextsync_explorer_selection_full_filename_path) !=0:
                splitted_filepath = self.left_file_nextsync_explorer_selection_full_filename_path.split('/')
                if not os.path.isdir(self.left_file_nextsync_explorer_selection_full_filename_path):
                # if '.' in dest_file_content:
                    for file_dest_token in range (0, len(splitted_filepath)-1):
                        selected_nextsync_explorer_sync_root_directory += splitted_filepath[file_dest_token] + "/"
                else:
                    selected_nextsync_explorer_sync_root_directory = self.left_file_nextsync_explorer_selection_full_filename_path + "/"
                        
            add_nextsync_log_window ("Using " + selected_nextsync_explorer_sync_root_directory + " as sync root")
            
            if not os.path.isfile(selected_nextsync_explorer_sync_root_directory + IGNOREFILE):
                add_nextsync_log_window ("Warning! Ignore file " + IGNOREFILE + " not found in directory. All files will be synced, possibly including this file.")
            if not os.path.isfile(selected_nextsync_explorer_sync_root_directory + SYNCPOINT):
                add_nextsync_log_window ("Sync point file " + SYNCPOINT + " not found, syncing all files regardless of timestamp.")
            initial = getFileList(selected_nextsync_explorer_sync_root_directory)
            total = 0
            for x in initial:
                total += x[1]
            severity = ""
            if len(initial) < 10 and total < 100000:
                severity ="Note"
            elif len(initial) < 100 and total < 1000000:
                severity = "Warning"
            else:
                severity = "WARNING"
            add_nextsync_log_window (severity + ": Ready to sync " + str(len(initial)) +" files, " + str(total/1024) +" kilobytes.")
            add_nextsync_log_window ("")
            
            
            nextsync_show_start_cancel_buttons()
            self.nextsync_prepare_server.setVisible(False)
            
        def nextsync_show_ip_info():
            add_nextsync_log_window ("------------------------------------------", False)
            add_nextsync_log_window ("NextSync server, protocol version: " + VERSION, False)
            add_nextsync_log_window ("", False)
            hostinfo = socket.gethostbyname_ex(socket.gethostname())    
            add_nextsync_log_window ("Running on host:\n    " + str(hostinfo[0]) , False)
            if hostinfo[1] != []:
                add_nextsync_log_window ("Aliases:", False)
                for x in hostinfo[1]:
                    add_nextsync_log_window ("    " + str(x), False)
            if hostinfo[2] != []:
                add_nextsync_log_window ("IP addresses:", False)
                for x in hostinfo[2]:
                    add_nextsync_log_window ("    " + str(x), False)

            # If we're unsure of the ip, try getting it via internet connection
            if len(hostinfo[2]) > 1 or "127" in hostinfo[2][0]:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                    s.connect(("8.8.8.8", 80)) # ping google dns
                    add_nextsync_log_window ("Primary IP:\n    " + str(s.getsockname()[0]), False)                   
                    
        def nextsync_cancel_server_job():
            nextsync_hide_start_cancel_buttons()
            self.nextsync_prepare_server.setVisible(True)
            
        def nextsync_do_server_job(progress_callback):

            selected_nextsync_explorer_sync_root_directory = ""
            self.nextsync_progressbar.setValue(0)
            self.nextsync_progressbar.setVisible(True)

            # hide all buttons
            self.nextsync_button_create_syncignore.setVisible(False)
            self.nextsync_button_delete_syncignore.setVisible(False)
            self.nextsync_button_delete_syncpointfile.setVisible(False)            
            
            
            
            hostinfo = socket.gethostbyname_ex(socket.gethostname())    
            add_nextsync_log_window ("Running on host:\n    " + str(hostinfo[0]) , False)
            if hostinfo[1] != []:
                add_nextsync_log_window ("Aliases:", False)
                for x in hostinfo[1]:
                    add_nextsync_log_window ("    " + str(x), False)
            if hostinfo[2] != []:
                add_nextsync_log_window ("IP addresses:", False)
                for x in hostinfo[2]:
                    add_nextsync_log_window ("    " + str(x), False)

            # If we're unsure of the ip, try getting it via internet connection
            if len(hostinfo[2]) > 1 or "127" in hostinfo[2][0]:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                    s.connect(("8.8.8.8", 80)) # ping google dns
                    add_nextsync_log_window ("Primary IP:\n    " + str(s.getsockname()[0]), False)              
            
            if len(self.left_file_nextsync_explorer_selection_full_filename_path) !=0:
                splitted_filepath = self.left_file_nextsync_explorer_selection_full_filename_path.split('/')
                if not os.path.isdir(self.left_file_nextsync_explorer_selection_full_filename_path):
                # if '.' in dest_file_content:
                    for file_dest_token in range (0, len(splitted_filepath)-1):
                        selected_nextsync_explorer_sync_root_directory += splitted_filepath[file_dest_token] + "/"
                else:
                    selected_nextsync_explorer_sync_root_directory = self.left_file_nextsync_explorer_selection_full_filename_path + "/"           
    
            working = True
            while working:
                add_nextsync_log_window (str(timestamp()) +  " | NextSync listening to port " + str(PORT))
                add_nextsync_log_window (str(timestamp()) +  " | Now start run .sync command on your Next!" )
                totalbytes = 0
                payloadbytes = 0
                starttime = 0
                retries = 0
                packets = 0
                restarts = 0
                gee = 0        
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(("", PORT))
                    s.listen()
                    conn, addr = s.accept()
                    # Make sure *nixes close the socket when we ask it to.
                    conn.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack('ii', 1, 0))
                    f = getFileList(selected_nextsync_explorer_sync_root_directory)
                    add_nextsync_log_window (str(timestamp()) + " | Sync file list has " + str(len(f)) + " files.")
                    knownfiles = []
                    if os.path.isfile(selected_nextsync_explorer_sync_root_directory + SYNCPOINT):
                        with open(selected_nextsync_explorer_sync_root_directory + SYNCPOINT) as kf:
                            knownfiles = kf.read().splitlines()
                    fn = 0
                    filedata = b''
                    packet = b''
                    fileofs = 0
                    totalbytes = 0
                    packetno = 0
                    starttime = time.time()
                    endtime = starttime
                    with conn:                
                        add_nextsync_log_window (str(timestamp()) + " | Connected by " + str(addr[0]) +" port " + str(addr[1]))
                        talking = True                
                        while talking:
                            data = conn.recv(1024)
                            if not data:
                                break
                            decoded = data.decode()
                            if PY_HDFM_GOOEY_VERBOSE_LOG_MODE:
                                add_nextsync_log_window (str(timestamp()) + " | Data received: " + str(decoded) + ", " + str(len(decoded))+ " bytes")
                            if data == b"Sync3":
                                add_nextsync_log_window (str(timestamp()) + " | Sending " + VERSION3)
                                packet = str.encode(VERSION3)
                                sendpacket(conn, packet, 0)
                                packets += 1
                                totalbytes += len(packet)
                            elif data == b"Next" or data == b"Neex": # Really common mistransmit. Probably uart-esp..
                                if data == b"Neex":
                                    gee += 1
                                if fn >= len(f):
                                    add_nextsync_log_window (str(timestamp()) + " | Nothing (more) to sync")
                                    packet = b'\x00\x00\x00\x00\x00' # end of.
                                    packets += 1
                                    sendpacket(conn, packet, 0)
                                    totalbytes += len(packet)
                                    # Sync complete, set sync point
                                    update_syncpoint(selected_nextsync_explorer_sync_root_directory, knownfiles)
                                else:
                                    specfn = f[fn][0].replace('\\','/')
                                    add_nextsync_log_window (str(timestamp()) + " | File: " +str(f[fn][0]) + " (as " +str(specfn)+") length: " + str(f[fn][1]) + " bytes")
                                    packet = (f[fn][1]).to_bytes(4, byteorder="big") + (len(specfn)).to_bytes(1, byteorder="big") + (specfn).encode()
                                    packets += 1
                                    sendpacket(conn, packet, 0)
                                    totalbytes += len(packet)
                                    with open(f[fn][0], 'rb') as srcfile:
                                        filedata = srcfile.read()
                                    payloadbytes += len(filedata)
                                    if f[fn][0] not in knownfiles:
                                        knownfiles.append(f[fn][0])
                                    fileofs = 0
                                    packetno = 0
                                    progress_callback.emit(fn*100/len(f)) # send progress update info to UI
                                    fn+=1
                            elif data == b"Get" or data == b"Gee": # Really common mistransmit. Probably uart-esp..
                                bytecount = MAX_PAYLOAD
                                if bytecount + fileofs > len(filedata):
                                    bytecount = len(filedata) - fileofs                        
                                packet = filedata[fileofs:fileofs+bytecount]
                                if PY_HDFM_GOOEY_VERBOSE_LOG_MODE:
                                    if len(filedata) != 0:
                                        add_nextsync_log_window (str(timestamp()) + " | Sending " + str(bytecount) + " bytes, offset " + str(fileofs/len(filedata)))
                                    else:
                                        add_nextsync_log_window (str(timestamp()) + " | Sending " + str(bytecount) + " bytes 0 bytes")
                                    
                                packets += 1
                                sendpacket(conn, packet, packetno)
                                totalbytes += len(packet)
                                fileofs += bytecount                        
                                packetno += 1
                                if data == b"Gee":
                                    gee += 1
                            elif data == b"Retry":
                                retries += 1
                                add_nextsync_log_window (str(timestamp()) + " | Resending")
                                sendpacket(conn, packet, packetno - 1)
                            elif data == b"Restart":
                                restarts += 1
                                add_nextsync_log_window (str(timestamp()) + " | Restarting")
                                fileofs = 0
                                packetno = 0
                                sendpacket(conn, str.encode("Back"), 0)
                            elif data == b"Bye":
                                sendpacket(conn, str.encode("Later"), 0)
                                add_nextsync_log_window (str(timestamp()) + " | Closing connection")
                                talking = False
                            elif data == b"Sync2" or data == b"Sync1" or data == b"Sync":
                                packet = str.encode("Nextsync 0.8 or later needed")
                                add_nextsync_log_window (str(timestamp()) + " | Old version requested")
                                sendpacket(conn, packet, 0)
                                packets += 1
                                totalbytes += len(packet)
                            else:
                                add_nextsync_log_window (str(timestamp()) + "  | Unknown command")
                                sendpacket(conn, str.encode("Error"), 0)
                        endtime = time.time()
                deltatime = endtime - starttime
                add_nextsync_log_window (str(timestamp()) + " | " + str(totalbytes/1024) + " kilobytes transferred in " + str(deltatime) + " seconds, " + str((totalbytes/deltatime)/1024) + " kBps")
                
                #TODO set content propoerly                
                add_nextsync_log_window (str(timestamp()) + " | " + str(payloadbytes/1024) + " kilobytes payload, " + str((payloadbytes/deltatime)/1024) + " kBps effective speed")
                add_nextsync_log_window (str(timestamp()) + " | packets: " + str(packets) + ", retries: " + str(retries) + ", restarts: " + str(restarts) + ", gee: " + str(gee))
                add_nextsync_log_window (str(timestamp()) + " | Disconnected")
                add_nextsync_log_window ("")                 
                if self.nextsync_synconce_checkbox.isChecked():
                    working = False
                    
            nextsync_hide_start_cancel_buttons()
            self.nextsync_prepare_server.setVisible(True)
            self.nextsync_progressbar.setVisible(False)


            
        # ------------------------------------------
        # main program starts here
        # ------------------------------------------

        # NextSync specific variables
        # If you want to be really safe (but transfer slower), use this:
        #MAX_PAYLOAD = 256

        # The next uart has a buffer of 512 bytes; sending packets of 256 bytes will always
        # fit and there won't be any buffer overruns. However, it's much slower.

        #  Build Main UI

        self.setWindowTitle("Py-Hdfm-Gooey " + PY_HDFM_GOOEY_VERSION)
        self.setFixedSize(QSize(PY_HDFM_GOOEY_UI_WIDTH, PY_HDFM_GOOEY_UI_HEIGTH))
        
        # Initialize configuration dictonnary
        for c in CONFIG_FILE_SETTINGS:
            configuration_dictionary[c] = ""

        # Init UI forms

        self.setWindowIcon(QIcon(PY_HDFM_GOOEY_ICON_IMAGE_FILE))

        self.hdfm_gooey_form = QFormLayout()
        self.nextsync_form = QFormLayout()
        
        # hdfm_gooey horizontals
        self.horizontal1 = QHBoxLayout()
        self.horizontal2 = QHBoxLayout()
        self.horizontal3 = QHBoxLayout()
        self.horizontal4 = QHBoxLayout()
        self.horizontal5 = QHBoxLayout()
        self.horizontal6 = QHBoxLayout()
        
        # nextsync horizontals
        
        self.horizontal10 = QHBoxLayout()
        self.horizontal11 = QHBoxLayout()
        self.horizontal12 = QHBoxLayout()
        self.horizontal13 = QHBoxLayout()
        self.horizontal14 = QHBoxLayout()
        self.horizontal15 = QHBoxLayout()
        self.horizontal16 = QHBoxLayout()
        

        self.imageinput = QLineEdit()
        
        self.imageinput.setText ('')
        self.selectimage = QPushButton("ToDisk", self)
        self.selectimage.setText("Select Disk Image")
        self.selectimage.toolTip = "Select a disk image to be loaded."
        self.selectimage.clicked.connect(select_image)
        
        self.horizontal1.addWidget(self.imageinput)
        self.horizontal1.addWidget(self.selectimage)
        
        self.hdfm_gooey_form.addRow(self.horizontal1)

        self.hdfm_gooey_diskdrive = QComboBox()
        
        available_drives = []
        
        if platform.system() == "Windows":

            available_drives = ['%s:' % d for d in string.ascii_uppercase if os.path.exists('%s:' % d)]
        
            for letter in available_drives:
                 self.hdfm_gooey_diskdrive.addItem(letter)            
        
            self.hdfm_gooey_diskdrive.show()

            self.horizontal2.addWidget(self.hdfm_gooey_diskdrive)
            self.hdfm_gooey_diskdrive.activated.connect(update_root_drive)
        else:
            available_drives.append('/')
            self.hdfm_gooey_diskdrive.setVisible(False)
        
        self.filterlabel = QLabel()
        self.filterlabel.setText(FILTER_LABEL_TEXT)

        
        self.horizontal2.addWidget(self.filterlabel)
        
        self.filtertext = QLineEdit()
        self.filtertext.returnPressed.connect(apply_file_extension_filter)
        self.filtertext.setMinimumWidth(FILTER_TEXT_WIDTH)
        self.filtertext.setMaximumWidth(FILTER_TEXT_WIDTH)
        
        self.horizontal2.addWidget(self.filtertext)

        self.diskimageexplorerlabel = QLabel()
        self.diskimageexplorerlabel.setText("                Disk Image Explorer: ")
        
        self.horizontal2.addWidget(self.diskimageexplorerlabel)

        self.diskimageexplorerlabelpath = QLabel()
        self.diskimageexplorerlabelpath.setText("")
        
        self.diskimageexplorerlabelpath.setMinimumWidth(400)
        self.diskimageexplorerlabelpath.setMaximumWidth(400)
        
        self.horizontal2.addWidget(self.diskimageexplorerlabelpath)

        self.hdfm_gooey_form.addRow(self.horizontal2)

        self.model = QFileSystemModel()

        self.model.setRootPath('/')
        self.model.setFilter(~QDir.NoDotAndDotDot | QDir.NoDot)

        self.treeview = QTreeView()
        self.treeview.setModel(self.model)
        self.proxy_model = QSortFilterProxyModel(recursiveFilteringEnabled = True, filterRole = QFileSystemModel.FileNameRole)
        self.proxy_model.setSourceModel(self.model)        
        self.treeview.setRootIndex(self.model.index(available_drives[0]))
        
        self.treeview.show()
        self.treeview.doubleClicked.connect(on_treeview_double_clicked)
        self.treeview.clicked.connect(on_treeview_clicked)

        self.centralbuttonscontainer = QWidget()
        self.centralbuttons = QVBoxLayout()
        
        self.button_to_disk = QPushButton("ToDisk", self)
        self.button_to_disk.setText("<<<")
        self.button_to_disk.setMaximumWidth(DISK_ARROWS_BUTTONS_SIZE)
        self.button_to_disk.clicked.connect(transfert_content_from_image_to_disk)
        
        self.button_to_image = QPushButton("ToImage", self)
        self.button_to_image.setText(">>>")
        self.button_to_image.setMaximumWidth(DISK_ARROWS_BUTTONS_SIZE)
        self.button_to_image.clicked.connect(transfert_content_from_disk_to_image)

        self.TableWidgetImage = QTableWidget(0, 3, self) # https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QTableWidget.html https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QListWidget.html
        set_table_image_properties()
        
        self.TableWidgetImage.doubleClicked.connect(disk_image_explorer_item_double_clicked)
        self.TableWidgetImage.itemSelectionChanged.connect(image_explorer_selection_changed)

        self.horizontal3.addWidget(self.treeview)
        
        self.centralbuttons.addWidget(self.button_to_image)
        self.centralbuttons.addWidget(self.button_to_disk)
        
        self.centralbuttons.setAlignment(Qt.AlignCenter)
        self.centralbuttonscontainer.setLayout(self.centralbuttons)
        self.horizontal3.addWidget(self.centralbuttonscontainer)
        self.horizontal3.addWidget(self.TableWidgetImage)

        self.hdfm_gooey_form.addRow(self.horizontal3)

        self.listWidgetLog = QListWidget(self)

        for l in INIT_LOG:
            add_main_log_window(l)
            
        self.listWidgetHelp = QListWidget(self)
        
        for l in INIT_HELP:
            add_help_content(l, False)

        
        self.listWidgetLog.setMinimumHeight(120)
        self.listWidgetLog.setMaximumHeight(120)
        self.listWidgetLog.setMinimumWidth(410)
        
        self.imageexplorerbuttonscontainer = QWidget()
        self.imageexplorerbuttons = QHBoxLayout()

        self.hiddenspacelabel1 = QLabel()
        self.hiddenspacelabel1.setText("      ")
        self.imageexplorerbuttons.addWidget(self.hiddenspacelabel1)
        
        self.button_new_folder = QPushButton("NewFolder", self)
        self.button_new_folder.setText("New Folder")
        self.button_new_folder.setMinimumWidth(IMAGE_BUTTONS_SIZE)
        self.button_new_folder.clicked.connect(image_newfolder)
        
        self.download_and_install_hdfmonkey_button = QPushButton("Download & install HDF Monkey", self)
        self.download_and_install_hdfmonkey_button.setText("Download and install HDF Monkey from speccy.org")
        self.download_and_install_hdfmonkey_button.setMinimumWidth(IMAGE_BUTTONS_SIZE)
        self.download_and_install_hdfmonkey_button.clicked.connect(download_and_install_hdflonkey)
        self.download_and_install_hdfmonkey_button.setVisible(False)
        
        self.hiddenspacelabel2 = QLabel()
        self.hiddenspacelabel2.setText("       ")
        self.imageexplorerbuttons.addWidget(self.hiddenspacelabel2)
        
        self.button_delete_files = QPushButton("DeleteFiles", self)
        self.button_delete_files.setText("Delete Files or Folder")
        self.button_delete_files.setMinimumWidth(IMAGE_BUTTONS_SIZE)
        self.button_delete_files.clicked.connect(delete_files_button_show_confirmation_buttons)
        
        self.button_cancel = QPushButton("Cancel", self)
        self.button_cancel.setText("Cancel")
        self.button_cancel.setMinimumWidth(IMAGE_BUTTONS_SIZE)
        self.button_cancel.setVisible(False)
        self.button_cancel.clicked.connect(button_cancel_deletion)
        
        self.button_confirm_deletion = QPushButton("Yes, confirm deletion", self)
        self.button_confirm_deletion.setText("Yes, confirm deletion")
        self.button_confirm_deletion.setMinimumWidth(IMAGE_BUTTONS_SIZE)
        self.button_confirm_deletion.setVisible(False)
        
        self.button_confirm_deletion.clicked.connect(button_confirm_directory_deletion)
        
        self.imageexplorerbuttons.addWidget(self.button_new_folder)
        self.imageexplorerbuttons.addWidget(self.button_delete_files)

        self.imageexplorerbuttons.addWidget(self.button_confirm_deletion)
        self.imageexplorerbuttons.addWidget(self.button_cancel)

        self.imageexplorerbuttons.addWidget(self.download_and_install_hdfmonkey_button)
       
        self.new_folder_input = QLineEdit()

        self.new_folder_input.setText ("NewDirName")
        tooltip_text = "Enter new directory name ("
        for not_allowed_chars in DIRECTORY_CREATION_NOT_ALLOWED_CHARACTERS:
            tooltip_text +=not_allowed_chars
        tooltip_text += " are not allowed): "
        
        self.new_folder_input.setToolTip(tooltip_text)
        self.new_folder_input.setMinimumWidth(150)
        self.new_folder_input.setMaximumWidth(150)

        self.button_create_directory = QPushButton("Create Directory", self)
        self.button_create_directory.setText("Create Directory")
        self.button_create_directory.setMinimumWidth(IMAGE_BUTTONS_SIZE/2)
        self.button_create_directory.clicked.connect(image_newfolder_create)
        
        self.button_create_directory_cancel = QPushButton("Cancel Directory", self)
        self.button_create_directory_cancel.setText("Cancel")
        self.button_create_directory_cancel.setMinimumWidth(IMAGE_BUTTONS_SIZE/2)
        self.button_create_directory_cancel.clicked.connect(image_newfolder_cancel)  
 
        self.imageexplorerbuttons.addWidget(self.new_folder_input)
        self.imageexplorerbuttons.addWidget(self.button_create_directory)
        self.imageexplorerbuttons.addWidget(self.button_create_directory_cancel)

        self.new_folder_input.setVisible(False)
        self.button_create_directory.setVisible(False)
        self.button_create_directory_cancel.setVisible(False)
        
        self.imageexplorerbuttons.setAlignment(Qt.AlignTop)
        
        self.imageexplorerbuttonscontainer.setLayout(self.imageexplorerbuttons)

        # Show Explorer selected Path
       
        self.file_explorer_path = QLabel()
        self.file_explorer_path.setText("-")
        
        self.horizontal4.addWidget(self.file_explorer_path)        

        self.hdfm_gooey_form.addRow(self.horizontal4)

        # Add Log Window
        self.horizontal5.addWidget(self.listWidgetLog)
        
        self.horizontal5.addWidget(self.imageexplorerbuttonscontainer)
        
        self.hdfm_gooey_form.addRow(self.horizontal5)
        
        # Add action buttons at the bottom
        
        self.button_start_cspect = QPushButton("LaunchCSpect", self)
        self.button_start_cspect.setText("Launch CSpect")
        self.button_start_cspect.clicked.connect(launch_cspect)
        self.horizontal6.addWidget(self.button_start_cspect)

        # Populate Screen Size Combo
        self.cspect_screensize = QComboBox()
        
        for sc in CSPECT_SCREEN_SIZES:
             self.cspect_screensize.addItem(sc[0])            

        self.cspect_screensize.show()
        self.cspect_screensize.currentIndexChanged.connect(set_cspect_screen_size)

        self.horizontal6.addWidget(self.cspect_screensize)
        
        # Populate Sound Combo
        self.cspect_sound = QComboBox()
        
        for ssound in CSPECT_SOUND:
             self.cspect_sound.addItem(ssound[0])            

        self.cspect_sound.show()
        self.cspect_sound.currentIndexChanged.connect(set_cspect_sound_on_off)

        self.horizontal6.addWidget(self.cspect_sound)

        # Populate vsync Combo
        self.cspect_vsync = QComboBox()
        
        for vs in CSPECT_SCREEN_SYNC:
             self.cspect_vsync.addItem(vs[0])            

        self.cspect_vsync.show()
        self.cspect_vsync.currentIndexChanged.connect(set_cspect_vsync_on_off)

        self.horizontal6.addWidget(self.cspect_vsync)
        
        # Populate Joystick Combo
        self.cspect_joystick = QComboBox()
        
        for jsc in CSPECT_JOYSTICK:
             self.cspect_joystick.addItem(jsc[0])            

        self.cspect_joystick.show()
        self.cspect_joystick.currentIndexChanged.connect(set_cspect_joystick_on_off)

        self.horizontal6.addWidget(self.cspect_joystick)

        # Populate frequency Combo
        self.cspect_frequency = QComboBox()
        
        for cf in CSPECT_FREQUENCY:
             self.cspect_frequency.addItem(cf[0])            

        self.cspect_frequency.show()
        self.cspect_frequency.currentIndexChanged.connect(set_cspect_display_frequency)

        self.horizontal6.addWidget(self.cspect_frequency)

        self.button_open_config_file = QPushButton("Open config file", self)
        self.button_open_config_file.setText("Open config file")
        self.button_open_config_file.clicked.connect(open_cspect_configuration_file)
        self.horizontal6.addWidget(self.button_open_config_file)

        self.hdfm_gooey_form.addRow(self.horizontal6)
        
        set_all_buttons_disabled()
        enable_image_selection()


        wid = QWidget()
        grid = QGridLayout(wid)
        wid.setLayout(grid)

        # setting the inner widget and layout
        grid_inner = QGridLayout()
        wid_inner = QWidget(wid)
        wid_inner.setLayout(grid_inner)

        # add the inner widget to the outer layout
        grid.addWidget(wid_inner)

        # add tab frame to widget
        wid_inner.tab = QTabWidget(wid_inner)
        grid_inner.addWidget(wid_inner.tab)

        hdfm_gooey_container = QWidget()
        hdfm_gooey_container.setLayout(self.hdfm_gooey_form)
        
        nextsync_container = QWidget()
        nextsync_container.setLayout(self.nextsync_form)

        self.nextsync_log_and_sync_buttons_container = QWidget()
        self.nextsync_container_log_and_sync_buttons = QVBoxLayout()
        
        self.nextsync_container_log_and_sync_buttons.setAlignment(Qt.AlignTop)
        self.nextsync_log_and_sync_buttons_container.setLayout(self.nextsync_container_log_and_sync_buttons)


        self.nextsync_fileexplorer_and_buttons_container = QWidget()
        self.nextsync_container_fileexplorer_and_buttons_buttons = QVBoxLayout()

        self.nextsync_container_fileexplorer_and_buttons_buttons.setAlignment(Qt.AlignTop)
        self.nextsync_fileexplorer_and_buttons_container.setLayout(self.nextsync_container_fileexplorer_and_buttons_buttons)     
        
        # Add Disk drive selection
        self.nextsync_diskdrive = QComboBox()
        
        if platform.system() == "Windows":

            available_drives = ['%s:' % d for d in string.ascii_uppercase if os.path.exists('%s:' % d)]
        
            for letter in available_drives:
                 self.nextsync_diskdrive.addItem(letter)            
        
            self.nextsync_diskdrive.show()

            self.horizontal10.addWidget(self.nextsync_diskdrive)
            self.nextsync_diskdrive.activated.connect(nextsync_update_root_drive)
        else:
            available_drives.append('/')
            self.nextsync_diskdrive.setVisible(False)
        
        
        # Add Filter
        self.nextsync_filterlabel = QLabel()
        self.nextsync_filterlabel.setText(FILTER_LABEL_TEXT)

        self.horizontal10.addWidget(self.nextsync_filterlabel)

        self.nextsync_filtertext = QLineEdit()
        self.nextsync_filtertext.returnPressed.connect(apply_file_extension_filter_nextsync)
        self.nextsync_filtertext.setMinimumWidth(FILTER_TEXT_WIDTH + 400)
        self.nextsync_filtertext.setMaximumWidth(FILTER_TEXT_WIDTH + 400)

        self.horizontal10.addWidget(self.nextsync_filtertext)

        
        self.nextsync_form.addRow(self.horizontal10)  
        
        self.nextsync_model = QFileSystemModel()

        self.nextsync_model.setRootPath('/')
        self.nextsync_model.setFilter(~QDir.NoDotAndDotDot | QDir.NoDot)

        self.nextsync_treeview = QTreeView()
        self.nextsync_treeview.setModel(self.nextsync_model)
        self.proxy_model = QSortFilterProxyModel(recursiveFilteringEnabled = True, filterRole = QFileSystemModel.FileNameRole)
        self.proxy_model.setSourceModel(self.nextsync_model)        
        self.nextsync_treeview.setRootIndex(self.nextsync_model.index(available_drives[0]))
        
        self.nextsync_treeview.show()

        self.nextsync_treeview.clicked.connect(nextsync_on_treeview_clicked)   
        
        set_treeview_properties()            
        
        self.nextsync_container_fileexplorer_and_buttons_buttons.addWidget(self.nextsync_treeview)

        # Show Explorer selected Path
       
        self.nextsync_file_explorer_path = QLabel()
        self.nextsync_file_explorer_path.setText("-")
        
        self.nextsync_container_fileexplorer_and_buttons_buttons.addWidget(self.nextsync_file_explorer_path)   


        self.horizontal12.addWidget(self.nextsync_fileexplorer_and_buttons_container)
        

        self.nextsync_button_create_syncignore = QPushButton("Create SyncIgnore File", self)
        self.nextsync_button_create_syncignore.setText("Create SyncIgnore File")
        self.nextsync_button_create_syncignore.clicked.connect(nextsync_create_syncingore_button) 
        self.nextsync_button_create_syncignore.setVisible(False)
        
        self.nextsync_container_fileexplorer_and_buttons_buttons.addWidget(self.nextsync_button_create_syncignore)

        self.nextsync_button_delete_syncignore = QPushButton("Delete SyncIgnore File", self)
        self.nextsync_button_delete_syncignore.setText("Delete SyncIgnore File")
        self.nextsync_button_delete_syncignore.clicked.connect(nextsync_delete_syncingore_button) 
        self.nextsync_button_delete_syncignore.setVisible(False)
        
        self.nextsync_container_fileexplorer_and_buttons_buttons.addWidget(self.nextsync_button_delete_syncignore)
        
        self.nextsync_button_delete_syncpointfile = QPushButton("Delete SyncPoint File", self)
        self.nextsync_button_delete_syncpointfile.setText("Delete SyncPoint File")
        self.nextsync_button_delete_syncpointfile.clicked.connect(nextsync_delete_syncpoint_button) 
        self.nextsync_button_delete_syncpointfile.setVisible(False)
        
        self.nextsync_container_fileexplorer_and_buttons_buttons.addWidget(self.nextsync_button_delete_syncpointfile)
        
        self.nextsync_form.addRow(self.horizontal12)
        
                                    
        # Add NextSync Log Window

        self.nextsync_log = QListWidget(self)
        self.nextsync_log.setMinimumHeight(NEXTSYNC_UI_HEIGTH)
        self.nextsync_log.setMaximumHeight(NEXTSYNC_UI_HEIGTH)
        
        self.nextsync_container_log_and_sync_buttons.addWidget(self.nextsync_log)
        

        self.nextsync_synconce_checkbox = QCheckBox("Sync once")
        self.nextsync_synconce_checkbox.setText("Sync once")
        #self.nextsync_synconce_checkbox.setChecked(True)
        self.nextsync_synconce_checkbox.stateChanged.connect(nextsync_synconce_checkbox_statechanged)
        self.nextsync_container_log_and_sync_buttons.addWidget(self.nextsync_synconce_checkbox)
        
        self.nextsync_alwayssync_checkbox = QCheckBox("Always Sync")
        self.nextsync_alwayssync_checkbox.setText("Always Sync")
        #self.nextsync_alwayssync_checkbox.setChecked(True)
        self.nextsync_alwayssync_checkbox.stateChanged.connect(nextsync_alwayssync_checkbox_statechanged)
        self.nextsync_container_log_and_sync_buttons.addWidget(self.nextsync_alwayssync_checkbox)


        self.nextsync_slowtransfer_checkbox = QCheckBox("Slow transfer")
        self.nextsync_slowtransfer_checkbox.setText("Slow transfer")
        #self.nextsync_alwayssync_checkbox.setChecked(True)
        self.nextsync_slowtransfer_checkbox.stateChanged.connect(nextsync_slowtransfer_checkbox_statechanged)
        self.nextsync_container_log_and_sync_buttons.addWidget(self.nextsync_slowtransfer_checkbox)
        
 
        self.nextsync_prepare_server = QPushButton("Prepare Server", self)
        self.nextsync_prepare_server.setText("Prepare NextSync server")
        self.nextsync_prepare_server.clicked.connect(nextsync_perform_checks_and_prepare_server_start)

        self.nextsync_container_log_and_sync_buttons.addWidget(self.nextsync_prepare_server)


        
        self.nextsync_start_server = QPushButton("Yes, start NextSync Server", self)
        self.nextsync_start_server.setText("Yes, start NextSync Server")
        self.nextsync_start_server.clicked.connect(nextsync_start_server)

        self.nextsync_cancel_server = QPushButton("Cancel NextSync Server", self)
        self.nextsync_cancel_server.setText("Cancel sync")
        self.nextsync_cancel_server.clicked.connect(nextsync_cancel_server_job)   

        
        self.nextsync_container_log_and_sync_buttons.addWidget(self.nextsync_start_server)
        self.nextsync_container_log_and_sync_buttons.addWidget(self.nextsync_cancel_server)
        


        
        self.horizontal12.addWidget(self.nextsync_log_and_sync_buttons_container)

        
        self.nextsync_form.addRow(self.horizontal14)
        
        nextsync_hide_start_cancel_buttons()
        
        self.nextsync_progressbar = QProgressBar()
        self.nextsync_progressbar.setGeometry(QRect(20, 10, 361, 23))
        self.nextsync_progressbar.setProperty("value", 0)
        self.nextsync_progressbar.setObjectName("progressBar")
        self.nextsync_progressbar.setVisible(False)
        
        self.horizontal15.addWidget(self.nextsync_progressbar)
        
        
        self.nextsync_form.addRow(self.horizontal15)
        
        self.setCentralWidget(wid_inner)
        

        # Create HDFM_Gooey Tab
        hdfm_gooey_tab = QWidget(wid_inner.tab)
        grid_tab = QGridLayout(hdfm_gooey_tab)
        grid_tab.addWidget(hdfm_gooey_container) # here use the form container
        hdfm_gooey_tab.setLayout(grid_tab)
        hdfm_gooey_tab.tab_name_private = PY_HDFM_GOOEY_TAB_TITLE_GOOEY
        wid_inner.tab.addTab(hdfm_gooey_tab, PY_HDFM_GOOEY_TAB_TITLE_GOOEY)
        
        # Create NextSync Tab
        hdfm_NextSync_tab = QWidget(wid_inner.tab)
        grid_tab_nextsync = QGridLayout(hdfm_NextSync_tab)
        grid_tab_nextsync.addWidget(nextsync_container) # here use the form container
        hdfm_NextSync_tab.setLayout(grid_tab_nextsync)
        hdfm_NextSync_tab.tab_name_private = PY_HDFM_GOOEY_TAB_TITLE_NEXTSYNC
        wid_inner.tab.addTab(hdfm_NextSync_tab, PY_HDFM_GOOEY_TAB_TITLE_NEXTSYNC)

         # Create Help Tab
        hdfm_Help_tab = QWidget(wid_inner.tab)
        grid_tab_Help = QGridLayout(hdfm_Help_tab)
        grid_tab_Help.addWidget(self.listWidgetHelp) # TODO as above use the form container of Help use the form container
        hdfm_Help_tab.setLayout(grid_tab_Help)
        wid_inner.tab.addTab(hdfm_Help_tab, "?")

        #  Start main logic

        load_configuration_file()
        
        if is_hdfmonkey_present():
            load_image()
        else:
            if platform.system() == "Windows":
                if show_hdf_monkey_download_and_install_buttons():
                    if is_hdfmonkey_present():
                        load_image()

        if len(right_disk_image_explorer_content) == 0:
            self.diskimageexplorerlabelpath.setText("Please load an image.")
        else:
            self.diskimageexplorerlabelpath.setText(generate_disk_file_path().replace('//', '/'))
        

        nextsync_show_ip_info()
        nextsync_show_sync_buttons_based_on_fileexplorer_content_selection()
        
        

        
        
app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()
