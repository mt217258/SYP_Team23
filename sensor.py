'''
Author:             Matthew McLaughlin/Will Thornton
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

import traceback
# CUSTOM #

#### CLASSES ####
class Sensor():
    #### MAGIC METHODS ####
    def __init__(self, side, sensorType, MAC, q_commandIn, q_dataOut):
        self.side = side
        self.type = sensorType
        self.name =  f"{self.type}_{self.side}" 
        self.MAC = MAC
        self.q_commandIn = q_commandIn
        self.q_dataOut = q_dataOut
        
        self.isStreaming = False
        self.notDead = True
        
        self.chunksize = 5
        self.streamTimeout = 1
        
        self.__findStream()
        
        self.blankData = pd.DataFrame()
        self.__buildBlankFrame()
        self.indexmapping = {} #dict for mapping meas using index
        self.__findDataIndices()
    
    def __findDataIndices(self): #build map for mapping data later into DataFrame
        if self.stream:
            possible_labels = ["EMG0", "gACC1", "gACC2", "gACC3", "EDABITREV0"]
            channel_labels = self.inlet.info().get_channel_labels()
            
            for label in possible_labels:
                if label in channel_labels: 
                    self.indexmapping[label] = channel_labels.index(label)
                
    def __buildBlankFrame(self):
        self.blankData["Time"] = []
        
        match self.type:
            case "sEMG":
                self.blankData[f"raw-sEMG_{self.side}"] = []
                self.blankData[f"raw-ACC_{self.side}"] = []
            case "EDA":
                self.blankData[f"raw-EDA_{self.side}"] = []
    
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
        pass
        '''
        command = self.q_commandIn.
    
        match command:
            case :
                pass
        '''
   
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
                    blankDict[f"raw-EDA_{self.side}"].append(sample[self.indexmapping["EDABITREV0"]])
                case _:
                    print("Unknown sensor type")    
            
            mappedData = pd.DataFrame(data=blankDict) 
        return mappedData
    
    def __mapSampleToDataFrame(self, rawData):
        #print("Mapping sample")
        blankDict = {}
        
        sample = rawData[0]
        blankDict["Time"] = [rawData[1]]
                
        match self.type:
            case "sEMG":
                blankDict[f"raw-sEMG_{self.side}"] = sample[self.indexmapping["EMG0"]]
                
                accX = sample[self.indexmapping["gACC1"]]
                accY = sample[self.indexmapping["gACC2"]]
                accZ = sample[self.indexmapping["gACC3"]]
                
                acc = sqrt(pow(accX,2) + pow(accY,2) + pow(accZ,2))
                
                blankDict[f"raw-ACC_{self.side}"] = acc
            case "EDA":
                blankDict[f"raw-EDA_{self.side}"] = sample[self.indexmapping["EDABITREV0"]]
            case _:
                print("Unknown sensor type")
        
        mappedData = pd.DataFrame(data=blankDict)                                                  
        return mappedData
    
    def getSample(self):
        if self.stream:
            try:
                rawSample = self.inlet.pull_sample()
                #print("rawSample: ", rawSample)
                sample = self.__mapSampleToDataFrame(rawSample)
                return sample
            except:
                print("Sample request failed")
                return None    
        else:
            print("Stream not found")
            return None
    
    def getChunk(self):
        if self.stream:
            try:
                rawChunk = self.inlet.pull_chunk(self.streamTimeout, self.chunksize)
                chunk = self.__mapChunkToDataFrame(rawChunk)
                return chunk
            except:
                print("Chunk request failed")
                traceback.print_exc()
                return None 
        else:
            print("Stream not found")
            return None

    def start(self):
        while(self.notDead):
            if self.stream: #does the stream exist
                if not self.q_commandIn.empty(): #if there is a command
                    self.__processCommand()
                if self.isStreaming(): 
                    self.q_dataOut.put(self.getChunk()) #get data and send to metrics

#### VULGAR METHODS #### (they have no class)
def thread_sensor(side, sensorType, MAC, q_commandIn, q_dataOut):
    sensor = Sensor(side, sensorType, MAC, q_commandIn, q_dataOut)
    sensor.start()
 
#### MAIN #### (just for testing independently of everything else)
def main():
    side = "L"
    sensorType = "sEMG"
    MAC = "58:8E:81:A2:48:D3"
    q_commandIn = multiprocessing.Queue()
    q_dataOut = multiprocessing.Queue()
    
    sensor = Sensor(side, sensorType, MAC, q_commandIn, q_dataOut)
    
    #print("Sample: ", sensor.getSample())
    #print("Chunk: ", sensor.getChunk())
    #TODO - move sensor into a thread

    import threading
    thread_sensor_test = threading.Thread()
    

if __name__ == '__main__':
    main()