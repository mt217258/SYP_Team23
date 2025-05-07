'''
Author:             Matthew McLaughlin/Will Thornton
Contact:            
Description:        Backend component to manage data collection, 
                    metric calculations & data saving 
TODO List:          
'''

#### LIBRARIES ####
# OFF THE SHELF #
import multiprocessing
# CUSTOM #
from rawData import RawData
from metrics import Metrics
from saveAndDisplay import SaveAndDisplay

class BackEnd():
    #### MAGIC METHODS ####
    def __init__(self, q_settings, q_commands, q_data, config):
        #link main queues
        self.q_settings = q_settings
        self.q_commands = q_commands
        self.q_toFrontEnd = q_data
        
        self.__createQueues()
        
        self.__createThreads()
        self.__startThreads()
        
        self.__createProcesses()
        self.__startProcesses()
        
    #### MANGELED METHODS ####
    def __createThreads(self):
        #TODO - create thread for watching for FE commands
        pass
    
    def __startThreads(self):
        pass
    
    def __createQueues(self):
        #queues for between backend processes
        self.q_rawdata = multiprocessing.Queue()
        self.q_metrics = multiprocessing.Queue() 
        
        self.q_commandsForRawData = multiprocessing.Queue()
        self.q_settingsForRawData = multiprocessing.Queue()
    
        self.q_metricdata = multiprocessing.Queue()
        self.q_commandsForMetrics = multiprocessing.Queue()
        self.q_settingsForMetrics = multiprocessing.Queue()
        
    def __createProcesses(self):
        #backend processes
        self.p_rawData = multiprocessing.Process(
            target=self.__prep_rawData, 
            args=(self.q_rawData, self.q_commandsForRawData, self.q_settingsForRawData) )
        
        self.p_metrics = multiprocessing.Process(
            target=self.__prep_metrics, 
            args=(self.q_rawData, self.q_metricdata, self.q_commandsForMetrics, self.q_settingsForMetrics) )
    
        self.p_saveAndDisplay = multiprocessing.Process(
            target=self.__prep_saveAndDisplay, 
            args=(self.q_metricdata, self.q_toFrontEnd, self.q_commandsForSAD, self.q_settingsForSAD) )
    
    def __prep_rawData(self, q_rawData, q_commandsForRawData, q_settingsForRawData):
        rd = RawData(q_rawData, q_commandsForRawData, q_settingsForRawData)
        rd.start()
    
    def __prep_metrics(self):
        pass
    
    def __prep_saveAndDisplay(self):
        pass
    
    
    
    def __startProcesses(self):
        self.p_rawData.start()
        self.p_metrics.start()
        self.p_saveAndDisplay.start()
    
    #### MUGGLE METHODS #### 

#### MAIN #### (just for testing independently of everything else)
def main():
    backend = BackEnd()
    

if __name__ == '__main__':
    main()