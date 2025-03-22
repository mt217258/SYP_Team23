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
import sys
#from PyQt5.QtWidgets import QApplication

# CUSTOM #
from window_main import WINDOW_main
from thread_rcvdata import Worker_DAQ
from common import dataselectmapping, data

#### CLASSES ####
class FrontEnd():
    #### MAGIC METHODS ####
    def __init__(self, q_settings, q_commands, q_data, config):
        self.q_settings = q_settings
        self.q_commands = q_commands
        self.q_data = q_data
        self.settings = config
        
        self.app = QtWidgets.QApplication(sys.argv)
        self.data = data  
        
        self.mainwindow = WINDOW_main(settings=config, Q_settings=q_settings, filepath="config.ini")
        print("Here")
        #self.thread_rcvdata = Worker_DAQ(self.q_data) TODO - get working
        
    #### MANGELED METHODS #### 
    def __linkWindows(self):
        pass    
    
    def __linkActions(self):
        pass
        

    
    def __windowData(self):
        pass
    
    #### MUGGLE METHODS #### 
    def start(self):
        self.mainwindow.show()
        sys.exit(self.app.exec()) #program loops forever
    
    def stop(self):
        pass
    
    def accumulateData(self, dataSet):
        pass
    
    def updateGraphs(self):
        currentTabview = self.mainwindow.widget_tabs.currentIndex() #grab index of tab in view
        currentTab = self.mainwindow.widget_tabs.currentWidget(currentTabview)  #grab that tab
        for plot in currentTab.list_Plots: #for the plots within current tab
            data2plot = plot.combobox.currentText() #what should this graph show
            left_data, right_data = dataselectmapping[data2plot]
            plot.updateGraph(self.data["Time"], self.data[left_data], self.data[right_data])
        
    def sendCommand(self, command):
        pass
    
    def sendSettings(self):
        pass

    #def load_settings(self):
    #    pass

#### MAIN #### (just for testing independently of everything else)
def main():
    q_settings = queue.Queue()
    q_commands = queue.Queue()
    q_data = queue.Queue()
    
    config = configparser.ConfigParser()
    config.read("config.ini")
    
    front = FrontEnd(q_settings, q_commands, q_data, config)
    front.start()
    

if __name__ == '__main__':
    main()