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
#import queue
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
        #BE->rawdata    
        self.q_commandsForRawData = multiprocessing.Queue()
        self.q_settingsForRawData = multiprocessing.Queue()
        #rawdata->metrics
        self.q_rawData = multiprocessing.Queue()
        #BE->metrics
        self.q_commandsForMetrics = multiprocessing.Queue()
        self.q_settingsForMetrics = multiprocessing.Queue()
        #metrics->SaD
        self.q_metricdata = multiprocessing.Queue()
        #BE->SaD
        self.q_commandsForSAD = multiprocessing.Queue()
        self.q_settingsForSAD = multiprocessing.Queue()
        #SaD->FE
        self.q_toFrontEnd = multiprocessing.Queue()
    ''' 
    def __prep_rawData(self, q_rawData, q_commandsForRawData, q_settingsForRawData):
        rd = RawData(q_rawData, q_commandsForRawData, q_settingsForRawData)
        rd.start()
    
    def __prep_metrics(self, q_rawData, q_metricdata, q_commandsForMetrics, q_settingsForMetrics):
        met = Metrics(q_rawData, q_metricdata, q_commandsForMetrics, q_settingsForMetrics)
        met.start()
    
    def __prep_saveAndDisplay(self, q_metricdata, q_toFrontEnd, q_commandsForSAD, q_settingsForSAD):
        sad = SaveAndDisplay(q_metricdata, q_toFrontEnd, q_commandsForSAD, q_settingsForSAD)
        sad.start() 
    '''
        
    def __createProcesses(self):
        #backend processes
        print("Creating processes...")
        
        self.p_rawData = multiprocessing.Process(
            target=prep_rawData, 
            args=(self.q_rawData, self.q_commandsForRawData, self.q_settingsForRawData) )
        
        self.p_metrics = multiprocessing.Process(
            target=prep_metrics, 
            args=(self.q_rawData, self.q_metricdata, self.q_commandsForMetrics, self.q_settingsForMetrics) )
        
        self.p_saveAndDisplay = multiprocessing.Process(
            target=prep_saveAndDisplay, 
            args=(self.q_metricdata, self.q_toFrontEnd, self.q_commandsForSAD, self.q_settingsForSAD) )
        
        if self.p_rawData and self.p_metrics and self.p_saveAndDisplay:
            print("Processes created")
        else:
            print("At least one process not created")
          
    def __startProcesses(self):
        print("Starting processes")
        #print("Backend attributes: ", self.__dict__.keys())
        #print("p-rawData has: ", self.p_rawData.__dict__.keys())
        #print("p-rawData has: ", dir(self.p_rawData))
        #
        self.p_rawData.start()
        #print("p_metrics has: ", self.p_metrics.__dict__.keys())
        #print("p_metrics has: ", dir(self.p_metrics))
        self.p_metrics.start()
        self.p_saveAndDisplay.start()
        print("All processes running")
    
    #### MUGGLE METHODS #### 
    def start(self):
        pass
    
    def stop(self):
        pass
    
    '''
    def start(self):
        if not self.running:
            self.stream_threads = []
            self.thread_queues = []
            self.processed_queues = []
            self.running = True
            self._find_streams()
            # Limit to 4 devices if more are detected.
            if len(self.inlets) > 4:
                pass
            for index, inlet in enumerate(self.inlets):
                self.thread_queues.append(queue.Queue())
                stream_thread = threading.Thread(target=self._stream_data, args=(inlet, index), daemon=True)
                self.stream_threads.append(stream_thread)
                stream_thread.start()
            self._start_processing_threads()
            self.aggregation_thread = threading.Thread(target=self._aggregate_data, daemon=True)
            self.aggregation_thread.start()

    def stop(self):
        if self.running:
            self.running = False
            for thread in self.stream_threads:
                thread.join()
    '''

#### Vulgar Method - They Have no class ####
def prep_rawData(q_rawData, q_commandsForRawData, q_settingsForRawData):
    rd = RawData(q_rawData, q_commandsForRawData, q_settingsForRawData)
    rd.start()
   
def prep_metrics(q_rawData, q_metricdata, q_commandsForMetrics, q_settingsForMetrics):
    met = Metrics(q_rawData, q_metricdata, q_commandsForMetrics, q_settingsForMetrics)
    met.start()
    
def prep_saveAndDisplay(q_metricdata, q_toFrontEnd, q_commandsForSAD, q_settingsForSAD):
    sad = SaveAndDisplay(q_metricdata, q_toFrontEnd, q_commandsForSAD, q_settingsForSAD)
    sad.start()   
    
#### MAIN #### (just for testing independently of everything else)
def main():
    q_settings = multiprocessing.Queue()
    q_commands = multiprocessing.Queue()
    q_data = multiprocessing.Queue()
    
    import configparser
    config = configparser.ConfigParser()
    config.read("config.ini")
    
    backend = BackEnd(q_settings, q_commands, q_data, config)
    backend.start()

if __name__ == '__main__':
    main()