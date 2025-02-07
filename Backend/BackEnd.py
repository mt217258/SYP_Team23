'''
Author:  Will Thornton          
Contact: wl939708@dal.ca
Description: Backend program to read data from the Lab Streaming Layer (LSL) place data in .csv file and process data to place in queue for front end.
TODO List:   

print data into csv, currently putting the data into seperate csv
Check if I can read four channels of data
filter/process data for queue
Accept commands to alter how processing is done
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
import csv
# CUSTOM #

#### CLASSES ####
class BackEnd():
    #### MAGIC METHODS ####
    def __init__(self, q_settings, q_commands, q_data, output_filename="lsl_data.csv"):
        self.q_settings = q_settings
        self.q_commands = q_commands
        self.q_data = q_data
        self.running = False
        self.stream_threads = [] # List of stream threads
        self.inlets = [] # List of StreamInlet objects
        self.channels = [] # Channel Labels from XML
        self.output_filename = output_filename
        self.headers_written = False
    
    #### MANGELED METHODS #### 
    def _parse_xml(self, xml_string, stream_index):
        root = ET.fromstring(xml_string)
        channels = [channel.find('label').text for channel in root.find(".//channels")]
        self.channels.append(channels)
        print(f"Extracted Channels {stream_index} - Extracted Channels: {channels}")
    
    def _find_streams(self):
        print("Looking for an OpenSignals stream...")
        streams = resolve_streams()
        streams = [s for s in streams if s.name() == 'OpenSignals']
        if not streams:
            print("No OpenSignals stream found.")
            return

        for index, stream in enumerate(streams):
            inlet = StreamInlet(stream)
            self.inlets.append(inlet)
            print(f"Stream {index} connected: {stream.name()}")

            # Get XML metadata and parse
            xml_string = inlet.info().as_xml()
            self._parse_xml(xml_string, index)

    def _stream_data(self, inlet, index):
        print(f"Streaming started for inlet {index}. Press 'ctrl+q' to stop")

        self.output_filename = "lsl_data.csv"  # Single CSV file
        file_exists = os.path.exists(self.output_filename)

        # Ensure we have all unique headers across streams
        all_channels = ["Time", "nSeq"]
        for stream_channels in self.channels:
            all_channels.extend([ch for ch in stream_channels if ch not in all_channels])

        with open(self.output_filename, mode="a", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=all_channels)

            # Only write header once
            if not file_exists:
                writer.writeheader()

            while self.running:
                result = inlet.pull_chunk(timeout=0.01)
                if result is None:
                    continue

                sample, timestamps = result
                if not sample or not timestamps:
                    continue

                if sample:
                    for sample, timestamp in zip(sample, timestamps):
                        data_dict = {"Time": timestamp, "nSeq": index}  # Shared fields
                        for ch, value in zip(self.channels[index], sample):
                            data_dict[ch] = value  # Correctly map values to respective channels

                        # Ensure missing values are represented as empty fields
                        for field in all_channels:
                            if field not in data_dict:
                                data_dict[field] = ""  

                        writer.writerow(data_dict)
                        self.q_data.put(data_dict)
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
        except queue.Empty:
            print("No data received.")

        if keyboard.is_pressed('ctrl+q'):
            print("Exiting program gracefully...")
            backend.stop()
            break


if __name__ == '__main__':
    main()
