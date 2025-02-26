'''
Author:             Matthew McLaughlin
Contact:            mt217258@dal.ca
Description:        PyQT widget for controlling streamed data 
TODO List:          
'''

#### LIBRARIES ####
# OFF THE SHELF #
from PyQt5 import QtWidgets
# CUSTOM #

#### CLASSES ####
class WIDGET_controls(QtWidgets.QWidget):
    #### MAGIC METHODS ####
    def __init__(self, *args, **kwargs):
        super(WIDGET_controls, self).__init__(*args, **kwargs)
        self.__createButtons()
        #uic.loadUi('../ui_files/widget_streamcontrols.ui', self)
        #self.__linkActions()
        #self.__linkWidgets()
        #self.__linkWindows()
        
        
    #### MANGELED METHODS #### ("private" methods)
    def __createButtons(self):
        pass
    
#### MAIN #### (just for testing independently of everything else)
def main():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = WIDGET_controls() # Create an instance of our class
    window.show()
    sys.exit(app.exec()) #program loops forever
    

if __name__ == '__main__':
    main()