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
#from future.backports.test.pystone import FALSE

#### CLASSES ####
class FrontEnd():
    #### MAGIC METHODS ####
    def __init__(self, q_settings, q_commands, q_data, config):
        self.q_settings = q_settings
        self.q_commands = q_commands
        self.q_data = q_data
        self.settings = config
        
        #self.mode = "Pause" #"Stream", "Pause", "Stop"
        self.isStreaming = False
        self.isRecording = False
        
        self.window_width = 30 #in mins
        self.window_offset = 0 #in int from 0 -> 100
        
        self.app = QtWidgets.QApplication(sys.argv)
        self.data = data  
        
        self.mainwindow = WINDOW_main(settings=config, Q_settings=q_settings, filepath="config.ini")
        self.__linkThreads()
        self.__linkControlSignals()
        
    #### MANGELED METHODS ####
    def __linkControlSignals(self):
        self.mainwindow.widget_controls.signal_streaming.connect(self.__updateStreaming)
        self.mainwindow.widget_controls.signal_recordname.connect(self.__updateFilename)
        self.mainwindow.widget_controls.signal_recording.connect(self.__updateRecording)
        self.mainwindow.widget_controls.signal_width.connect(self.__updateWindowWidth)
        self.mainwindow.widget_controls.signal_offset.connect(self.__updateWindowOffset)
    
    def __updateStreaming(self, onoff):
        print("FE: Streaming update to: ", onoff)
        if not self.isStreaming and onoff: #streaming turned on
            pass
        if not self.isStreaming and not onoff: #streaming paused
            self.index_lastSampleBeforePause = len(self.data)
        self.isStreaming = onoff
    
    def __updateFilename(self, filename):
        self.filename = filename
    
    def __updateRecording(self, onoff):
        if not self.isRecording:
            self.q_commands.put("Record:".format(name=self.filename)) #
        else:
            self.q_commands.put("Stop") #stop recording & streaming
        self.isStreaming = onoff
    
    def __updateWindowWidth(self, width):
        print("FE: Window width updated to: ", width)
        self.window_width = width
        self.updateGraphs()
    
    def __updateWindowOffset(self, offset):
        print("FE: Window offset updated to: ", offset)
        self.window_offset = offset
        self.updateGraphs() 
    
    def __linkThreads(self):
        self.thread_DAQ = QThread() #create thread
        self.worker_DAQ = Worker_DAQ(self.q_data) #create object to run in thread
        self.worker_DAQ.moveToThread(self.thread_DAQ) #move object to thread
        
        self.thread_DAQ.started.connect(self.worker_DAQ.run) #when thread started, run worker's run()
        #self.thread_DAQ.started.connect(self.worker_DAQ.test_run) #used for testing

        self.worker_DAQ.sendData.connect(self.__getData) #link pyqt signals
        
        self.thread_DAQ.start()
        
    def __getData(self, sample):
        self.data = pd.concat([self.data, sample])
        #TODO - downsample data
        if self.isStreaming:
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