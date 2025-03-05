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
import configparser
from PyQt5 import QtWidgets

# CUSTOM #
from window_main import WINDOW_main

from thread_rcvdata import Worker_DAQ

#### CLASSES ####
class FrontEnd():
    #### MAGIC METHODS ####
    def __init__(self, q_settings, q_commands, q_data, config):
        self.q_settings = q_settings
        self.q_commands = q_commands
        self.q_data = q_data
        self.settings = config
        
        self.mainwindow = WINDOW_main()
        self.thread_rcvdata = Worker_DAQ(self.q_data)
        
    #### MANGELED METHODS #### 
    def __linkWindows(self):
        
    
    def __linkActions(self):
        pass
        

    
    def __windowData(self):
        pass
    
    #### MUGGLE METHODS #### 
    def start(self):
        self.mainwindow.show()
    
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

    #def load_settings(self):
    #    pass

#### MAIN #### (just for testing independently of everything else)
def main():
    import sys
    from PyQt5.QtWidgets import QApplication
    #TODO - add passing queues
    app = QApplication(sys.argv)
    mainwindow = WINDOW_main()
    mainwindow.show()
    sys.exit(app.exec()) #program loops forever

if __name__ == '__main__':
    main()