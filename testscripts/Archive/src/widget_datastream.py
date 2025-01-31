'''
Author:             Matthew McLaughlin
Contact:            mt217258@dal.ca
Description:        PyQT widget for displaying streamed data 
TODO List:          
'''

#### LIBRARIES ####
#from pylsl import StreamInlet, resolve_streams
#from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import QtWidgets, uic
#from PyQt5.QtCore import Qt
#from PyQt5.QtWidgets import *

#### GLOBAL VARIABLES ####

#### CLASSES ####
class WIDGET_datastream(QtWidgets.QWidget):
    #### MAGIC METHODS ####
    def __init__(self, *args, **kwargs):
        super(WIDGET_datastream, self).__init__(*args, **kwargs)
        uic.loadUi('widget_datastream.ui', self)
        self.__linkActions()
        self.__linkWidgets()
        self.__linkWindows()
        
    #### MANGELED METHODS #### ("private" methods)
    def __linkActions(self):
        pass
    
    def __linkWidgets(self):
        pass
    
    def __linkWindows(self):
        pass
    
    #### MUGGLE METHODS ####  (public methods)
    def updateStreamList(self):
        pass
    
    def updateGraph(self):
        pass
    
#### VULGAR METHODS #### (they have no class) 

#### MAIN #### (just for testing independently of everything else)
def main():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = WIDGET_datastream() # Create an instance of our class
    window.show()
    sys.exit(app.exec()) #program loops forever

if __name__ == '__main__':
    main()
