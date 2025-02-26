'''
Author:             Matthew McLaughlin
Contact:            mt217258@dal.ca
Description:        PyQT widget for controlling streamed data 
TODO List:          
'''

#### LIBRARIES ####
# OFF THE SHELF #
from PyQt5 import QtWidgets, uic
# CUSTOM #

#### CLASSES ####
class WIDGET_settingSensor(QtWidgets.QWidget):
    #### MAGIC METHODS ####
    def __init__(self, title, MAC, SampleRate, *args, **kwargs):
        super(WIDGET_settingSensor, self).__init__(*args, **kwargs)
        uic.loadUi('ui_files/widget_settings_sensors.ui', self)
        self.args = {"title":title, "MAC":MAC, 'samplerate':SampleRate}
        
        #self.__linkActions()
        self.__linkWidgets()
        self.__initialize()
        #self.__linkWindows()
        
    #### MANGELED METHODS #### ("private" methods)
    def __linkWidgets(self):
        self.MAC = self.findChild(QtWidgets.QLineEdit, 'lineEdit_MAC')
        self.sampleRate = self.findChild(QtWidgets.QComboBox, 'comboBox_sampleRate')
        self.groupBox = self.findChild(QtWidgets.QGroupBox, 'groupBox')
        
    def __initialize(self):
        self.sampleRate.addItems(['1 Hz','10 Hz','100 Hz','1000 Hz']) #samp freq to list
        self.groupBox.setTitle(self.args["title"])
        self.setSettings(self.args["MAC"], self.args["samplerate"])
    
    #### MUGGLE METHODS #### 
    def getSettings(self): #return settings
        settings = {} #return settings as a dictionary
        settings["MAC"] = self.MAC.text()
        settings["SampleRate"] = self.sampleRate.currentText()
        return settings
    
    def setSettings(self, MAC, sampleRate):
        self.MAC.setText(MAC)
        index = self.sampleRate.findText(sampleRate)
        self.sampleRate.setCurrentIndex(index)
        
    
#### MAIN #### (just for testing independently of everything else)
def main():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = WIDGET_settingSensor(title="L_sEMG", MAC="123", SampleRate="10 Hz") # Create an instance of our class
    print(window.getSettings()) #test return
    window.show()
    sys.exit(app.exec()) #program loops forever
    

if __name__ == '__main__':
    main()