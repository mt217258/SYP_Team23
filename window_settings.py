'''
Author:             Matthew McLaughlin
Contact:            mt217258@dal.ca
Description:        Settings control for data viewer
TODO List:          
'''

#### LIBRARIES ####
# OFF THE SHELF #
from PyQt5 import QtWidgets, uic
import queue
import configparser

# CUSTOM #
from widget_settingSensor import WIDGET_settingSensor 
from PyQt5.Qt import QComboBox, QMessageBox, QSpinBox
#import WIDGET_settingSensor 

#### CLASSES ####
class WINDOW_settings(QtWidgets.QDialog):
    #### MAGIC METHODS ####
    def __init__(self, settings, q_settings, filepath, *args, **kwargs):
        super(WINDOW_settings, self).__init__(*args, **kwargs)
        uic.loadUi('ui_files/window_settings.ui', self)
        
        self.settings = settings #configParser object
        self.q_settings = q_settings
        self.filepath = filepath
        
        self.__linkActions()
        self.__linkWidgets()
        self.__initialize()
        #self.__buildWidget()
        
    #### MANGELED METHODS #### ("private" methods)
    def __linkActions(self):
        pass
      
    def __linkWidgets(self): #links widgest and updates from settings
        #buttons
        self.button_applyANDsave = self.findChild(QtWidgets.QPushButton, 'button_applyANDsave')
        self.button_applyANDsave.clicked.connect(self.__applyANDclose)
        
        self.button_close = self.findChild(QtWidgets.QPushButton, 'button_close')
        self.button_close.clicked.connect(self.__close)
        
        #settings
        self.sensor_L_EDA = self.findChild(WIDGET_settingSensor, 'L_EDA')
        self.sensor_L_EDA.setSettings("L_EDA", self.settings["L_EDA"]["MAC"])#, self.settings["L_EDA"]["sampleRate"])
        
        self.sensor_R_EDA = self.findChild(WIDGET_settingSensor, 'R_EDA')
        self.sensor_R_EDA.setSettings("R_EDA", self.settings["R_EDA"]["MAC"])#, self.settings["R_EDA"]["sampleRate"])
        
        self.sensor_L_MuscleBan = self.findChild(WIDGET_settingSensor, 'L_MuscleBan')
        self.sensor_L_MuscleBan.setSettings("L_MuscleBan", self.settings["L_MuscleBan"]["MAC"])#, self.settings["L_MuscleBan"]["sampleRate"])
        
        self.sensor_R_MuscleBan = self.findChild(WIDGET_settingSensor, 'R_MuscleBan')
        self.sensor_R_MuscleBan.setSettings("R_MuscleBan", self.settings["R_MuscleBan"]["MAC"])#, self.settings["R_MuscleBan"]["sampleRate"])
        
        self.sample_rate = self.findChild(QComboBox, 'comboBox_samplerate')
        self.__initSR(self.settings['Default']["samplerate"])

        self.sEMGwindow_nrm = self.findChild(QSpinBox, 'spinBox_sEMGwindownrm')
        self.sEMGwindow_nrm.setValue(int(self.settings['DataNMetrics']["semgwindow_nrm"]))
        
        self.sEMGwindow_TA = self.findChild(QSpinBox, 'spinBox_sEMGwindowTA')
        self.sEMGwindow_TA.setValue(int(self.settings['DataNMetrics']["semgwindow_ta"]))
        
        self.sEMGwindow_RMS = self.findChild(QSpinBox, 'spinBox_sEMGwindowRMS')
        self.sEMGwindow_RMS.setValue(int(self.settings['DataNMetrics']["semgwindow_rms"]))
        
        self.EDAwindow_nrm = self.findChild(QSpinBox, 'spinBox_EDAwindownrm')
        self.EDAwindow_nrm.setValue(int(self.settings['DataNMetrics']["edawindow_nrm"]))
        
        self.EDAwindow_NSSCR = self.findChild(QSpinBox, 'spinBox__EDAwindownsscr')
        self.EDAwindow_NSSCR.setValue(int(self.settings['DataNMetrics']["edawindow_nsscr"]))
        
        self.EDAwindow_SCRA = self.findChild(QSpinBox, 'spinBox__EDAwindowscr')
        self.EDAwindow_SCRA.setValue(int(self.settings['DataNMetrics']["edawindow_scra"]))
        
        self.ACCwindow_nrm = self.findChild(QSpinBox, 'spinBox_ACTwindownrm')
        self.ACCwindow_nrm.setValue(int(self.settings['DataNMetrics']["accwindow_nrm"]))

    def __initSR(self, samplerate):
        self.sample_rate.addItems(['1','10','100','1000']) #samp freq to list
        index = self.sample_rate.findText(samplerate)
        self.sample_rate.setCurrentIndex(index)

    def __initialize(self):
        pass
    
    def __updateSettings(self):
        print("BEGIN: Grabbing settings from window")
        self.settings['Default']['samplerate'] = self.sample_rate.currentText()
        self.settings['L_MuscleBan']['MAC'] = self.sensor_L_MuscleBan.getMAC()
        self.settings['R_MuscleBan']['MAC'] = self.sensor_R_MuscleBan.getMAC()
        self.settings['L_EDA']['MAC'] = self.sensor_L_EDA.getMAC()
        self.settings['R_EDA']['MAC'] = self.sensor_R_EDA.getMAC()
        self.settings['DataNMetrics']['sEMGwindow_nrm'] = str(self.sEMGwindow_nrm.value())
        self.settings['DataNMetrics']['sEMGwindow_TA'] = str(self.sEMGwindow_TA.value())
        self.settings['DataNMetrics']['sEMGwindow_RMS'] = str(self.sEMGwindow_RMS.value())
        self.settings['DataNMetrics']['EDAwindow_nrm'] = str(self.EDAwindow_nrm.value())
        self.settings['DataNMetrics']['EDAwindow_NSSCR'] = str(self.EDAwindow_NSSCR.value())
        self.settings['DataNMetrics']['EDAwindow_SCRA'] = str(self.EDAwindow_SCRA.value())
        self.settings['DataNMetrics']['ACCwindow_nrm'] = str(self.ACCwindow_nrm.value()) 
        print("END: Grabbing settings from window")
        
    def __applyANDclose(self):
        self.__updateSettings() #grab settings from settinsg window
        
        self.q_settings.put(self.q_settings) #pass to backend
        
        with open(self.filepath, 'w') as configfile: #write file
            print("Start: Writing settings to config")
            self.settings.write(configfile)
            print("End: Writing settings to config")
        #self.done()
        self.close()
        
    
    def __close(self):
        self.areyoursure = QMessageBox()
        self.areyoursure.setIcon(QMessageBox.Warning)
        self.areyoursure.setWindowTitle("Warning!")
        self.areyoursure.setText("Discard any changes to your settings?")
        self.areyoursure.setStandardButtons(QMessageBox.Yes|QMessageBox.No)
        response = self.areyoursure.exec_()
        #print(response)
        if response == 16384: #Yes was pressed
            self.close()
        elif response == 65536: #No was pressed
            pass #do nothing
    
    #### MUGGLE METHODS #### 

#### VULGAR METHODS #### they have no class
    
#### MAIN #### (just for testing independently of everything else)
def main():
    import sys
    
    app = QtWidgets.QApplication(sys.argv)
    
    Settings = configparser.ConfigParser()
    Settings.read('config.ini')
    
    Q_settings = queue.Queue()
      
    window = WINDOW_settings(settings=Settings, q_settings=Q_settings, filepath='config.ini') # Create an instance of our class
    result = window.show()
    
    sys.exit(app.exec()) #program loops forever  

if __name__ == '__main__':
    main()