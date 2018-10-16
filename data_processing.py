from os import listdir
from os.path import isfile, join
from multiprocessing import Pool
import pickle
import time
import datetime
import config
import collections
import easyquotation

last_trade_date = easyquotation.use('sina').stocks('sh000001', prefix=True)['sh000001']['date']
last_trade_date = datetime.date(*(time.strptime(last_trade_date, '%Y-%m-%d')[0:3]))
print(last_trade_date)


def get_file_names(path):

    filenames = [f for f in listdir(path) if isfile(join(path, f))]

    return filenames


def get_file_path(path, filename):

    return path + '/' + filename


def get_stock_symbol(filename):

    return filename.rstrip('.txt')


def read_data_and_save(path_read, filename_read, path_write, data_category=''):

    if data_category == 'stock_minute':
        return read_data_and_save_minute_line(path_read, filename_read, path_write)

    data = []

    with open(get_file_path(path_read, filename_read), 'r', encoding='GB18030') as f:

        symbol = get_stock_symbol(filename_read)

        lines = f.readlines()

        if len(lines) >= 2:

            last_date = lines[-2].split('\t')[0]
            # print(last_date)
            last_date = datetime.date(
                    int(last_date[:4]),
                    int(last_date[4:6]),
                    int(last_date[6:8])
                )
            if last_date != last_trade_date:
                print('%s may not have been updated. current date: %s, last trade date: %s.'
                      % (str(symbol), str(last_date), str(last_trade_date)))

            for line_index, line in enumerate(lines[:-1]):

                keys = ['symbol', 'date', 'open', 'high', 'low', 'close', 'volume', 'amount']
                values = [symbol] + line.split('\t')
                values[1] = datetime.date(
                    int(values[1][:4]),
                    int(values[1][4:6]),
                    int(values[1][6:8])
                )
                for i in range(2, len(values)):
                    values[i] = float(values[i].rstrip('\n'))
                record = dict(zip(keys, values))

                data.append(record)

    enhance_data(data)

    save(data, path_write, get_stock_symbol(filename_read))

    save(convert_to_dict(data), path_write+'/dict', get_stock_symbol(filename_read))


def read_data_and_save_minute_line(path_read, filename_read, path_write):

    def chunks(l, n):
        """Yield successive n-sized chunks from l."""
        for i in range(0, len(l), n):
            yield l[i:i + n]

    data = []

    with open(get_file_path(path_read, filename_read), 'r', encoding='GB18030') as f:

        symbol = get_stock_symbol(filename_read)

        lines = f.readlines()

        # print(filename_read, len(lines), len(lines) % 240)

        assert len(lines) % 240 == 1

        if len(lines) >= 2:

            lines = list(chunks(lines[:-1], 240))

            for line_index, line in enumerate(lines):

                if line_index == 0 or line_index == len(lines)-1:
                    continue

                # print('!')
                # print(lines[line_index-1])
                # print(lines[line_index])
                # print(lines[line_index+1])
                # print('.')

                record = dict()

                record['symbol'] = symbol

                date_str = line[0].split('\t')[0]

                record['date'] = datetime.date(
                    int(date_str[:4]),
                    int(date_str[4:6]),
                    int(date_str[6:8])
                )

                record['last_close'] = float(lines[line_index-1][-1].split('\t')[5])

                record['open'] = float(line[0].split('\t')[2])

                record['next_open'] = float(lines[line_index+1][0].split('\t')[2])

                def minute_line_to_dict(minute_line):
                    content = minute_line.rstrip('\n').split('\t')
                    return {
                        'price': float(content[5]),
                        'volume': float(content[6])
                    }
                record['detail'] = [minute_line_to_dict(minute_line) for minute_line in line]

                enhance_data_minute(record)
                # print(record)

                data.append(record)

    #
    save(data, path_write, get_stock_symbol(filename_read))
    #
    # save(convert_to_dict(data), path_write+'/dict', get_stock_symbol(filename_read))


def save(content, path, filename):

    with open(get_file_path(path, filename), 'wb') as f:
        pickle.dump(content, f)


def read(path, filename):

    # print(path, filename)

    with open(get_file_path(path, filename), 'rb') as f:
        res = pickle.load(f)

    return res


def enhance_data_minute(data):

    """
    add more parameters to data: last_close, [ma, hi, lo][5, 10]
    :param data: dict
    :return: enhanced data: dict
    """

    data_detail = data['detail']
    for i, record in enumerate(data_detail):
        sum_of_volume = sum([each['volume'] for each in data_detail[:i+1]])
        record['average_price'] = (sum([each['price']*each['volume'] for each in data_detail[:i+1]]) /
                                   sum_of_volume) if sum_of_volume > 0 else None
        record['average_volume'] = sum_of_volume / (i+1)


def enhance_data(data):

    """
    add more parameters to data: last_close, [ma, hi, lo][10, 20, 50, 200]
    :param data: dict
    :return: enhanced data: dict
    """

    for i, record in enumerate(data):
        record['last_close'] = data[i-1]['close'] if i >= 1 else None
        for interval in [10, 20, 50, 200]:
            record['ma'+str(interval)] = (sum([each['close'] for each in data[i-interval:i]]) / interval) \
                if i >= interval else None
            record['hi'+str(interval)] = max([each['high'] for each in data[i-interval:i]]) \
                if i >= interval else None
            record['lo'+str(interval)] = min([each['low'] for each in data[i-interval:i]]) \
                if i >= interval else None


