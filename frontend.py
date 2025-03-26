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

import multiprocessing
from PyQt5.QtCore import QObject, QThread, pyqtSignal
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
        
        self.mode = "Pause" #"Stream", "Pause", "Stop"
        
        self.app = QtWidgets.QApplication(sys.argv)
        self.data = data  
        
        self.mainwindow = WINDOW_main(settings=config, Q_settings=q_settings, filepath="config.ini")
        self.__linkThreads()
        self.__linkControlSignals()
        
        #self.thread_rcvdata = Worker_DAQ(self.q_data) #TODO - get working
        
    #### MANGELED METHODS ####
    def __linkControlSignals(self):
        self.mainwindow.widget_controls.signal_mode.connect(self.__updateMode)
        self.mainwindow.widget_controls.signal_timeframe.connect(self.__updateTimeFrame)
        self.mainwindow.widget_controls.signal_offset.connect(self.__updateWindowOffset)
    
    def __updateMode(self, mode):
        print("Mode updated: ", mode)
    
    def __updateTimeFrame(self, frame):
        print("Timeframe updated: ", frame)
    
    def __updateWindowOffset(self, offset):
        print("Window offset updated: ", offset)
    
    def __linkThreads(self):
        self.thread_DAQ = QThread() #create thread
        self.worker_DAQ = Worker_DAQ(self.q_data) #create object to run in thread
        self.worker_DAQ.moveToThread(self.thread_DAQ) #move object to thread
        
        self.thread_DAQ.started.connect(self.worker_DAQ.run) #when thread started, run worker's run()
        #self.thread_DAQ.started.connect(self.worker_DAQ.test_run)
        
        #self.worker.finished.connect(self.thread.quit)
        #self.worker.finished.connect(self.worker.deleteLater)
        #self.thread.finished.connect(self.thread.deleteLater)
        self.worker_DAQ.sendData.connect(self.__getData) #link pyqt signals
        
        #TODO: move start thread to when stream starts, not on program start
        self.thread_DAQ.start()
        
    def __getData(self, sample):
        self.data = pd.concat([self.data, sample])
        #TODO - downsample data
        self.updateGraphs() 
     
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
        #TODO - window data
        
        #currentTabview = self.mainwindow.widget_tabs.currentIndex() #grab index of tab in view
        currentTab = self.mainwindow.widget_tabs.currentWidget()  #grab that tab
        for plot in currentTab.listPlots: #for the plots within current tab
            data2plot = plot.combobox.currentText() #what should this graph show
            left_data, right_data = dataselectmapping[data2plot]
            #print(left_data, self.data[left_data])
            plot.updateGraph(self.data["Time"], self.data[left_data], self.data[right_data])
        
    def sendCommand(self, command):
        pass
    
    def sendSettings(self):
        pass

    #def load_settings(self):
    #    pass

#### MAIN #### (just for testing independently of everything else)
def main():
    q_settings = multiprocessing.Queue()
    q_commands = multiprocessing.Queue()
    q_data = multiprocessing.Queue()
    
    config = configparser.ConfigParser()
    config.read("config.ini")
    
    front = FrontEnd(q_settings, q_commands, q_data, config)
    front.start()

if __name__ == '__main__':
    main()