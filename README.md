#### Folder Synchronization Script

This is a Python-based script that synchronizes the contents of two directories, `source` and `replica`. It ensures that the `replica` folder is an exact copy of the `source` folder and does so periodically.

## Usage

To run the script, use the following command:

`py folder_sync.py --source <source_directory> --replica <replica_directory> --interval <sync_interval> --logfile <logfile_path>`


## Arguments:
   
    -s, --source: Required. The path to the source directory you want to sync.
    -r, --replica: Required. The path to the replica directory that will be synchronized.
    -i, --interval: Optional. The synchronization interval in seconds. The default is 10 seconds.
    -l, --logfile: Required. The path to the log file where actions will be recorded.
