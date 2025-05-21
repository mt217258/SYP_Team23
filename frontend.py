#### LIBRARIES ####
# OFF THE SHELF #
import queue
import pandas as pd
import configparser
from PyQt5 import QtWidgets
import multiprocessing
from PyQt5.QtCore import QObject, QThread, pyqtSignal, QTimer
import sys

from pandas._libs import index

# CUSTOM #
from window_main import WINDOW_main
from thread_rcvdata import Worker_DAQ
from common import dataselectmapping, data

#### Classes ####
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
        
        self.plot_update_timer = QTimer()
        self.plot_update_timer.timeout.connect(self.updateGraphs)
        #TODO - Refresh rate controlled in settings
        self.refreshrate = 1 #Hz
        self.refreshperiod_ms = int(1/self.refreshrate *1000) #ms
        
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
            print("Starting Stream")
            self.isStreaming = onoff
            self.q_commands.put("Play")
            self.plot_update_timer.start(self.refreshperiod_ms) #convert to period in ms
            
        if self.isStreaming and not onoff: #streaming paused
            print("Pausing stream")
            self.isStreaming = onoff
            self.index_lastSampleBeforePause = len(self.data["Time"])-1
            self.plot_update_timer.stop()
            print("Pausing stream. Last index: ", self.index_lastSampleBeforePause)    
    
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
        
        #self.thread_DAQ.started.connect(self.worker_DAQ.run) #when thread started, run worker's run()
        self.thread_DAQ.started.connect(self.worker_DAQ.test_run) #used for testing

        self.worker_DAQ.sendData.connect(self.__getData) #link pyqt signals
        
        self.thread_DAQ.start()
        
    def __getData(self, sample):
        self.data = pd.concat([self.data, sample], ignore_index=True)
        #TODO - downsample data
    
    #### MUGGLE METHODS #### 
    def start(self):
        print("FE: Start")
        self.mainwindow.show()
        sys.exit(self.app.exec()) #program loops forever
    
    def updateWindowIndices(self):
        datalength = len(self.data["Time"])
        
        if self.isStreaming: #not paused
            self.index_end = datalength - 1
            
            #TODO - update window width for streaming based on downsample rates
            window_size = 1
            match self.window_width:
                case 30: #in minutes
                    window_size = 500 
                case 60:
                    window_size = 750
                case 120:
                    window_size = 1000
                case 480:
                    window_size = 1250
            self.index_start = self.index_end - window_size  
            
        else: #stream paused
            #print("Stream paused")
            #print("Pause index: ", self.index_lastSampleBeforePause)
            
            self.startTime = self.data["Time"].iloc[0] #first value
            self.endTime = self.data["Time"].iloc[self.index_lastSampleBeforePause] #last value
            #print("Paused data start time: ", self.startTime)
            #print("Paused data end time: ", self.endTime)
            
            self.timeDiff = self.endTime - self.startTime - self.window_width*60 #time not on screen in s
            #print("Paused data time diff: ", self.timeDiff)
            
            #if window is larger than data sample, use all data
            if self.window_width*60 > self.endTime - self.startTime:
                
                self.index_start = 0
                self.index_end = len(self.data["Time"])
            #if window is smaller, find start/stop indices
            else:
                self.offset_s = self.timeDiff * (float(self.window_offset)/100.0)
                print("Offset in s is: ", self.offset_s)
                #print("Offset value: ", self.window_offset)
                #for the paused interval, from index 0 to index_pause
                #set start index for plot window - thyme is time
                for index, thyme in enumerate(self.data["Time"].iloc[0:self.index_lastSampleBeforePause]):
                    '''
                    #if, set start point to start of whole data
                    if 0 > (self.endTime - self.window_width*60 - self.offset_s):
                        self.index_start = 0
                        break
                    #else, if positive, iterate through timestamps until 1st time greater
                    #than windowed time
                    '''
                    if thyme > (self.endTime - self.window_width*60 - self.offset_s):
                        self.index_start = index
                        break
            
                    #set end index for plot window - thyme is time
                for index, thyme in enumerate(self.data["Time"].iloc[0:self.index_lastSampleBeforePause]):
                    '''
                    #if, set end point to end of whole data
                    if 0 > (self.endTime - self.window_width*60 - self.offset_s):
                        self.index_end = self.index_lastSampleBeforePause
                        break
                    '''    
                    if thyme > (self.endTime - self.offset_s):
                        self.index_end = index
                        break
            
            #print("Data length: ", datalength)
            
            print("Window start index: ", self.index_start)
            print("Window end index: ", self.index_end)
            
            print("Window Start time: ", self.data["Time"].iloc[self.index_start])
            print("Window End time: ", self.data["Time"].iloc[self.index_end-1])
            
    def updateGraphs(self): 
        print("Updating plots")  
        self.updateWindowIndices()
        
        #currentTabview = self.mainwindow.widget_tabs.currentIndex() #grab index of tab in view
        currentTab = self.mainwindow.widget_tabs.currentWidget()  #grab that tab
        for plot in currentTab.listPlots: #for the plots within current tab
            data2plot = plot.combobox.currentText() #what should this graph show
            left_data, right_data = dataselectmapping[data2plot]
            #print(left_data, self.data[left_data])
            plot.updateGraph(self.data["Time"][self.index_start:self.index_end], 
                             self.data[left_data][self.index_start:self.index_end], 
                             self.data[right_data][self.index_start:self.index_end])
        
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