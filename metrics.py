'''
Author:             Matthew McLaughlin/Will Thornton
Contact:            
Description:        Backend component for metric calculations
TODO List:          
'''

#### LIBRARIES ####
# OFF THE SHELF #
import multiprocessing
# CUSTOM #

class Metrics():
    #### MAGIC METHODS ####
    def __init__(self, q_rawData, q_metricdata, q_commandsForMetrics, q_settingsForMetrics):
        #link main queues
        pass

    #### MANGELED METHODS ####
    '''
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
    '''
    #### MUGGLE METHODS #### 
    def start(self):
        pass

#### MAIN #### (just for testing independently of everything else)
def main():
    pass

if __name__ == '__main__':
    main()