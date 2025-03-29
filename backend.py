import enum
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
import traceback
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
            self.mac_addresses[stream_index] = mac_address
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
        print("Looking for OpenSignals streams...")
        all_streams = resolve_streams()
    
        # Filter to only unique MAC addresses (last seen wins)
        unique_streams = {}
        for stream in all_streams:
            if stream.name() == 'OpenSignals':
                inlet = StreamInlet(stream)  # Temporary connection
                xml = inlet.info().as_xml()
                mac = ET.fromstring(xml).find(".//type").text.strip()
                unique_streams[mac] = stream  # Overwrite duplicates
    
        if not unique_streams:
            print("❌ No valid OpenSignals streams found")
            return

        # Connect only to the 4 real devices
        self.inlets = []
        for index, (mac, stream) in enumerate(unique_streams.items()):
            if index >= 4:  # Only keep first 4 devices
                break
            
            inlet = StreamInlet(stream)
            self.inlets.append(inlet)
            self.thread_queues.append(queue.Queue())
        
            # Parse XML and store MAC (but still use stream_{index} for files)
            xml_string = inlet.info().as_xml()
            self._parse_xml(xml_string, index)  # index 0-3 only
        
            print(f"✅ Connected to stream {index} | MAC: {mac}")
            self._debug_lsl(inlet)
        print(f"Final MAC Address Mapping: {self.mac_addresses}")

    def _debug_lsl(self, inlet):
        print("Attempting to pull a test sample...")
        sample, timestamp = inlet.pull_sample(timeout=2.0)
        if sample:
            print(f"✅ LSL is WORKING! Sample: {sample}, Timestamp: {timestamp}")
        else:
            print("❌ No data received from LSL. Check your data source!")

    def _stream_data(self, inlet, index):
        print(f"🚀 Starting stream {index} - Enhanced Batch Mode")
        mac_address = self.mac_addresses.get(index, f"stream_{index}")
        filename = f"{mac_address}.h5"

        # Configuration
        TARGET_RATE = 400       # Hz
        SAMPLES_PER_BATCH = 40  # Target batch size
        HDF5_BATCH_SIZE = 10    # HDF5 write batch size
        STREAM_TIMEOUT = 0.01   # 10ms
        SYNTHETIC_RATE = 400    # Hz
        MAX_WAIT_TIME = 0.200   # Max wait for partial batch

        # State tracking
        sample_buffer = []
        data_buffer = []        # For HDF5 writing
        synthetic_timestamp = time.time()
        batch_counter = 0
        last_valid_time = time.time()
        batch_start_time = time.time()

        with h5py.File(filename, "w") as h5file:
            group = h5file.require_group(f"stream_{index}")
            all_channels = ["Time"] + self.channels[index]

            while self.running:
                try:
                    # Get available samples
                    samples, _ = inlet.pull_chunk(timeout=STREAM_TIMEOUT)
                
                    if samples:
                        # Generate synthetic timestamps
                        timestamps = [synthetic_timestamp + (i/SYNTHETIC_RATE) 
                                    for i in range(len(samples))]
                        synthetic_timestamp = timestamps[-1] + (1/SYNTHETIC_RATE)
                    
                        # Add to buffers
                        for sample, timestamp in zip(samples, timestamps):
                            data_dict = {
                                "Time": timestamp,
                                "raw": sample[0],
                                "nSeq": index,
                                **{ch: value for ch, value in zip(self.channels[index], sample)}
                            }
                            sample_buffer.append(data_dict)
                            data_buffer.append(data_dict)
                    
                        last_valid_time = time.time()
                        print(f"📥 Received {len(samples)} samples | Buffer: {len(sample_buffer)}")

                    # Write to HDF5 when enough samples
                    if len(data_buffer) >= HDF5_BATCH_SIZE:
                        self._write_to_hdf5(h5file, group, data_buffer, all_channels)
                        data_buffer.clear()

                    # Process complete batches
                    current_time = time.time()
                    buffer_ready = len(sample_buffer) >= SAMPLES_PER_BATCH
                    time_elapsed = current_time - batch_start_time >= MAX_WAIT_TIME
                
                    if buffer_ready or time_elapsed:
                        if buffer_ready:
                            batch_samples = sample_buffer[:SAMPLES_PER_BATCH]
                        else:
                            batch_samples = sample_buffer.copy()
                            print(f"⏱️ Sending partial batch after {MAX_WAIT_TIME:.3f}s wait")

                        batch_df = pd.DataFrame(batch_samples)
                    
                        try:
                            self.thread_queues[index].put(batch_df, timeout=0.1)
                            batch_counter += 1
                            print(f"📤 Sent batch {batch_counter} | Size: {len(batch_df)}")
                        
                            # Remove processed samples
                            if buffer_ready:
                                sample_buffer = sample_buffer[SAMPLES_PER_BATCH:]
                            else:
                                sample_buffer.clear()
                            
                            batch_start_time = current_time
                        except queue.Full:
                            print("❌ Queue full - dropping batch")

                    # Handle stream timeouts
                    if time.time() - last_valid_time > 1.0:
                        print(f"⚠️ No data for 1s | Buffer: {len(sample_buffer)} samples")
                        last_valid_time = time.time()
                
                    time.sleep(0.001)
                
                except Exception as e:
                    print(f"🚨 Stream error: {str(e)}")
                    time.sleep(0.1)

            # Final flush
            if data_buffer:
                self._write_to_hdf5(h5file, group, data_buffer, all_channels)
            if sample_buffer:
                final_df = pd.DataFrame(sample_buffer)
                self.thread_queues[index].put(final_df)
        
            print(f"🔴 Stream {index} stopped | Total batches: {batch_counter} | Samples: {len(sample_buffer)}")

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
        print("🔄 Starting Enhanced Data Aggregation")
        batch_counter = 0
    
        while self.running:
            try:
                # DEBUG: Show queue states
                print("\n--- Queue Status ---")
                for i, q in enumerate(self.thread_queues):
                    print(f"Queue {i} ({self.mac_addresses.get(i, 'unknown')}): {q.qsize()} items")

                # Process all available queues
                combined_data = []
                for i, q in enumerate(self.thread_queues):
                    while not q.empty():  # Process all available batches per queue
                        try:
                            data = q.get_nowait()
                            if not data.empty:
                                print(f"\n--- Received Data from Stream {i} ---")
                                print(f"Shape: {data.shape}")
                                print(f"Columns: {data.columns.tolist()}")
                                combined_data.append((i, data))
                        except queue.Empty:
                            break

                if combined_data:
                    # Option 1: Forward raw batches with stream identifiers
                    for i, data in combined_data:
                        data['stream_id'] = i  # Add stream identifier
                        self.q_data.put(data)
                        batch_counter += 1
                        print(f"📨 Forwarded batch {batch_counter} from stream {i} | Size: {len(data)}")

                    # Option 2: Maintain original aggregation logic for specific processing
                    flattened_data = {}
                    for i, data_df in combined_data:
                        # Handle both single-row and multi-row batches
                        data_dic = data_df.iloc[0].to_dict() if len(data_df) == 1 else data_df.mean().to_dict()
                    
                        if i > 0 and 'Time' in data_dic:
                            del data_dic['Time']
                        
                        for key, value in data_dic.items():
                            if 'nSeq' not in key and 'stream_id' not in key:
                                flattened_data[key] = value

                        # Handle ACC data (maintain your existing logic)
                        acc_columns = [col for col in data_dic.keys() if col.startswith('gACC')]
                        if len(acc_columns) == 3:
                            gACC1 = data_dic.get(acc_columns[0], 0.0)
                            gACC2 = data_dic.get(acc_columns[1], 0.0)
                            gACC3 = data_dic.get(acc_columns[2], 0.0)
                            acc_magnitude = (gACC1**2 + gACC2**2 + gACC3**2) ** 0.5

                            for col in acc_columns:
                                flattened_data.pop(col, None)

                            if 'R' in acc_columns[0]:
                                flattened_data['raw-ACC_R'] = acc_magnitude
                            elif 'L' in acc_columns[0]:
                                flattened_data['raw-ACC_L'] = acc_magnitude

                    # Create and send aggregated summary
                    if flattened_data:
                        df = pd.DataFrame([flattened_data])
                        print("\n--- Aggregated Summary ---")
                        print(f"Shape: {df.shape}")
                        print(f"Columns: {df.columns.tolist()}")
                        print("Sample values:")
                        for col in df.columns:
                            if 'Time' not in col:
                                print(f"{col}: {df[col].values[0]}")
                    
                        # Send to alternative queue or processing if needed
                        # self.alt_q_data.put(df)

                time.sleep(0.01)  # Prevent CPU overload
            
            except Exception as e:
                print(f"❌ Aggregation error: {str(e)}")
                traceback.print_exc()
                time.sleep(0.1)

    #### MUGGLE METHODS ####
    def start(self):
        if not self.running:
            self.stream_threads = []
            self.thread_queues = []
            self.running = True
            self._find_streams()

            if len(self.inlets) > 4:
                print("⚠️ Warning: More than 4 devices detected. Using first 4.")

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
