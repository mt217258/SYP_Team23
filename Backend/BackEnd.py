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
import keyboard
# CUSTOM #

#### CLASSES ####
class BackEnd():
    #### MAGIC METHODS ####
    def __init__(self, q_settings, q_commands, q_data):
        self.q_settings = q_settings
        self.q_commands = q_commands
        self.q_data = q_data
        self.running = False
        self.stream_threads = [] # List of stream threads
        self.inlets = [] # List of StreamInlet objects
        self.channels = [] # Channel Labels from XML
    
    #### MANGELED METHODS #### 
    def _parse_xml(self, xml_string):
        root = ET.fromstring(xml_string)
        self.channels = [channel.find('label').text for channel in root.find(".//channels")]
        print("I am in parse_xml")
        print(f"Extracted Channels: {self.channels}")
    
    def _find_streams(self):
        print("Looking for an OpenSignals stream...")
        streams = resolve_streams()
        streams = [s for s in streams if s.name() == 'OpenSignals']
        if not streams:
            print("No OpenSignals stream found.")
            return

        for stream in streams:
            inlet = StreamInlet(stream)
            self.inlets.append(inlet)
            print(f"Stream connected: {stream.name()}")

            # Get XML metadata and parse
            xml_string = inlet.info().as_xml()
            self._parse_xml(xml_string)

    def _stream_data(self, inlet, index):
        print(f"Streaming started for inlet {index}. Press Ctrl+C to stop")

        filename = f"lsl_data_{index}.csv"
        file_exists = os.path.exists(filename)

        with open(filename, mode ="w") as file:
            writer = None
            while self.running:
                sample, timestamp = inlet.pull_sample(timeout=0.01)
                if sample:
                    data_dict = dict(zip(["Time"] + self.channels, [timestamp] + sample))
                    df = pd.DataFrame([data_dict])
                    if not file_exists:
                        writer = df.to_csv(file, mode='w', header=True, index = False)
                        file_exists = True
                    else:
                        df.to_csv(file, mode='w', header=False, index = False)

                    self.q_data.put(data_dict) # data to the queue
                    print(f"Data from stream {index}: {data_dict}")
                time.sleep(0.001)
    #### MUGGLE METHODS #### 
    def start(self):
        if not self.running:
            self.running = True
            self.stream_threads = []
            self._find_streams()
            for index, inlet in enumerate(self.inlets):
                stream_thread = threading.Thread(target=self._stream_data, args=(inlet, index), daemon=True)
                self.stream_threads.append(stream_thread)
                stream_thread.start()

            print("LSL Stream started.")
    
    def stop(self):
        if self.running:
            self.running = False
            for thread in self.stream_threads:
                thread.join()
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

        if keyboard.is_pressed('ctrl+q'):
            print("Exiting program gracefully...")
            backend.stop()
            break


if __name__ == '__main__':
    main()