def convert_to_dict(data):

    res = {}
    for record in data:
        res[record['date']] = record

    return res


def check(path, filename):

    for i, record in enumerate(list(read(path, filename))):
        print(record)
        if i + 1 >= 5:
            break


def process_raw_data(data_category='stock', is_test_data=False, specific_file_names=()):

    t0 = time.time()

    path = config.data_category_to_path[data_category]

    if not specific_file_names:
        for filename in get_file_names(path):
            print(filename)
            if '.DS_Store' in filename:
                continue
            read_data_and_save(path_read=path, filename_read=filename,
                               path_write=config.DATA_PATH + '/' + data_category, data_category=data_category)
            if is_test_data:
                break
    else:
        # print(specific_file_names)
        for filename in specific_file_names:
            # print(filename)
            read_data_and_save(path_read=path, filename_read=filename,
                               path_write=config.DATA_PATH + '/' + data_category, data_category=data_category)

    t1 = time.time()
    print('process data complete. duration: %.2f s.' % (t1-t0))


def process_raw_data_mp(data_category='', mp_n=8):

    t0 = time.time()

    path = config.data_category_to_path[data_category]

    mp_n = mp_n
    tasks = [[] for _ in range(mp_n)]
    print(tasks)

    for i, filename in enumerate(get_file_names(path)):
        tasks[i % mp_n].append(filename)
    print(tasks)
    print('allocate tasks complete')

    pool = Pool(mp_n)
    for i in range(mp_n):
        kwds = {'data_category': data_category, 'is_test_data': False, 'specific_file_names': tuple(tasks[i])}
        pool.apply_async(process_raw_data, kwds=kwds)

    print('tasks started')

    pool.close()
    pool.join()

    pool.terminate()

    t1 = time.time()
    print('process data complete (main). duration: %.2f s.' % (t1-t0))


def process_raw_financial_data():

    path = config.DATA_RAW_FINANCIAL_PATH

    filenames = get_file_names(path)

    if len(filenames) != 1:
        raise ValueError('Please make sure that there is only one file in the path: %s.' % path)

    filename = filenames[0]

    with open(path + '/' + filename, 'r', encoding='GBK') as f:
        fin_data = f.readlines()

    keys = fin_data[0].split(',')
    keys[-1] = keys[-1].rstrip('\n')

    print(keys)

    data = collections.defaultdict(list)

    for record in fin_data[1:]:
        record = record.split(',')
        record[-1] = record[-1].rstrip('\n')
        symbol = record[0].upper()
        symbol = symbol[:2] + '#' + symbol[2:]
        item = dict(zip(keys, record))
        data[symbol].append(item)

    # sort all data s.t. records are newest first
    for symbol in data:
        data[symbol].sort(key=lambda x: x['报告日期'], reverse=False)

    # save data
    save(data, config.DATA_PATH_FINANCIAL, 'financial')


def financial_data_reader(path):

    filenames = get_file_names(path)

    if len(filenames) != 1:
        raise ValueError('Please make sure there is only one file in the path: %s' % path)

    filename = filenames[0]

    return read(path, filename)


def find_financial_report_index(financial_data, symbol, date, start_i=0):

    try:
        if symbol not in financial_data:
            print('Could not find financial record for %s.' % symbol)
            return -1

        j = start_i

        if datetime.date(*(time.strptime(financial_data[symbol][j]['报告日期'], '%Y-%m-%d')[0:3])) > date:
            # print('Could not find report for %s before %s.' % (symbol, date))
            return -1

        while j+1 < len(financial_data[symbol]) and datetime.date(*(time.strptime(financial_data[symbol][j+1]['报告日期'], '%Y-%m-%d')[0:3])) < date:
            j += 1

        report_date = datetime.date(*(time.strptime(financial_data[symbol][j]['报告日期'], '%Y-%m-%d')[0:3]))
        if (date - report_date).days > 400:
            # print('WARNING: Report date (%s) is more than 400 days older than current date (%s).'
            # % (report_date, date))
            return -1

        return j

    except ValueError:

        return -1


def test_find_financial_report():

    data_financial = financial_data_reader(config.DATA_PATH + '/' + 'financial')
    symbol = 'SH#600522'
    index = find_financial_report_index(data_financial, symbol,
                                        datetime.date(*(time.strptime('2005-10-22', '%Y-%m-%d')[0:3])))
    if index == -1:
        print('Could not find.')
        return 0

    print(data_financial[symbol][index])


def stock_data_generator(path):

    for filename in get_file_names(path):
        if '.' in filename:
            continue
        yield read(path, filename)


def load_stock_data(path):

    res = []

    for filename in get_file_names(path):
        if '.' in filename:
            continue
        res.append(read(path, filename))

    return res


def index_data_reader(path):

    res = {}

    for filename in get_file_names(path):
        res[get_stock_symbol(filename)] = read(path, filename)

    return res


if __name__ == '__main__':
    process_raw_data_mp(data_category='index')
    process_raw_data_mp(data_category='stock')
    # process_raw_financial_data()
    # process_raw_data(data_category='stock_minute')
    # process_raw_data_mp(data_category='stock_minute')
