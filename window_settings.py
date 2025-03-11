'''
Author:             Matthew McLaughlin
Contact:            mt217258@dal.ca
Description:        Settings control for data viewer
TODO List:          
'''

#### LIBRARIES ####
# OFF THE SHELF #
from PyQt5 import QtWidgets, uic
import configparser
# CUSTOM #
from widget_settingSensor import WIDGET_settingSensor 
#import WIDGET_settingSensor 

#### CLASSES ####
class WINDOW_settings(QtWidgets.QDialog):
    #### MAGIC METHODS ####
    def __init__(self, settings, *args, **kwargs):
        super(WINDOW_settings, self).__init__(*args, **kwargs)
        uic.loadUi('ui_files/window_settings.ui', self)
        
        self.settings = settings #configParser object
        print(dir(self.settings))
        #print("Settings type is: " , type(self.settings))
        
        self.__linkActions()
        self.__linkWidgets()
        self.__initialize()
        #self.__buildWidget()
        
    #### MANGELED METHODS #### ("private" methods)
    '''
    def __buildWidget(self): 
        self.widget_outer = QtWidgets.QWidget()
        self.layout_widget_outer = QtWidgets.QVBoxLayout()
        
        self.widget_tab = QtWidgets.QTabWidget()
        self.layout_widget_tab = QtWidgets.QVBoxLayout()
        
        self.frame_buttons = QtWidgets.QFrame()
        self.layout_frame_buttons = QtWidgets.QHBoxLayout()
        
        self.button_applyNclose = QtWidgets.QPushButton()
        self.button_close = QtWidgets.QPushButton()
        #self.layout_frame_buttons.addWidget(QtWidgets.QSpacerItem()
        self.layout_frame_buttons.addWidget(self.button_applyNclose)
        self.layout_frame_buttons.addWidget(self.button_close)
        
        
        self.layout_widget_outer.addWidget(self.widget_tab)
        self.layout_widget_outer.addWidget(self.frame_buttons)
        
        self.setCentralWidget(self.widget_outer)
    '''
    def __linkActions(self):
        pass
      
    def __linkWidgets(self):
        self.button_applyANDsave = self.findChild(QtWidgets.QPushButton, 'button_applyANDsave')
        self.button_applyANDsave.clicked.connect(self.__applyANDclose)
        
        self.button_close = self.findChild(QtWidgets.QPushButton, 'button_close')
        self.button_close.clicked.connect(self.__close)
        
        self.sensor_L_EDA = self.findChild(WIDGET_settingSensor, 'L_EDA')
        self.sensor_L_EDA.setSettings("L_EDA", self.settings["L_EDA"]["MAC"])#, self.settings["L_EDA"]["sampleRate"])
        
        self.sensor_R_EDA = self.findChild(WIDGET_settingSensor, 'R_EDA')
        self.sensor_R_EDA.setSettings("R_EDA", self.settings["R_EDA"]["MAC"])#, self.settings["R_EDA"]["sampleRate"])
        
        self.sensor_L_MuscleBan = self.findChild(WIDGET_settingSensor, 'L_MuscleBan')
        self.sensor_L_MuscleBan.setSettings("L_MuscleBan", self.settings["L_MuscleBan"]["MAC"])#, self.settings["L_MuscleBan"]["sampleRate"])
        
        self.sensor_R_MuscleBan = self.findChild(WIDGET_settingSensor, 'R_MuscleBan')
        self.sensor_R_MuscleBan.setSettings("R_MuscleBan", self.settings["R_MuscleBan"]["MAC"])#, self.settings["R_MuscleBan"]["sampleRate"])
        

    def __initialize(self):
        pass
    
    def __applyANDclose(self):
        pass
    
    def __close(self):
        pass
    
    #### MUGGLE METHODS #### 
    def returnSettings(self):
        pass

#### VULGAR METHODS #### they have no class
    
#### MAIN #### (just for testing independently of everything else)
def main():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    
    Settings = configparser.ConfigParser()
    Settings.read('config.ini')
    
    window = WINDOW_settings(settings=Settings) # Create an instance of our class
    window.show()
    sys.exit(app.exec()) #program loops forever  

if __name__ == '__main__':
    main()