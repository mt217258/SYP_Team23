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
    def __init__(self, q_settings, q_commands, q_data, config):
        self.q_settings = q_settings
        self.q_commands = q_commands
        self.q_data = q_data
        self.config = config
        self.running = False
        self.mac_addresses = {}
        self.thread_queues = []
        self.processed_queues = []
        self.stream_threads = []
        self.processing_threads = []
        self.inlets = []
        self.channels = []
        self.baseline_buffers = {}
        self.baseline_stats = {}
        self.nrm_ready = {}

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

    def _start_processing_threads(self):
        for i in range(len(self.inlets)):
            raw_q = self.thread_queues[i]
            processed_q = queue.Queue()
            self.processed_queues.append(processed_q)
            t = threading.Thread(target=self._process_stream_data, args=(i, raw_q, processed_q), daemon=True)
            self.processing_threads.append(t)
            t.start()

    def _process_stream_data(self, index, raw_queue, processed_queue):
        BATCH_LIMIT = 60000
        total_samples_collected = 0

        while self.running:
            try:
                batch = raw_queue.get(timeout=0.1)
                if batch.empty:
                    continue

                if index not in self.baseline_buffers:
                    self.baseline_buffers[index] = []
                    self.baseline_stats[index] = {}
                    self.nrm_ready[index] = False

                baseline_buf = self.baseline_buffers[index]
                stats = self.baseline_stats[index]

                baseline_buf.append(batch)
                total_samples = sum(len(b) for b in baseline_buf)
                
                for side in ['L', 'R']:
                    sEMG_col = f'raw-sEMG_{side}'
                    rms_col = f'RMS-sEMG_{side}'
                    if sEMG_col in batch.columns:
                        batch[rms_col] = np.sqrt(batch[sEMG_col]**2)

                    eda_col = f'raw-EDA_{side}'
                    rms_col = f'RMS-EDA_{side}'
                    if eda_col in batch.columns:
                        batch[rms_col] = np.sqrt(batch[eda_col]**2)


                acc_cols = [col for col in batch.columns if col.startswith("gACC")]
                if len(acc_cols) == 3:
                    try:
                        acc_mag = np.sqrt(
                            batch[acc_cols[0]]**2 +
                            batch[acc_cols[1]]**2 +
                            batch[acc_cols[2]]**2
                        )
                        side = 'R' if 'R' in acc_cols[0] else 'L'
                        batch[f'raw-ACC_{side}'] = acc_mag
                    except Exception as e:
                        print(f"ACC magnitude calculation error: {e}")

                if not self.nrm_ready[index]:
                    baseline_buf.append(batch.copy())
                    total_samples_collected += len(batch)
                    
                    if total_samples_collected >= BATCH_LIMIT:
                        full_df = pd.concat(baseline_buf, ignore_index = True)
                        for signal in [
                            "raw-sEMG_L", "raw-sEMG_R",
                            "raw-EDA_L", "raw-EDA_R",
                            "raw-ACC_L", "raw-ACC_R"
                        ]:
                            if signal in full_df.columns:
                                stats[signal] = {
                                    "mean": full_df[signal].mean(),
                                    "std": full_df[signal].std(ddof=0) or 1e-6
                                    }
                        self.nrm_ready[index] = True
                        print(f"[Stream {index}] Normalization basline collected.")
                    else:
                        for signal in [
                            "RMS-sEMG_L", "RMS-sEMG_R",
                            "raw-EDA_L", "raw-EDA_R",
                            "raw-ACC_L", "raw-ACC_R"
                        ]:
                            if signal in batch.columns:
                                batch[f"nrm-{signal.split('-')[1]}"] = np.nan
                        processed_queue.put(batch)
                        continue

                for signal, stat in stats.items():
                    if signal in batch.columns:
                        nrm_col = f"nrm-{signal.split('-')[1]}"
                        mu = stat["mean"]
                        sigma = stat["std"]
                        batch[nrm_col] = (batch[signal] - mu)/sigma
                processed_queue.put(batch)
            except queue.Empty:
                continue

    def _stream_data(self, inlet, index):
        mac_address = self.mac_addresses.get(index, f"stream_{index}")
        filename = f"{mac_address}.h5"

        TARGET_RATE = 400
        SAMPLES_PER_BATCH = 40
        HDF5_BATCH_SIZE = 10
        STREAM_TIMEOUT = 0.01
        SYNTHETIC_RATE = 400
        MAX_WAIT_TIME = 0.200

        sample_buffer = []
        data_buffer = []
        synthetic_timestamp = time.time()
        batch_counter = 0
        last_valid_time = time.time()
        batch_start_time = time.time()

        with h5py.File(filename, "w") as h5file:
            group = h5file.require_group(f"stream_{index}")
            all_channels = ["Time"] + self.channels[index]

            while self.running:
                try:
                    samples, _ = inlet.pull_chunk(timeout=STREAM_TIMEOUT)
                    if samples:
                        timestamps = [synthetic_timestamp + (i/SYNTHETIC_RATE) for i in range(len(samples))]
                        synthetic_timestamp = timestamps[-1] + (1/SYNTHETIC_RATE)
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

                    if len(data_buffer) >= HDF5_BATCH_SIZE:
                        self._write_to_hdf5(h5file, group, data_buffer, all_channels)
                        data_buffer.clear()

                    current_time = time.time()
                    buffer_ready = len(sample_buffer) >= SAMPLES_PER_BATCH
                    time_elapsed = current_time - batch_start_time >= MAX_WAIT_TIME

                    if buffer_ready or time_elapsed:
                        if buffer_ready:
                            batch_samples = sample_buffer[:SAMPLES_PER_BATCH]
                        else:
                            batch_samples = sample_buffer.copy()
                        batch_df = pd.DataFrame(batch_samples)
                        try:
                            self.thread_queues[index].put(batch_df, timeout=0.1)
                            batch_counter += 1
                            if buffer_ready:
                                sample_buffer = sample_buffer[SAMPLES_PER_BATCH:]
                            else:
                                sample_buffer.clear()
                            batch_start_time = current_time
                        except queue.Full:
                            pass

                    if time.time() - last_valid_time > 1.0:
                        last_valid_time = time.time()

                    time.sleep(0.001)

                except Exception as e:
                    time.sleep(0.1)

            if data_buffer:
                self._write_to_hdf5(h5file, group, data_buffer, all_channels)
            if sample_buffer:
                final_df = pd.DataFrame(sample_buffer)
                self.thread_queues[index].put(final_df)

    def _write_to_hdf5(self, h5file, group, buffer, all_channels):
        try:
            valid_entries = [entry for entry in buffer if isinstance(entry, dict)]
            if not valid_entries:
                return
            available_channels = set()
            for entry in valid_entries:
                available_channels.update(entry.keys())
            common_channels = [ch for ch in all_channels if ch in available_channels]
            if not common_channels:
                return
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
            if "data" not in group:
                maxshape = (None, len(common_channels))
                group.create_dataset("data", data=data_array, maxshape=maxshape)
                group.attrs["channels"] = common_channels
            else:
                dataset = group["data"]
                if dataset.shape[1] != len(common_channels):
                    return
                old_size = dataset.shape[0]
                new_size = old_size + len(data_array)
                dataset.resize((new_size, dataset.shape[1]))
                dataset[old_size:new_size] = data_array
        except Exception as e:
            raise

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

    def start(self):
        if not self.running:
            self.stream_threads = []
            self.thread_queues = []
            self.processed_queues = []
            self.running = True
            self._find_streams()
            # Limit to 4 devices if more are detected.
            if len(self.inlets) > 4:
                pass
            for index, inlet in enumerate(self.inlets):
                self.thread_queues.append(queue.Queue())
                stream_thread = threading.Thread(target=self._stream_data, args=(inlet, index), daemon=True)
                self.stream_threads.append(stream_thread)
                stream_thread.start()
            self._start_processing_threads()
            self.aggregation_thread = threading.Thread(target=self._aggregate_data, daemon=True)
            self.aggregation_thread.start()

    def stop(self):
        if self.running:
            self.running = False
            for thread in self.stream_threads:
                thread.join()
