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
from pyqtgraph import PlotWidget, mkPen
#from PyQt5.QtCore import Qt
#from PyQt5.QtWidgets import *
#import pandas as pd
import os
import numpy as np

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
        self.plot_graph.setLabel("bottom", "Time [s]")
        self.plot_graph.addLegend()
    
        penL = mkPen(color=(255, 0, 0))
        penR = mkPen(color=(0, 0, 255))
        self.plotLeft = self.plot_graph.plot([0],[0], name="Left", pen=penL)
        self.plotRight = self.plot_graph.plot([0],[0], name="Right", pen=penR)
        
    
    def updateGraph(self, time, data_left, data_right):
<<<<<<< Updated upstream
<<<<<<< Updated upstream
        try:
            # Convert to numpy arrays
            x = np.array(time, dtype=np.float64)
            y = np.array(data_left, dtype=np.float64)

            # Auto-scrolling time axis
            if len(x) > 1:
                time_range = x[-1] - x[0]
                self.plot_graph.setXRange(x[-1]-10, x[-1]+0.1)

            self.plotLeft.setData(x,y)
            if data_right is not None:
                self.plotRight.setData(x, np.array(data_right))

            # Enable auto-scrolling
            self.plot_graph.enableAutoRange()

        except Exception as e:
            print(f"Plotting failed: {str(e)}")

        # Update Plots
        #self.plotLeft.setData(time_array, left_array)
       # self.plotRight.setData(time_array, right_array)
=======
        self.plotLeft.setData(list(time), list(data_left))
        self.plotRight.setData(list(time), list(data_right))
>>>>>>> Stashed changes
=======
        self.plotLeft.setData(list(time), list(data_left))
        self.plotRight.setData(list(time), list(data_right))
>>>>>>> Stashed changes
        #NOTE - Error when lists are empty, might be ignorable
        
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
