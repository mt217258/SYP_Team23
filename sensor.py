'''
Author:             Matthew McLaughlin
Contact:            
Description:        Backend component to manage data collection
TODO List:  

Notes
    https://github.com/labstreaminglayer/pylsl/blob/main/src/pylsl/inlet.py
    stream.name() = OpenSignals
    stream.type() = MAC
    inlet = StreamInlet(stream)
    inlet.info().get_channel_labels() = headers for sample
    inlet.time_corection add this to timestamp to correct for drift
    
'''

#### LIBRARIES ####
# OFF THE SHELF #
from pylsl import StreamInlet, resolve_streams
import pandas as pd
import multiprocessing
from math import sqrt, pow
import time
import traceback

# CUSTOM #

#### CLASSES ####
class Sensor():
    #### MAGIC METHODS ####
    def __init__(self, side, sensorType, MAC, chunksize, q_commandIn, q_dataOut):
        self.side = side
        self.type = sensorType
        self.name =  f"{self.type}_{self.side}" 
        self.MAC = MAC
        self.q_commandIn = q_commandIn
        self.q_dataOut = q_dataOut
        
        self.isStreaming = False
        self.notDead = True
        
        self.chunksize = chunksize
        self.streamTimeout = 1
        
        self.__findStream()
        
        self.blankData = pd.DataFrame()
        #self.__buildBlankFrame()
        self.indexmapping = {} #dict for mapping meas using index
        self.__findDataIndices()
    
    #### MANGELED METHODS ####
    def __findDataIndices(self): #build map for mapping data later into DataFrame
        if self.stream:
            possible_labels = ["EMG0", "gACC1", "gACC2", "gACC3", "RAW0"]
            channel_labels = self.inlet.info().get_channel_labels()
            
            for label in possible_labels:
                if label in channel_labels: 
                    self.indexmapping[label] = channel_labels.index(label)
                    
    def __findStream(self):
        print("Looking for stream for MAC:", self.MAC)
        self.stream = False
        
        all_streams = resolve_streams()
        
        for stream in all_streams:
            if stream.name() == 'OpenSignals' and stream.type() == self.MAC:
                self.stream = stream
                self.inlet = StreamInlet(stream)
                print("Found stream for MAC:", self.MAC)
                break
        
        if not self.stream: #check if stream exists
            print("Stream not found for MAC: ", self.MAC)
    
    def __processCommand(self):
        command = self.q_commandIn.get(timeout=0.1)
    
        print("Rx'd command: ", command)
    
        match command:
            case "Stream":
                self.isStreaming = True
            case "Stop":
                self.isStreaming = False
            case "Reconnect":
                self.__findStream()
            case _:
                print("Unknown command: ", command)       
   
    def __mapChunkToDataFrame(self, rawData):
        #print("Mapping chunk")
        #print("Raw chunk: ", rawData)
        
        blankDict = {}
        blankDict["Time"] = []
        match self.type:
            case "sEMG":
                blankDict[f"raw-sEMG_{self.side}"] = []
                blankDict[f"raw-ACC_{self.side}"] = []
            case "EDA":
                blankDict[f"raw-EDA_{self.side}"] = []
            case _:
                print("Unknown sensor type")
        
        for index, sample in enumerate(rawData[0]):
            blankDict["Time"].append(rawData[1][index])
        
            match self.type:
                case "sEMG":
                    blankDict[f"raw-sEMG_{self.side}"].append(sample[self.indexmapping["EMG0"]])
                    
                    accX = sample[self.indexmapping["gACC1"]]
                    accY = sample[self.indexmapping["gACC2"]]
                    accZ = sample[self.indexmapping["gACC3"]]
                    acc = sqrt(pow(accX,2) + pow(accY,2) + pow(accZ,2))
                    blankDict[f"raw-ACC_{self.side}"].append(acc)
                case "EDA":
                    blankDict[f"raw-EDA_{self.side}"].append(sample[self.indexmapping["RAW0"]])
                case _:
                    print("Unknown sensor type")    
            
            mappedData = pd.DataFrame(data=blankDict) 
        return mappedData
    
    def __mapSampleToDataFrame(self, rawData):
        #print("Mapping sample")
        blankDict = {}
        
        sample = rawData[0]
        blankDict["Time"] = rawData[1]
                
        match self.type:
            case "sEMG":
                blankDict[f"raw-sEMG_{self.side}"] = sample[self.indexmapping["EMG0"]]
                
                accX = sample[self.indexmapping["gACC1"]]
                accY = sample[self.indexmapping["gACC2"]]
                accZ = sample[self.indexmapping["gACC3"]]
                
                acc = sqrt(pow(accX,2) + pow(accY,2) + pow(accZ,2))
                
                blankDict[f"raw-ACC_{self.side}"] = acc
            case "EDA":
                blankDict[f"raw-EDA_{self.side}"] = sample[self.indexmapping["RAW0"]]
            case _:
                print("Unknown sensor type")
        
        mappedData = pd.DataFrame(data=blankDict)                                                  
        return mappedData
    
    #### MUGGLE METHODS #### 
    def getSample(self):
        try:
            rawSample = self.inlet.pull_sample()
            #print("rawSample: ", rawSample)
            #time.sleep(1)
            sample = self.__mapSampleToDataFrame(rawSample)
            return sample
        except:
            print("Sample request failed")
            return None    
     
    def getChunk(self):
        try:
            rawChunk = self.inlet.pull_chunk(self.streamTimeout, self.chunksize)
            chunk = self.__mapChunkToDataFrame(rawChunk)
            return chunk
        except:
            print("Chunk request failed")
            traceback.print_exc()
            return None 
        

    def start(self):
        while(self.notDead):
            if self.stream: #does the stream exist
                if not self.q_commandIn.empty(): #if there is a command
                    print(self.name, ": Command received")
                    self.__processCommand()
                if self.isStreaming: 
                    self.q_dataOut.put(self.getChunk()) #get data and send to metrics
                    #print("Sample: ", self.getSample())
            else:
                print(self.name, ": Not streaming")
                time.sleep(1)
                    

