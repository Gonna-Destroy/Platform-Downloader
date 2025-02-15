import time
import os
import logging

logger = logging.getLogger('cleaner')
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler('logs/downloads_cleaning.log', mode='a')
file_handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

directory = 'downloads'
time_step = 600
wait_time = 7200

def setParams(dir: str = 'downloads', step: int = 600, wait: int = 7200):
    global directory, time_step, wait_time, logger
    directory = dir
    time_step = step
    wait_time = wait
    logger.log(f'Updated: dir: {directory}, step: {time_step}, wait: {wait_time}')
    

def cleaning():
    global directory
    while True:
        current = time.time()

        files = os.listdir(directory)

        times_modify = []
        for file in files:
            times_modify.append(os.path.getmtime(f'{directory}/{file}'))

        files_times = {}

        i = 0
        for file in files:
            files_times[times_modify[i]] = file
            i += 1

        # for key, value in files_times.items():
        #     print(key,': ', value, '\n')

        deleted = 0

        for time_mod in times_modify:
            if time_mod + wait_time < current:
                file = files_times.get(time_mod)
                try:
                    os.remove(f'{directory}/{file}')
                    # print('File ', file, ' deleted!')
                    logger.info(f'File {file} success deleted.')
                    deleted += 1
                except Exception as e:
                    # print('This file not deleted: ', e)
                    logger.error(f'File {file} not deleted!')

        if deleted == 0:
            logger.info('All files remain in place.')


        time.sleep(time_step)

