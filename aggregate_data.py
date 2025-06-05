'''
Author:             Matthew McLaughlin
Contact:            
Description:        Backend component to be run in a thread to merge data
                    before being saved down or displayed in the front end
TODO List:  

Notes
    
'''

#### LIBRARIES ####
# OFF THE SHELF #
import pandas as pd
import multiprocessing

import time
# CUSTOM #

# Global Vars
NUM_SENSORS = 1
NUM_FAILRX = 5

#### CLASSES ####
class Aggregator():
    #### MAGIC METHODS ####
    def __init__(self, qs_data, q_metric, q_command, q_feedback):
        self.qs_data = qs_data
        self.q_dataOut = q_metric
        self.q_command = q_command
        self.q_feedback = q_feedback
        
        self.notDead = False
        
        self.mergedRawData = pd.DataFrame()
        self.num_pullFailures = [0]*NUM_SENSORS #got tracking unmber of times a sensor has 
                                                #been polled and failed to send data

    #### MANGELED METHODS ####
    def __processCommand(self):
        command = self.q_commandIn.get(timeout=0.1)
    
        print("Rx'd command: ", command)
    
        match command:
            case "Stream":
                self.isStreaming = True
                print("Aggregate: Stream")
            case "Stop":
                self.isStreaming = False
                print("Aggregate: Don't Stream")
            case _:
                print("Unknown command: ", command)   
    
    def __forwardMergedData(self):
        self.q_dataOut.put(self.mergedRawData)
        self.mergedRawData.iloc[:0] #empty dataframe
    
    #### MUGGLE METHODS #### 
    def getAndMerge(self):
        for index, q in enumerate(self.qs_data):
            if not q.empty() :
                self.num_pullFailures[index] = 0
                temp_data = q.get()
                print("Data rcvd: ", temp_data )
                self.mergedRawData = self.mergedRawData.merge(temp_data, how='outer', on='Time')
            else:
                self.num_pullFailures[index] += 1
                if self.num_pullFailures[index] > NUM_FAILRX:
                    self.q_feedback.put("Reconnect:{index}".format(num=index)) #let BE know to try to reconnect sensor
    
    def start(self):
        print("Aggregator thread started")
        while(self.notDead):
            if self.stream: #does the stream exist
                if not self.q_commandIn.empty(): #if there is a command
                    print(self.name, ": Command received")
                    self.__processCommand()
                    
                self.getAndMerge()
                self.__forwardMergedData()    
                

#### VULGAR METHODS #### they have no class
def make_thread_AggregateData(qs_data, q_metric, q_command, q_feedback):
    aggr = Aggregator(qs_data, q_metric, q_command, q_feedback)  
    aggr.start()
    
#### MAIN #### (just for testing independently of everything else)
def main():
    print("Aggregator: Start Main")
    
    qs_data = []
    qs_simSensorCommand = []
    for index in range(NUM_SENSORS):
        qs_data.append(multiprocessing.Queue())
        qs_simSensorCommand.append(multiprocessing.Queue())
        
    q_metric = multiprocessing.Queue()
    q_commandIn = multiprocessing.Queue()
    q_feedback = multiprocessing.Queue()
    
    import threading
    my_threads = []
    #create aggregatpr thread
    my_threads.append(  threading.Thread( target=make_thread_AggregateData, 
                                          args=(qs_data,q_metric,q_commandIn,q_feedback,), 
                                          daemon=True
                                        )
                     )
    #create sim sensor threads
    from sensor_sim import make_thread_sensor
    
    MACs = ["58:8E:81:A2:48:D3", "60:77:71:82:92:C9", "58:8E:81:A2:49:02","5C:02:72:9F:4E:4C" ]
    sides = ["L", "L", "R", "R"]
    sensorTypes = ["sEMG", "EDA", "sEMG", "EDA"]
    chunksize = 5  
    
    for index in range(NUM_SENSORS):
        my_threads.append(  threading.Thread( target=make_thread_sensor, 
                                              args=(sides[index], 
                                                    sensorTypes[index], 
                                                    MACs[index], 
                                                    chunksize, 
                                                    qs_simSensorCommand[index], 
                                                    qs_data[index],), 
                                              daemon=True
                                            )
                         )

    #start running threads
    for thred in my_threads:
        thred.start()

    import keyboard
    import time
    
    while True:
        readKey = keyboard.read_key()
        time.sleep(2)
        
        match readKey:
            case "esc":
                break
            case "1": 
                print("Sending message: Stream")
                q_commandIn.put("Stream")
                
                for q in qs_simSensorCommand:
                    q.put("Stream")
            case "2": 
                print("Sending message: Stop")
                q_commandIn.put("Stop")
                
                for q in qs_simSensorCommand:
                    q.put("Stop")
            case "3": 
                print("Sending message: Reconnect")
                #q_commandIn.put("Reconnect")
                
                for q in qs_simSensorCommand:
                    q.put("Stream")
            case _:
                print("Unknown key press: ", readKey)     

        if not q_metric.empty():
            mergedData = q_metric.get()
            print("Merged data rcd: ", mergedData)

    print("Aggregator: Ending Main")

if __name__ == '__main__':
    main()

