'''
Author:             Matthew McLaughlin/Will Thornton
Contact:            
Description:        Backend component for data saving & passing to front end
TODO List:          
'''

#### LIBRARIES ####
# OFF THE SHELF #
import multiprocessing
# CUSTOM #

class SaveAndDisplay():
    #### MAGIC METHODS ####
    def __init__(self, q_metricdata, q_toFrontEnd, q_commandsForSAD, q_settingsForSAD):
        #link main queues
        pass

    #### MANGELED METHODS ####
    '''
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
    '''
    
    #### MUGGLE METHODS #### 
    def start(self):
        pass

#### MAIN #### (just for testing independently of everything else)
def main():
    pass

if __name__ == '__main__':
    main()