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
        #self.__linkActions()
        self.__linkWidgets()
        self.__initialize()
        
    #### MANGELED METHODS #### ("private" methods)
    '''def __linkActions(self):
        self.ActionApplyAndClose = self.findChild(QtWidgets.QAction, 'actionImport')
        self.ActionApplyAndClose.triggered.connect(self.__applyANDclose)
        
        self.ActionImport = self.findChild(QtWidgets.QAction, 'actionImport')
        self.ActionImport.triggered.connect(self.__importData)
    '''
        
    def __linkWidgets(self):
        self.button_applyANDsave = self.findChild(QtWidgets.QPushButton, 'button_applyANDsave')
        self.button_applyANDsave.clicked.connect(self.__applyANDclose)
        
        
    
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
def importSettings():
    pass
    
    
#### MAIN #### (just for testing independently of everything else)
def main():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    
    Settings = importSettings()
    
    window = WINDOW_settings(settings=Settings) # Create an instance of our class
    window.show()
    sys.exit(app.exec()) #program loops forever  

if __name__ == '__main__':
    main()