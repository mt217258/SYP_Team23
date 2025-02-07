'''
Author:  Will Thornton          
Contact: wl939708@dal.ca
Description: Backend program to read data from the Lab Streaming Layer (LSL) place data in .csv file and process data to place in queue for front end.
TODO List:   

print data into csv
Read in more than one channel of data
filter/process data for queue
Accept input to alter how processing is done
Data format: data = pd.DataFrame(data={"Time":[], "sEMG_L":[], "sEMG_R":[]})
       
'''
# Test push in Will Thornton
#### LIBRARIES ####
# OFF THE SHELF #
import queue
import pandas as pd
import threading
from pylsl import StreamInlet, resolve_streams
import xml.etree.ElementTree as ET # Parsing channel data
import time
import os
# CUSTOM #

#### CLASSES ####
class BackEnd():
    #### MAGIC METHODS ####
    def __init__(self, q_settings, q_commands, q_data):
        self.q_settings = q_settings
        self.q_commands = q_commands
        self.q_data = q_data
        self.running = False
        self.stream_thread = None # Thread for streaming
        self.inlet = None
        self.channels = [] # Channel Labels from XML
    
    #### MANGELED METHODS #### 
    def _parse_xml(self, xml_string):
        root = ET.fromstring(xml_string)
        self.channels = [channel.find('label').text for channel in root.find(".//channels")]
        print("I am in parse_xml")
        print(f"Extracted Channels: {self.channels}")
    
    def _find_stream(self):
        print("Looking for an OpenSignals stream...")
        streams = resolve_streams()
        streams = [s for s in streams if s.name() == 'OpenSignals']
        if not streams:
            print("No OpenSignals stream found.")
            return

        self.inlet = StreamInlet(streams[0])
        print("Stream connected!")

        # Get XML metadata and parse
        xml_string = self.inlet.info().as_xml()
        self._parse_xml(xml_string)

    def _stream_data(self):
        self._find_stream()
        print("Streaming started. Press Ctrl+C to stop")

        filename = "lsl_data.csv"
        file_exists = os.path.exists(filename)

        with open(filename, mode ="w") as file:
            while self.running:
                sample, timestamp = self.inlet.pull_sample(timeout=0.01)
                if sample:
                    data_dict = dict(zip(["Time"] + self.channels, [timestamp] + sample))

                    df = pd.DataFrame([data_dict])

                    df.to_csv(file, mode='w', header=not file_exists, index = False)

                    self.q_data.put(data_dict) # data to the queue
                    print(data_dict)
                time.sleep(0.001)
    #### MUGGLE METHODS #### 
    def start(self):
        if not self.running:
            self.running = True
            self.stream_thread = threading.Thread(target=self._stream_data, daemon=True)
            self.stream_thread.start()
            print("LSL Stream started.")
    
    def stop(self):
        if self.running:
            self.running = False
            self.stream_thread.join()
            print("LSL Stream stopped.")

#### MAIN #### (just for testing independently of everything else)
def main():
    q_settings = queue.Queue()
    q_commands = queue.Queue()
    q_data = queue.Queue()

    backend = BackEnd(q_settings, q_commands, q_data)
    backend.start()

    while True:
        try:
            sample = q_data.get(timeout=0.1)
            #print("Received: ", sample)
        except queue.Empty:
            print("No data received.")

    backend.stop()


if __name__ == '__main__':
    main()
