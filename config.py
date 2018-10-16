import os

DATA_PATH = '/Users/troy/Documents/Stock_Data'

DATA_PATH_INDEX = DATA_PATH + '/' + 'index'
DATA_PATH_STOCK = DATA_PATH + '/' + 'stock'
DATA_PATH_STOCK_MINUTE = DATA_PATH + '/' + 'stock_minute'
DATA_PATH_FINANCIAL = DATA_PATH + '/' + 'financial'

DATA_PATH_INDEX_DICT = DATA_PATH_INDEX + '/' + 'dict'
DATA_PATH_STOCK_DICT = DATA_PATH_INDEX + '/' + 'dict'

DATA_RAW_FINANCIAL_PATH = 'data_raw_financial'


PATH_TO_EXECUTION_FOLDER = '/Volumes/C/Users/Troy/Desktop/execution_folder' \
    if os.name == 'posix' else r'C:\Users\Troy\Desktop\execution_folder'
PATH_TO_EXECUTION_FOLDER_DATA = os.path.join(PATH_TO_EXECUTION_FOLDER, 'data')
PATH_TO_EXECUTION_FOLDER_DATA_STOCK = os.path.join(PATH_TO_EXECUTION_FOLDER_DATA, 'stock')
PATH_TO_EXECUTION_FOLDER_DATA_STOCK_MINUTE = os.path.join(PATH_TO_EXECUTION_FOLDER_DATA, 'stock_minute')
PATH_TO_EXECUTION_FOLDER_DATA_INDEX = os.path.join(PATH_TO_EXECUTION_FOLDER_DATA, 'index')
PATH_TO_EXECUTION_FOLDER_DATA_FINANCIAL = os.path.join(PATH_TO_EXECUTION_FOLDER_DATA, 'financial')

data_category_to_path = {
    'index': PATH_TO_EXECUTION_FOLDER_DATA_INDEX,
    'stock': PATH_TO_EXECUTION_FOLDER_DATA_STOCK,
    'stock_minute': PATH_TO_EXECUTION_FOLDER_DATA_STOCK_MINUTE,
}