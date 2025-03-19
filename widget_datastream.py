'''
Author:             Matthew McLaughlin
Contact:            mt217258@dal.ca
Description:        PyQT widget for displaying streamed data 
TODO List:          
'''

#### LIBRARIES ####
# OFF THE SHELF #
#from pylsl import StreamInlet, resolve_streams
#from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import QtWidgets, uic
from pyqtgraph import PlotWidget
#from PyQt5.QtCore import Qt
#from PyQt5.QtWidgets import *
#import pandas as pd
import os

# CUSTOM #
from common import list_signals

#### GLOBAL VARIABLES ####


#### CLASSES ####
class WIDGET_datastream(QtWidgets.QWidget):
    #### MAGIC METHODS ####
    def __init__(self, plot_num, *args, **kwargs):
        super(WIDGET_datastream, self).__init__(*args, **kwargs)
        
        #path = os.path.abspath(__file__)
        #dir_path = os.path.dirname(path)
        dir_path = os.path.dirname(os.path.abspath(__file__))
        ui_filepath = dir_path + '/ui_files/widget_datastream.ui'
        uic.loadUi(ui_filepath, self)
        #uic.loadUi('ui_files/widget_datastream.ui', self)
        
        self.plot_num = plot_num
        
        self.__linkActions()
        self.__linkWidgets()
        self.__linkWindows()
        self.updateStreamList()
        self.init_graph()
        #self.data = pd.DataFrame(data={"Time":[], "Y1":[], "Y2":[]})
        
    #### MANGELED METHODS #### ("private" methods)
    def __linkActions(self):
        pass
    
    def __linkWidgets(self):
        self.plot_graph = self.findChild(PlotWidget, 'widget_graph')
        self.combobox = self.findChild(QtWidgets.QComboBox, 'comboBox')
    
    def __linkWindows(self):
        pass
    
    #def __window_data(self): #only show newest N samples
    #    pass
    
    #### MUGGLE METHODS ####  (public methods)
    def updateStreamList(self):
        self.combobox.addItems(list_signals)
    
    def init_graph(self):
        self.plotLeft = self.plot_graph.plot([0],[0], name="Left Data", symbol='+', symbolSize=15)
        self.plotRight = self.plot_graph.plot([0],[0], name="Right Data", symbol='x', symbolSize=15)
    
    def updateGraph(self, time, data_left, data_right):
        self.plotLeft.setData(time, data_left)
        self.plotRight.setData(time, data_right)
        
#### VULGAR METHODS #### (they have no class) 
#TODO Will implement in frontend
#def window_data(windowSize, time, data1, data2):
    #returns a windowed sample of newest data, based on number of sample, windowSize
    #return time[len(time)-windowSize:], data1[len(data1)-windowSize:], data2[len(data2)-windowSize:]

#### MAIN #### (just for testing independently of everything else)
def main():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = WIDGET_datastream(0) # Create an instance of our class
    window.show()
    #window.updateGraph([1], [2], [3])
    sys.exit(app.exec()) #program loops forever
    

if __name__ == '__main__':
    main()
