import multiprocessing
from re import I
import pandas as pd
import threading
from pylsl import StreamInlet, resolve_streams
import xml.etree.ElementTree as ET  # Parsing channel data
import time
import os
import keyboard
import csv
import queue
from queue import Empty
import h5py
import numpy as np

class BackEnd():
    #### MAGIC METHODS ####
    def __init__(self, q_settings, q_commands, q_data, config):
        # Shared memory setup
        self.q_settings = q_settings
        self.q_commands = q_commands
        self.q_data = q_data
        self.config = config
        self.running = False
        self.mac_addresses = {}
        self.thread_queues = []
        self.stream_threads = []  # List of stream threads
        self.inlets = []  # List of StreamInlet objects
        self.channels = []  # Channel Labels from XML

    #### MANGELED METHODS ####
    def _parse_xml(self, xml_string, stream_index):
        root = ET.fromstring(xml_string)

        # Extract MAC address
        mac_element = root.find(".//type")
        if mac_element is not None:
            mac_address = mac_element.text.strip().replace(":", "_")  # Clean MAC address
            if mac_address == "5C_02_72_9F_4E_4C":
                mac_address = "EDA_R"
            elif mac_address == "60_77_71_82_92_C9":
                mac_address = "EDA_L"
            elif mac_address == "58_8E_81_A2_49_02":
                mac_address = "sEMG_R"
            elif mac_address == "58_8E_81_A2_48_D3":
                mac_address = "sEMG_L"
            print(f"MAC Address for stream {stream_index}: {mac_address}")
        else:
            mac_address = f"stream_{stream_index}"  # Default name if MAC is not found
            print(f"No MAC Address found in stream {stream_index}, using default name.")

        # Extract channels and prefix them with the MAC address
        channels = []
        for channel in root.findall(".//channels/channel"):
            label = channel.find('label').text
            if label == "EDABITREV0":
                label = "raw"
            elif label == "EMG0":
                label = "raw"
            # Prefix the channel name with the MAC address
            channel_name = f"{label}-{mac_address}"
            channels.append(channel_name)

        # Store the channels for this stream
        self.channels.append(channels)
        print(f"Extracted Channels {stream_index}: {channels}")

    def _find_streams(self):
        print("Looking for an OpenSignals stream...")
        streams = resolve_streams()
        
        if not streams:
            print("❌ No LSL streams found. Make sure your data source is running!")
            return
        
        streams = [s for s in streams if s.name() == 'OpenSignals']
        
        if not streams:
            print("❌ No OpenSignals stream found. Check your LSL source!")
            return

        for index, stream in enumerate(streams):
            inlet = StreamInlet(stream)
            self.inlets.append(inlet)
            self.thread_queues.append(queue.Queue())
            print(f"✅ Connected to stream {index}: {stream.name()} | Type: {stream.type()}")
            
            xml_string = inlet.info().as_xml()
            self._parse_xml(xml_string, index)
            
            self._debug_lsl(inlet)
        
        print("Waiting 2s to stabilize LSL streams...")
        time.sleep(2)

    def _debug_lsl(self, inlet):
        print("Attempting to pull a test sample...")
        sample, timestamp = inlet.pull_sample(timeout=2.0)
        if sample:
            print(f"✅ LSL is WORKING! Sample: {sample}, Timestamp: {timestamp}")
        else:
            print("❌ No data received from LSL. Check your data source!")

    def _stream_data(self, inlet, index):
        print(f"Streaming started for inlet {index}. Press 'ctrl+q' to stop")

        mac_address = self.mac_addresses.get(index, f"stream_{index}")
        filename = f"{mac_address}.h5"

        with h5py.File(filename, "a") as h5file:
            group = h5file.require_group(f"stream_{index}")

            all_channels = ["Time"] + self.channels[index]

            buffer = []
            batch_size = 10

            while self.running:
                samples, timestamps = inlet.pull_chunk(timeout=0.001)
                if not samples or not timestamps:
                    continue

                for sample, timestamp in zip(samples, timestamps):
                    data_dict = {"Time": timestamp, "nSeq": index}
                    for ch, value in zip(self.channels[index], sample):
                        data_dict[ch] = value

                    # Send data to the frontend queue
                    #self.q_data.put(data_dict)

                    # Send data to the data queue (if needed)
                    self.thread_queues[index].put(data_dict)

                    buffer.append(data_dict)

                    if len(buffer) >= batch_size:
                        self._write_to_hdf5(h5file, group, buffer, all_channels)
                        buffer.clear()

            if buffer:
                self._write_to_hdf5(h5file, group, buffer, all_channels)

    def _write_to_hdf5(self, h5file, group, buffer, all_channels):
        #"""Safe HDF5 writing with proper error handling"""
        try:
            # Filter out None or invalid entries
            valid_entries = [entry for entry in buffer if isinstance(entry, dict)]
        
            if not valid_entries:
                print("Warning: Empty buffer or invalid entries")
                return

            # Get actual available channels
            available_channels = set()
            for entry in valid_entries:
                available_channels.update(entry.keys())
        
            # Use only channels that exist in all entries
            common_channels = [ch for ch in all_channels if ch in available_channels]
        
            if not common_channels:
                print("Warning: No common channels found in buffer entries")
                return

            # Create data array only with available channels
            data_list = []
            for entry in valid_entries:
                row = []
                for ch in common_channels:
                    try:
                        row.append(float(entry.get(ch, np.nan)))
                    except (ValueError, TypeError):
                        row.append(np.nan)
                data_list.append(row)
        
            data_array = np.array(data_list)
        
            # Write to HDF5
            if "data" not in group:
                # Create dataset if it doesn't exist
                maxshape = (None, len(common_channels))
                group.create_dataset("data", data=data_array, maxshape=maxshape)
                group.attrs["channels"] = common_channels
            else:
                # Append to existing dataset
                dataset = group["data"]
            
                # Resize if needed
                if dataset.shape[1] != len(common_channels):
                    print(f"Warning: Channel count mismatch ({dataset.shape[1]} vs {len(common_channels)})")
                    return
            
                # Append data
                old_size = dataset.shape[0]
                new_size = old_size + len(data_array)
                dataset.resize((new_size, dataset.shape[1]))
                dataset[old_size:new_size] = data_array
            
        except Exception as e:
            print(f"Error in _write_to_hdf5: {str(e)}")
            raise

    def _aggregate_data(self):
        print("Starting data aggregation...")
        while self.running:
            if all(not q.empty() for q in self.thread_queues):
                combined_data = [q.get(timeout=0.1) for q in self.thread_queues]
                flattened_data = {}
                for i, data_dic in enumerate(combined_data):
                    if i > 0 and 'Time' in data_dic:
                        del data_dic['Time']
                    for key, value in data_dic.items():
                        if 'nSeq' not in key:
                            flattened_data[key] = value

                    # Determine which stream (R or L) this data belongs to
                    acc_columns = [col for col in data_dic.keys() if col.startswith('gACC')]
                    if len(acc_columns) == 3:  # Ensure we have all 3 ACC components
                        gACC1 = data_dic.get(acc_columns[0], 0.0)
                        gACC2 = data_dic.get(acc_columns[1], 0.0)
                        gACC3 = data_dic.get(acc_columns[2], 0.0)
                        acc_magnitude = (gACC1**2 + gACC2**2 + gACC3**2) ** 0.5  # Magnitude formula

                        # Remove individual ACC columns
                        for col in acc_columns:
                            flattened_data.pop(col, None)

                        # Determine if this is the R or L stream
                        if 'R' in acc_columns[0]:  # Check if the first ACC column belongs to the R stream
                            flattened_data['raw-ACC_R'] = acc_magnitude
                        elif 'L' in acc_columns[0]:  # Check if the first ACC column belongs to the L stream
                            flattened_data['raw-ACC_L'] = acc_magnitude

                # Create DataFrame with a single row
                df = pd.DataFrame([flattened_data])
                #print(f"Aggregated DataFrame Backend:\n{df}\n")
                self.q_data.put(df)
            #time.sleep(1.0)

    #### MUGGLE METHODS ####
    def start(self):
        if not self.running:
            self.stream_threads = []
            self.thread_queues = []
            self.running = True
            self._find_streams()

            # Start stream threads
            for index, inlet in enumerate(self.inlets):

                stream_thread = threading.Thread(target=self._stream_data, args=(inlet, index), daemon=True)
                self.stream_threads.append(stream_thread)
                stream_thread.start()
            self.aggregation_thread = threading.Thread(target=self._aggregate_data, daemon=True)
            self.aggregation_thread.start()
            print("LSL Stream started and data logging in progress.")

    def stop(self):
        if self.running:
            self.running = False
            for thread in self.stream_threads:
                thread.join()
            print("LSL Stream stopped.")
