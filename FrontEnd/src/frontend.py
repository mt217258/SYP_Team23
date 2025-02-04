'''
Author:             Matthew McLaughlin
Contact:            mt217258@dal.ca
Description:        
TODO List:          
'''

#### LIBRARIES ####
# OFF THE SHELF #
import queue
import pandas as pd
# CUSTOM #
from mainwindow import MainWindow
from thread_rcvdata import Worker_DAQ
#from widget_datastream import WIDGET_datastream #may not need this here

#### CLASSES ####
class FrontEnd():
    #### MAGIC METHODS ####
    def __init__(self, q_settings, q_commands, q_data):
        self.q_settings = q_settings
        self.q_commands = q_commands
        self.q_data = q_data
        
        self.load_settings()
        
        self.mainwindow = MainWindow()
        self.thread_rcvdata = Worker_DAQ(self.q_data)
        
        self.mainwindow.show()
        
    #### MANGELED METHODS #### 
    def __windowData(self):
        pass
    
    #### MUGGLE METHODS #### 
    def start(self):
        pass
    
    def stop(self):
        pass
    
    def accumulateData(self, dataSet):
        pass
    
    def updateGraphs(self):
        for graph in self.mainwindow.listGraphs:
            data_set = graph.selection()
            time, l_data, r_data = self.getData(data_set)
            graph.updateGraph(time, l_data, r_data)
    
    def sendCommand(self, command):
        pass
    
    def sendSettings(self):
        pass

    def load_settings(self):
        pass

#### MAIN #### (just for testing independently of everything else)
def main():
    pass

if __name__ == '__main__':
    main()