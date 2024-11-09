import argparse
import os
import shutil
import hashlib
import time


def get_dir_content(path):
    """
    Get a list of files and directories in the specified path.
    """
    return os.listdir(path)


def calculate_hash(file_path):
    """
    Calculate the MD5 hash of a file to check for content changes.
    """
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


def same_files(src_path, rep_path):
    """
    Compare two files to check if they are identical based on size and hash.
    """
    # Compare file sizes first for quick detection of different files
    if os.path.getsize(src_path) != os.path.getsize(rep_path):
        return False
    return calculate_hash(src_path) == calculate_hash(rep_path)


def log(action, file_path, log_file):
    """
    Log actions (create, update, delete) to both the console and a specified log file.
    """
    log_message = f"{action}: {file_path}"
    print(log_message)
    with open(log_file, 'a') as f:
        f.write(log_message + '\n')


def synchronize_file(src_path, rep_path, file, log_file):
    """
    Synchronize an individual file between the source and replica directories.
    """
    src_file = os.path.join(src_path, file)
    rep_file = os.path.join(rep_path, file)

    # If the source file is empty, make sure the replica has an empty file as well
    if os.path.getsize(src_file) == 0:
        if os.path.exists(rep_file):  # If the file exists in replica, remove it
            os.remove(rep_file)
        open(rep_file, 'w').close()  # Create an empty file in the replica
        log("Created empty file", rep_file, log_file)
        return

    # If the file does not exist in the replica, copy it from the source
    if not os.path.exists(rep_file):
        shutil.copy2(src_file, rep_file)
        log("Created", rep_file, log_file)
    # If the files are different, update the file in the replica
    # This is not the most efficient solution, as it copies the whole file
    # even when only a part of it has changed.
    elif not same_files(src_file, rep_file):
        shutil.copy2(src_file, rep_file)
        log("Updated", rep_file, log_file)


def synchronize_dir(src_path, rep_path, dir, log_file):
    """
    Synchronize a directory by ensuring it exists in the replica and calling 
    the synchronization function on all files and subdirectories within it.
    """
    src_dir = os.path.join(src_path, dir)
    rep_dir = os.path.join(rep_path, dir)

    # If the directory does not exist in the replica, create it
    if not os.path.exists(rep_dir):
        os.makedirs(rep_dir)
        log("Created directory", rep_dir, log_file)

    # Synchronize the contents of the directory
    src_to_rep(src_dir, rep_dir, log_file)


def src_to_rep(src_path, rep_path, log_file):
    """
    Synchronize the source directory to the replica directory. Ensures all files 
    and subdirectories from the source exist in the replica, creating or updating 
    them as needed.
    """
    src_lst = get_dir_content(src_path)

    for item in src_lst:
        item_path = os.path.join(src_path, item)
        if os.path.isfile(item_path):
            synchronize_file(src_path, rep_path, item, log_file)
        elif os.path.isdir(item_path):
            synchronize_dir(src_path, rep_path, item, log_file)


def rep_to_src(src_path, rep_path, log_file):
    """
    Ensure the replica is updated by removing files and directories
    that do not exist in the source.
    """
    rep_lst = get_dir_content(rep_path)

    for item in rep_lst:
        src_item = os.path.join(src_path, item)
        rep_item = os.path.join(rep_path, item)
        
        if not os.path.exists(src_item):
            if os.path.isfile(rep_item):
                os.remove(rep_item)
                log("Deleted", rep_item, log_file)
            elif os.path.isdir(rep_item):
                shutil.rmtree(rep_item)
                log("Deleted", rep_item, log_file)


def synchronize(src_path, rep_path, log_file):
    """
    Perform the full synchronization between the source and replica directories.
    This includes:
    - Copying or updating files from the source to the replica.
    - Deleting files and directories from the replica that don't exist in the source.
    """
    src_to_rep(src_path, rep_path, log_file)
    rep_to_src(src_path, rep_path, log_file)


if __name__ == "__main__":
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(prog='Folder-synchronization')
    parser.add_argument('-s', '--source', required=True, help="Path to source directory")
    parser.add_argument('-r', '--replica', required=True, help="Path to replica directory")
    parser.add_argument('-i', '--interval', type=int, default=10, help="Synchronization interval in seconds")
    parser.add_argument('-l', '--logfile', required=True, help="Path to the log file")

    args = parser.parse_args()

    # Loop to periodically synchronize the directories
    while True:
        synchronize(args.source, args.replica, args.logfile)
        time.sleep(args.interval)
