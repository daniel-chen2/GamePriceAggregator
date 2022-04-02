import logging 
import os
module_dir = os.path.dirname(__file__)

def scrape_logger(store):
    file_path = os.path.join(module_dir, store + '_scrape.log')
    logger=logging.getLogger(store)
    logger.setLevel(logging.INFO) 
    if not logger.hasHandlers():
        formatter = logging.Formatter('%(asctime)s : %(message)s')
        fileHandler = logging.FileHandler(file_path, mode='w')
        fileHandler.setFormatter(formatter)
        streamHandler = logging.StreamHandler()
        streamHandler.setFormatter(formatter)
        logger.addHandler(fileHandler)
        logger.addHandler(streamHandler)
    return logger
