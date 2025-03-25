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
from PyQt5.QtCore import Qt, pyqtSignal

from tkinter.filedialog import asksaveasfile
from tkinter import messagebox

#from PyQt5.QtCore.Qt import Horizontal

# CUSTOM #

#### CLASSES ####
class WIDGET_controls(QtWidgets.QWidget):
    signal_mode = pyqtSignal(str)
    signal_timeframe = pyqtSignal(float)
    signal_offset = pyqtSignal(float)
    #### MAGIC METHODS ####
    def __init__(self, *args, **kwargs):
        super(WIDGET_controls, self).__init__(*args, **kwargs)
        self.__createButtons()

        self.mode = "Stop"
        self.in_session = False
        self.window_widths = [30,60,120,480] #number of minutes to be in frame
        self.window_width = self.window_widths[0] #default 30 minutes
        self.window_offset = int(0) #% of data not in frame, 0:100 ints as percent
        
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
        self.scrollbar.setMinimum(int(0))
        self.scrollbar.setMaximum(int(100))
        self.scrollbar.setValue(int(100))
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
    
    def __recstop(self):
        match self.mode:
            case "Record": #switch to Stop
                response = messagebox.askyesno('End Stream', "Are you sure you want to end the stream?")
                if response: #returns true if "yes"
                    self.mode = "Stop"
                    self.in_session = False
                    self.button_recstop.setIcon(QIcon('./icons/icon_record.png'))
                else:
                    pass
                
            case "Stop" | "Play" | "Pause": #switch to record
                files = [('H5','.h5')]
                filename = ""
                while filename == "": #check if no file name given
                    filename = asksaveasfile(defaultextension=files, filetypes=files)
                if type(filename) == type(None):
                    print("Didn't pass, canceled")
                elif filename.name.endswith(".h5"):
                    print("Passed check")
                    self.mode = "Record"
                    self.in_session = True
                    self.button_recstop.setIcon(QIcon('./icons/icon_stop.png'))
                    self.button_playpause.setIcon(QIcon('./icons/icon_pause.png'))
                    self.signal_mode.emit("Record:{file}".format(file=filename.name))
                else:
                    print("Didn't pass, bad name")
                    pass
                
        print(self.mode)
                    
    def __playpause(self):
        match self.mode:
            case "Play" | "Record": #switch to pause
                self.mode = "Pause"
                self.button_playpause.setIcon(QIcon('./icons/icon_play.png'))
                self.signal_mode.emit("Pause")
            case "Pause" | "Stop": #switch to play
                self.mode = "Play"
                self.button_playpause.setIcon(QIcon('./icons/icon_pause.png'))
                self.signal_mode.emit("Play") 
                self.window_offset = 0
                self.signal_offset.emit(self.window_offset)
                self.scrollbar.setValue(100 - self.window_offset)
        print(self.mode)           
    
    def __zoomin(self):
        index = self.window_widths.index(self.window_width)
        
        if index > 0:
            self.window_width = self.window_widths[index-1]
            self.signal_timeframe.emit(self.window_width)
        else:
            pass
        
        print(self.window_width)
        
    def __zoomout(self):
        index = self.window_widths.index(self.window_width)
        
        if index < (len(self.window_widths)-1):
            self.window_width = self.window_widths[index+1]
            self.signal_timeframe.emit(self.window_width)
        else:
            pass
        
        print(self.window_width)
    
    def __prev(self):
        self.window_offset = self.window_offset + 10
        if self.window_offset > 100:
            self.window_offset = 100
        self.signal_offset.emit(self.window_offset)
        self.scrollbar.setValue(100 - self.window_offset)
        print(self.window_offset)
    
    def __rewind(self):
        self.window_offset = self.window_offset + 5
        if self.window_offset > 100:
            self.window_offset = 100
        self.signal_offset.emit(self.window_offset)
        self.scrollbar.setValue(100 - self.window_offset)
        print(self.window_offset)
    
    def __next(self):
        self.window_offset = self.window_offset - 5
        if self.window_offset < 0:
            self.window_offset = 0
        self.signal_offset.emit(self.window_offset)
        self.scrollbar.setValue(100 - self.window_offset)
        print(self.window_offset)
    
    def __ff(self):
        self.window_offset = self.window_offset - 10
        if self.window_offset < 0:
            self.window_offset = 0
        self.signal_offset.emit(self.window_offset)
        self.scrollbar.setValue(100 - self.window_offset)
        print(self.window_offset)
    
#### MAIN #### (just for testing independently of everything else)
def main():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = WIDGET_controls() # Create an instance of our class
    window.show()
    sys.exit(app.exec()) #program loops forever
    

if __name__ == '__main__':
    main()