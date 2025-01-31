'''
Author:             Matthew McLaughlin
Contact:            mt217258@dal.ca
Description:        PyQT widget for displaying streamed data 
TODO List:          
'''

#### LIBRARIES ####
# OFF THE SHELF #
import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication
# CUSTOM #

#### CLASSES ####
class MainWindow(QMainWindow):
    #### MAGIC METHODS ####
    def __init__(self, parent=None):
        super(MainWindow, self).__init__()
        uic.loadUi('../ui_files/mainwindow.ui', self)
        
        self.__linkActions()
        self.__linkWidgets()
        self.__linkWindows()  
      
    #### MANGELED METHODS ####   
    def __linkActions(self):
        pass
    
    def __linkWidgets(self):
        pass

    def __linkWindows(self):
        pass

    #### MUGGLE METHODS #### 

#### MAIN #### (just for testing independently of everything else)
def main():
    app = QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.show()
    sys.exit(app.exec()) #program loops forever

if __name__ == '__main__':
    main()