#### VULGAR METHODS #### (they have no class)
def make_thread_sensor( side:str, sensorType:str, MAC:str,
                        chunksize:int, 
                        q_commandIn:multiprocessing.Queue, 
                        q_dataOut:multiprocessing.Queue):
    
    #print("Inputs are: ", side, sensorType, MAC, q_commandIn, q_dataOut)
    
    sensor = Sensor(side, sensorType, MAC, chunksize, q_commandIn, q_dataOut)
    #sensor.isStreaming = True #TODO - remove after command handling added
    sensor.start()
    
    #print("Sample: ", sensor.getSample())
    #print("Chunk: ", sensor.getChunk())
 
#### MAIN #### (just for testing independently of everything else)
def main():
    print("Sensor: Starting Main")
    MACs = ["58:8E:81:A2:48:D3", "60:77:71:82:92:C9", "58:8E:81:A2:49:02","5C:02:72:9F:4E:4C" ]
    sides = ["L", "L", "R", "R"]
    sensorTypes = ["sEMG", "EDA", "sEMG", "EDA"]
    chunksize = 5
    
    selection = 1 #for picking which snesor to connect to
    
    #side = "L"
    #sensorType = "sEMG"
    #MAC = "58:8E:81:A2:48:D3"
    q_commandIn = multiprocessing.Queue()
    q_dataOut = multiprocessing.Queue()
    
    #sensor = Sensor(side, sensorType, MAC, chunksize, q_commandIn, q_dataOut)
    #print("Sample: ", sensor.getSample())
    #print("Chunk: ", sensor.getChunk())

    print("Inputs are: ",   sides[selection], sensorTypes[selection], 
                            MACs[selection], q_commandIn, q_dataOut)

    import threading
    thread_sensor_test = threading.Thread(  target=make_thread_sensor, 
                                            args=(sides[selection], sensorTypes[selection], 
                                                  MACs[selection], chunksize, 
                                                  q_commandIn, q_dataOut,), 
                                            daemon=True
                                          )
    thread_sensor_test.start()
    
    import keyboard
    
    while True:
        readKey = keyboard.read_key()
        time.sleep(2)
        
        match readKey:
            case "esc":
                break
            case "1": 
                print("Sending message: Stream")
                q_commandIn.put("Stream")
            case "2": 
                print("Sending message: Stop")
                q_commandIn.put("Stop")
            case "3": 
                print("Sending message: Reconnect")
                q_commandIn.put("Reconnect")
            case _:
                print("Unknown key press: ", readKey)     

    print("Sensor: Ending Main")

if __name__ == '__main__':
    main()