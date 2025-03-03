'''
Author:  Will Thornton          
Contact: wl939708@dal.ca
Description: Backend program to read data from the Lab Streaming Layer (LSL) place data in .csv file and process data to place in queue for front end.
TODO List:   

filter/process data for queue
Accept commands to alter how processing is done
Data format: data = pd.DataFrame(data={"Time":[], "sEMG_L":[], "sEMG_R":[]})
       
'''
# Test push in Will Thornton
#### LIBRARIES ####
# OFF THE SHELF #
from logging import Manager
import multiprocessing
import pandas as pd
import threading
from pylsl import StreamInlet, resolve_streams
#from consume_lsl import consume_and_write_to_csv
import xml.etree.ElementTree as ET # Parsing channel data
import time
import os
import keyboard
import csv
import queue
from queue import Empty

# CUSTOM #

#### CLASSES ####
class BackEnd():
    #### MAGIC METHODS ####
    def __init__(self, q_settings, q_commands):
        self.q_settings = q_settings
        self.q_commands = q_commands
        self.running = False
        self.stream_threads = [] # List of stream threads
        self.queue_writer_threads = []
        self.inlets = [] # List of StreamInlet objects
        self.channels = [] # Channel Labels from XML
        self.q_data_per_stream = {}
        self.mac_addresses = {}
        self.csv_lock = {} 
    
    #### MANGELED METHODS #### 
    def _parse_xml(self, xml_string, stream_index):
        root = ET.fromstring(xml_string)

        mac_element = root.find(".//type")
        if mac_element is not None:
            mac_address = mac_element.text.strip().replace(":", "_")
            self.mac_addresses[stream_index] = mac_address
            print(f"MAC Address for stream {stream_index}: {mac_address}")
        else:
            mac_address = f"stream_{stream_index}"
            print(f"No MAC Address found in stream {stream_index}, using default name.")

        channels = [channel.find('label').text for channel in root.find(".//channels")]
        self.channels.append(channels)
        print(f"Extracted Channels {stream_index}: {channels}")
    
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

        mac_address = self.mac_addresses.get(index, f"stream_{index}")
        filename = f"{mac_address}.csv"
        file_exists = os.path.exists(filename)

        with open(filename, mode="a", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["Time"] + self.channels[index])

            # Only write header once
            if not file_exists:
                writer.writeheader()

            all_channels = ["Time"] + self.channels[index]
            q_data = self.q_data_per_stream[index]

            while self.running:
                samples, timestamps = inlet.pull_chunk(timeout = 0.001)
                if not samples or not timestamps:
                    continue

                for sample, timestamp in zip(samples, timestamps):
                    data_dict = {"Time": timestamp, "nSeq": index}
                    for ch, value in zip(self.channels[index], sample):
                        data_dict[ch] = value
                    with self.csv_lock[index]:
                        writer.writerow(data_dict)

                    q_data.put(data_dict)

                    print(f"Data from stream {index}: {data_dict}")

    def _write_queue_data_to_csv(self, index):
        filename = f"data_{index}.csv"
        file_exists = os.path.exists(filename)

        with open(filename, mode="a", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["Time"] + self.channels[index])

            if not file_exists:
                writer.writeheader()

            q_data = self.q_data_per_stream[index]
            while self.running:
                try:
                    data_dict = q_data.get(timeout=0.1)
                    if data_dict is None:
                        break
                    lock = self.csv_lock[index]
                    with lock:
                        writer.writerow(data_dict)
                except Empty:
                    continue

    #### MUGGLE METHODS #### 
    def start(self):
        if not self.running:
            self.stream_threads = []
            self.running = True
            self._find_streams()

            # Start stream threads
            for index, inlet in enumerate(self.inlets):
                self.q_data_per_stream[index] = queue.Queue()
                self.csv_lock[index] = threading.Lock()

                stream_thread = threading.Thread(target=self._stream_data, args=(inlet, index), daemon=True)
                self.stream_threads.append(stream_thread)
                stream_thread.start()

                # Start data writing thread for individual queue data
                queue_writer_thread = threading.Thread(target=self._write_queue_data_to_csv, args=(index,), daemon=True)
                self.queue_writer_threads.append(queue_writer_thread)
                queue_writer_thread.start()

            print("LSL Stream started and data logging in progress.")

    
    def stop(self):
        if self.running:
            self.running = False
            for index in self.q_data_per_stream:
                self.q_data_per_stream[index].put(None)
            for thread in self.stream_threads:
                thread.join()
            print("LSL Stream stopped.")

#### MAIN #### (just for testing independently of everything else)
def main():
    with multiprocessing.Manager() as manager:
        q_settings = manager.Queue()
        q_commands = manager.Queue()

        backend = BackEnd(q_settings, q_commands)
        backend.start()

        #csv_process = multiprocessing.Process(target=consume_and_write_to_csv, args=(q_data, backend.output_filename_data))
        #csv_process.start()

        try:
            while True:
                if keyboard.is_pressed('ctrl+q'):
                    print("Exiting program gracefully...")
                    break
        except KeyboardInterrupt:
            print("KeyboardInterrupt detecte. Stopping processes....")

        backend.stop()

        #q_data.put(None)
        #csv_process.join()

        print("Main process exiting after CSV writer finishes.")


if __name__ == '__main__':
    main()
