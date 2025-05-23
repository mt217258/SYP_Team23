'''
Author:             Matthew McLaughlin/Will Thornton
Contact:            
Description:        Backend component to manage data collection
TODO List:          
'''

#### LIBRARIES ####
# OFF THE SHELF #
#from pylsl import StreamInlet, resolve_streams
#import xml.etree.ElementTree as ET  # Parsing channel data
import configparser
import pandas as pd
import queue
#from matplotlib import streamplot
#from future.backports.test.pystone import TRUE
# CUSTOM #

class RawData():
    #### MAGIC METHODS ####
    def __init__(self, q_rawData, q_commandsForRawData, q_settingsForRawData):
        #link main queues
        print("rD - Hello World")
        self.q_send_RawData = q_rawData
        self.q_rcv_commandsForRawData = q_commandsForRawData
        self.q_rcv_q_settingsForRawData = q_settingsForRawData
        
        self.isStreaming = False
        self.settings = configparser.ConfigParser()
    
        self.__linkThreads()
    
    def __linkThreads(self):
        pass
    
    def start(self):
        pass
    
    '''    
    def __findStreams(self): #find OS streams
        all_streams = resolve_streams()
        unique_streams = {}
        
        #look for unique OS streams
        for stream in all_streams:
            if stream.name() == 'OpenSignals':
                inlet = StreamInlet(stream)
                xml = inlet.info().as_xml()
                mac = ET.fromstring(xml).find(".//type").text.strip()
                unique_streams[mac] = stream
        if not unique_streams: #if no streams found, exit
            return
        
        #
        self.inlets = []
        for index, (mac, stream) in enumerate(unique_streams.items()):
            #if index >= 4:
            #    break
            inlet = StreamInlet(stream)
            self.inlets.append(inlet)
            self.thread_queues.append(queue.Queue())
            xml_string = inlet.info().as_xml()
            
            self._parse_xml(xml_string, index)
            self._debug_lsl(inlet)   

    def _parse_xml(self, xml_string, stream_index):
        root = ET.fromstring(xml_string)
        mac_element = root.find(".//type")
        if mac_element is not None:
            mac_address = mac_element.text.strip().replace(":", "_")
            if mac_address == "5C_02_72_9F_4E_4C":
                mac_address = "EDA_R"
            elif mac_address == "60_77_71_82_92_C9":
                mac_address = "EDA_L"
            elif mac_address == "58_8E_81_A2_49_02":
                mac_address = "sEMG_R"
            elif mac_address == "58_8E_81_A2_48_D3":
                mac_address = "sEMG_L"
            self.mac_addresses[stream_index] = mac_address
        else:
            mac_address = f"stream_{stream_index}"
        channels = []
        for channel in root.findall(".//channels/channel"):
            label = channel.find('label').text
            #if label == "nSeq":
            #continue
            if label == "EDABITREV0":
                label = "raw"
            elif label == "EMG0":
                label = "raw"
            channel_name = f"{label}-{mac_address}"
            channels.append(channel_name)
        print("All cahnnesl for stream:", channels)
        self.channels.append(channels)

    def _debug_lsl(self, inlet):
        # Debug prints removed
        sample, timestamp = inlet.pull_sample(timeout=2.0)
        print("Timestamp: ", timestamp, " Sample: ", sample)
        # (No output printed)

    def start(self):
        self.running = True
        
        self.stream_threads = []
        self.thread_queues = []
        
        self.__findStreams()
    '''
        '''
        while self.running:
            if not self.q_rcv_commandsForRawData.empty(): #check for command
                self.readCommand()
            else: #otherwise keep 
                if self.isStreaming: 
                    #self.data = self.collectData()
                    #self.q_rcv_q_settingsForRawData.put(self.data)
        '''
        
    def collectData(self):
        temp_data = pd.DataFrame()
        for sensor in self.sensors:
            pass  
               
    def stop(self):
        self.isStreaming = False
        self.running = False 
        
    def readCommand(self):
        command = self.q_rcv_commandsForRawData.get()
        
        match command:
            case "Stream":
                self.isStreaming = True
                self.settings = self.q_rcv_q_settingsForRawData.get()
                self.startStreaming()
            case "Stop":
                self.stop()
    
    #### THREADS ####
    
    
    #### MANGELED METHODS ####
    
    
    '''
    def _parse_xml(self, xml_string, stream_index):
        root = ET.fromstring(xml_string)
        mac_element = root.find(".//type")
        if mac_element is not None:
            mac_address = mac_element.text.strip().replace(":", "_")
            if mac_address == "5C_02_72_9F_4E_4C":
                mac_address = "EDA_R"
            elif mac_address == "60_77_71_82_92_C9":
                mac_address = "EDA_L"
            elif mac_address == "58_8E_81_A2_49_02":
                mac_address = "sEMG_R"
            elif mac_address == "58_8E_81_A2_48_D3":
                mac_address = "sEMG_L"
            self.mac_addresses[stream_index] = mac_address
        else:
            mac_address = f"stream_{stream_index}"
        channels = []
        for channel in root.findall(".//channels/channel"):
            label = channel.find('label').text
            #if label == "nSeq":
            #continue
            if label == "EDABITREV0":
                label = "raw"
            elif label == "EMG0":
                label = "raw"
            channel_name = f"{label}-{mac_address}"
            channels.append(channel_name)
        print("All cahnnesl for stream:", channels)
        self.channels.append(channels)


    def _find_streams(self):
        all_streams = resolve_streams()
        unique_streams = {}
        for stream in all_streams:
            if stream.name() == 'OpenSignals':
                inlet = StreamInlet(stream)
                xml = inlet.info().as_xml()
                mac = ET.fromstring(xml).find(".//type").text.strip()
                unique_streams[mac] = stream
        if not unique_streams:
            return
        self.inlets = []
        for index, (mac, stream) in enumerate(unique_streams.items()):
            if index >= 4:
                break
            inlet = StreamInlet(stream)
            self.inlets.append(inlet)
            self.thread_queues.append(queue.Queue())
            xml_string = inlet.info().as_xml()
            self._parse_xml(xml_string, index)
            self._debug_lsl(inlet)

    def _debug_lsl(self, inlet):
        # Debug prints removed
        sample, timestamp = inlet.pull_sample(timeout=2.0)
        # (No output printed)
        
    def _aggregate_data(self):
        batch_counter = 0
        while self.running:
            try:
                for i, q in enumerate(self.processed_queues):
                    while not q.empty():
                        try:
                            data = q.get_nowait()
                            if not data.empty:
                                data['stream_id'] = i
                                self.q_data.put(data)
                                batch_counter += 1
                        except queue.Empty:
                            break
                time.sleep(0.01)
            except Exception as e:
                traceback.print_exc()
                time.sleep(0.1)
    '''
    #### MUGGLE METHODS #### 
    
        
#### MAIN #### (just for testing independently of everything else)
def main():
    pass

if __name__ == '__main__':
    main()