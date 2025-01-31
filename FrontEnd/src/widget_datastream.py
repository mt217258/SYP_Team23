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
from pyqtgraph import PlotWidget
#from PyQt5.QtCore import Qt
#from PyQt5.QtWidgets import *
#import pandas as pd
#### GLOBAL VARIABLES ####

#### CLASSES ####
class WIDGET_datastream(QtWidgets.QWidget):
    #### MAGIC METHODS ####
    def __init__(self, *args, **kwargs):
        super(WIDGET_datastream, self).__init__(*args, **kwargs)
        uic.loadUi('../ui_files/widget_datastream.ui', self)
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
    
    def __linkWindows(self):
        pass
    
    def __window_data(self): #only show newest N samples
        pass
    
    #### MUGGLE METHODS ####  (public methods)
    def updateStreamList(self):
        pass
    
    def init_graph(self):
        self.plotLeft = self.plot_graph.plot([0],[0], name="Left Data", symbol='+', symbolSize=15)
        self.plotRight = self.plot_graph.plot([0],[0], name="Right Data", symbol='x', symbolSize=15)
    
    def updateGraph(self, time, data_left, data_right):
        self.plotLeft.setData(time, data_left)
        self.plotRight.setData(time, data_right)
    
    #def add_datapoint(self, t, y1, y2):
    #    new_datapoint = pd.DataFrame(data={"Time":[t], "Y1":[y1], "Y2":[y2]})
    #    self.data = pd.concat([self.data, new_datapoint], ignore_index=True)
    #    self.updateGraph()
        
#### VULGAR METHODS #### (they have no class) 
def window_data(windowSize, time, data1, data2):
    #returns a windowed sample of newest data, based on number of sample, windowSize
    return time[len(time)-windowSize:], data1[len(data1)-windowSize:], data2[len(data2)-windowSize:]

#### MAIN #### (just for testing independently of everything else)
def main():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = WIDGET_datastream() # Create an instance of our class
    window.show()
    #window.updateGraph([1], [2], [3])
    sys.exit(app.exec()) #program loops forever
    

if __name__ == '__main__':
    main()
