'''
Author:             Matthew McLaughlin
Contact:            mt217258@dal.ca
Description:        PyQT widget for controlling streamed data 
TODO List:          
'''

#### LIBRARIES ####
# OFF THE SHELF #
from PyQt5 import QtWidgets
from PyQt5.Qt import QPushButton
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

#from PyQt5.QtCore.Qt import Horizontal

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
        self.mode = "Standby"
        
    #### MANGELED METHODS #### ("private" methods)
    def __createButtons(self):
        self.layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.layout)
        
        self.button_prev = QPushButton("", self)
        self.button_prev.setFixedWidth(50)
        self.button_prev.clicked.connect(self.__prev)
        self.button_prev.setIcon(QIcon('./icons/icon_prev.png'))
        
        
        self.layout.addWidget(self.button_prev)
        
        self.button_rewind = QPushButton("", self)
        self.button_rewind.setFixedWidth(50)
        self.button_rewind.clicked.connect(self.__rewind)
        self.button_rewind.setIcon(QIcon('./icons/icon_rewind.png'))
        self.layout.addWidget(self.button_rewind)
    
        self.scrollbar = QtWidgets.QScrollBar()
        self.scrollbar.setOrientation(Qt.Horizontal)
        self.layout.addWidget(self.scrollbar)
    
        self.button_ff = QPushButton("", self)
        self.button_ff.setFixedWidth(50)
        self.button_ff.clicked.connect(self.__ff)
        self.button_ff.setIcon(QIcon('./icons/icon_ff.png'))
        self.layout.addWidget(self.button_ff)
    
        self.button_next = QPushButton("", self)
        self.button_next.setFixedWidth(50)
        self.button_next.clicked.connect(self.__next)
        self.button_next.setIcon(QIcon('./icons/icon_next.png'))
        self.layout.addWidget(self.button_next)
    
        self.button_zoomin = QPushButton("", self)
        self.button_zoomin.setFixedWidth(50)
        self.button_zoomin.clicked.connect(self.__zoomin)
        self.button_zoomin.setIcon(QIcon('./icons/icon_zoomin.png'))
        self.layout.addWidget(self.button_zoomin)
    
        self.button_zoomout = QPushButton("", self)
        self.button_zoomout.setFixedWidth(50)
        self.button_zoomout.clicked.connect(self.__zoomout)
        self.button_zoomout.setIcon(QIcon('./icons/icon_zoomout.png'))
        self.layout.addWidget(self.button_zoomout)
    
        self.button_playpause = QPushButton("", self)
        self.button_playpause.setFixedWidth(50)
        self.button_playpause.clicked.connect(self.__playpause)
        self.button_playpause.setIcon(QIcon('./icons/icon_play.png'))
        self.layout.addWidget(self.button_playpause)
    
        self.button_recstop = QPushButton("", self)
        self.button_recstop.setFixedWidth(50)
        self.button_recstop.clicked.connect(self.__recstop)
        self.button_recstop.setIcon(QIcon('./icons/icon_record.png'))
        self.layout.addWidget(self.button_recstop)
    
    def __zoomout(self):
        pass
    
    def __recstop(self):
        pass
    
    def __playpause(self):
        pass
    
    def __zoomin(self):
        pass
    
    def __ff(self):
        pass
    
    def __prev(self):
        pass
    
    def __rewind(self):
        pass
    
    def __zoomIn(self):
        pass
    
    def __next(self):
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