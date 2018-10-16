import data_processing as dp
import json
import datetime
import config
import bisect
import random
import matplotlib.pyplot as plt
from matplotlib.finance import candlestick_ohlc, date2num


def read_details(path_to_scan):

    res = [file_name for file_name in dp.get_file_names(path_to_scan) if 'details' in file_name]

    if not res:
        raise ValueError('The given path does not contain any detail files.')

    if len(res) > 1:
        print('Filenames:')
        for i, file_name in enumerate(res):
            print(i, file_name)
        i = int(input('Please specify which file to read (0 - %d): ' % (len(res)-1)))
        return res[i]

    return res[0]


def read_detail_get_index(path_to_read, file_name, get_last_index=False):

    file_location = path_to_read + '/' + file_name

    print('Reading \"%s\"' % file_location)

    with open(file_location, 'r') as f:
        content = f.readlines()

    last_index = None
    for line in content[::-1]:
        if 'Trade # ' in line:
            last_index = int(line.split(' ')[-1].rstrip(':\n'))
            break

    if last_index is None:
        raise ValueError('No valid record in detail file.')

    if last_index > 0:
        if get_last_index:
            return last_index
        else:
            index = input('Please specify which record to read (0 - %s): ' % str(last_index)) \
                or random.randint(0, last_index)
        return int(index)


def read_trade_record(path_to_read, file_name, record_index):

    file_location = path_to_read + '/' + file_name

    print('Reading record %d in \"%s\"' % (record_index, file_location))

    with open(file_location, 'r') as f:
        content = f.readlines()

    for i, line in enumerate(content):
        if 'Trade # %d:' % record_index in line:
            j = i + 1
            while content[j] != '\n':
                j += 1
            record_temp = content[i+1: j]
            res = [json.loads(r) for r in record_temp]
            for record_temp in res:
                record_temp[1] = datetime.date(*record_temp[1])
            # print(res)
            return res

    raise ValueError('Cannot find trade record # %d in %s.' % (record_index, file_location))


def plot_history_minute(trade_record, save=False, record_index=-1):

    if not trade_record:
        raise ValueError('Empty record. %s' % trade_record)

    symbol, date, minute_index, buy_price, sell_price, profit, volume_power, price_power = trade_record
    stock_history = dp.read(config.DATA_PATH_STOCK_MINUTE, symbol)

    print(trade_record)

    stock_history_dates = [r['date'] for r in stock_history]
    date_index = bisect.bisect_left(stock_history_dates, date)

    stock_history_to_plot = stock_history[date_index]['detail']
    print(stock_history[date_index])

    plt.rcParams['font.size'] = 15
    fig, ax = plt.subplots(2, 1, figsize=(10, 8), gridspec_kw={'height_ratios':[3, 1]})
    ax1, ax2 = ax

    close_price = stock_history[date_index]['last_close']
    ax1.axhline(y=close_price*0.9,
                # xmin=stock_history_to_plot[0]['date'],
                # xmax=stock_history_to_plot[-1]['date'],
                linestyle=':',
                color='r',
                alpha=0.5,
                linewidth=2)
    ax1.axhline(y=close_price*1.1,
                # xmin=stock_history_to_plot[0]['date'],
                # xmax=stock_history_to_plot[-1]['date'],
                linestyle=':',
                color='r',
                alpha=0.5,
                linewidth=2)
    ax1.axhline(y=close_price*1.0,
                # xmin=stock_history_to_plot[0]['date'],
                # xmax=stock_history_to_plot[-1]['date'],
                color='r',
                alpha=0.5,
                linewidth=2)
    ax1.axvline(x=minute_index,
                # xmin=stock_history_to_plot[0]['date'],
                # xmax=stock_history_to_plot[-1]['date'],
                linestyle=':',
                color='g',
                alpha=0.3,
                linewidth=2)
    ax2.axvline(x=minute_index,
                # xmin=stock_history_to_plot[0]['date'],
                # xmax=stock_history_to_plot[-1]['date'],
                linestyle=':',
                color='g',
                alpha=0.5,
                linewidth=2)
    ax1.set_title("record # %d: profit = %.2f %%, hold time = %d calendar days" % (record_index, profit, 1))
    ax1.grid(True)
    ax1.plot(
         range(len(stock_history_to_plot)),
         [r['price'] for r in stock_history_to_plot],
         '-', color='#0094af', alpha=0.8)
    ax1.plot(
         range(len(stock_history_to_plot)),
         [r['average_price'] for r in stock_history_to_plot],
         '--', color='#434051', alpha=0.8)
    # print([minute_index, 240])
    # print([buy_price, sell_price])
    ax1.plot(
         [minute_index, 240],
         [buy_price, sell_price],
         'bo', alpha=0.8)
    ax1.set_xlim(0, 241)
    ax1.set_ylim(close_price * 0.85, close_price * 1.15)
    ax1.set_xticklabels([])

    ax2.grid(True)
    ax2.bar(
         range(len(stock_history_to_plot)),
         [r['volume']/10000 for r in stock_history_to_plot],
         0.6, color='#0094af', alpha=0.8)
    ax2.plot(
         range(len(stock_history_to_plot)),
         [r['average_volume']/10000 for r in stock_history_to_plot],
         '--', color='#434051', alpha=0.8)
    ax2.set_xlim(0, 241)
    ax2.set_ylim(0, stock_history[date_index]['detail'][-1]['average_volume']/10000*8)
    # quotes = [
    #     [
    #         date2num(stock_history_to_plot[i]['date']),
    #         stock_history_to_plot[i]['open'],
    #         stock_history_to_plot[i]['high'],
    #         stock_history_to_plot[i]['low'],
    #         stock_history_to_plot[i]['close'],
    #     ]
    #     for i in range(len(stock_history_to_plot))
    # ]
    # ax1.axhline(y=stock_history_to_plot[dates_index[0]]['lo50'],
    #             # xmin=stock_history_to_plot[0]['date'],
    #             # xmax=stock_history_to_plot[-1]['date'],
    #             # color='b',
    #             alpha=0.3,
    #             linewidth=2)
    # candlestick_ohlc(ax1, quotes, width=0.7, colorup='#d81715', colordown='#0c8731', alpha=0.9)
    # ax1.set_xlim(dates[0] - datetime.timedelta(days=20),
    #              dates[-1] + datetime.timedelta(days=20))
    ax2.set_xlabel('minute # of %s' % str(date))
    ax2.set_ylabel('volume /10k')
    # Make the y-axis label, ticks and tick labels match the line color.
    ax1.set_ylabel('stock price of %s' % symbol, color='k')
    ax1.tick_params('y', colors='k')

    # horizontal = {
    #     0: dates[0] - datetime.timedelta(days=pre // 3),
    #     1: dates[1] - datetime.timedelta(days=pre // 4),
    #     2: dates[2] - datetime.timedelta(days=(dates[2] - dates[1]).days // 3)
    # }
    # max_price = max([r['close'] for r in stock_history_to_plot])
    # min_price = min([r['close'] for r in stock_history_to_plot])
    # vertical = {
    #     0: (max_price - stock_history_markers[0]) / 3 + stock_history_markers[0],
    #     1: (max_price - stock_history_markers[1]) / 2 + stock_history_markers[1],
    #     2: (min_price - stock_history_markers[2]) / 2 + stock_history_markers[2]
    # }
    # # 个股基本面数据全，每股收益大于2毛，ROE大于10%，营收增长大于30%。
    # stock_basic_info = ''
    # report_index = dp.find_financial_report_index(data_financial, symbol, dates[1])
    # if report_index > 0:  # 可以比较成长性
    #     current_report, previous_report = data_financial[symbol][report_index], \
    #                                       data_financial[symbol][report_index - 1]
    #     if any([r[item] == '' or float(r[item]) == 0
    #             for r in [current_report, previous_report]
    #             for item in ['每股收益TTM', '净资产收益率TTM', '营业总收入']]):
    #         pass
    #     else:
    #         stock_basic_info = 'EPSTTM: %.2f' % float(current_report['每股收益TTM']) \
    #                      + '\nROETTM: %.2f %%' % (float(current_report['净资产收益率TTM']) * 100) \
    #                      + '\nIncome growth: %.2f %%\n' % \
    #                        ((float(current_report['营业总收入']) / float(previous_report['营业总收入']) - 1.0) * 100)
    # if stock_basic_info:
    #     plt.text(0.02, 0.90, stock_basic_info,
    #              horizontalalignment='left',
    #              verticalalignment='center',
    #              transform=ax1.transAxes,
    #              color='#1d8450',
    #              alpha=0.8)
    # annotate_text = {
    #     0: 'Watch',
    #     1: 'Buy',
    #     2: 'Sell',
    # }
    # for i in range(len(dates)):
    #     plt.annotate('%s: %s, %.2f' % (annotate_text[i], dates[i], stock_history_markers[i]),
    #                  xy=(dates[i], stock_history_markers[i]),
    #                  xytext=(horizontal[i], vertical[i]),
    #                  arrowprops=dict(width=1, headwidth=5, facecolor='black', shrink=0.15),
    #                  )
    #
    # ax2 = ax1.twinx()
    # ax1.rcParams['font.size'] = 13
    # ax2.plot([r['date'] for r in index_history_to_plot],
    #          [r['close'] for r in index_history_to_plot],
    #          'b', alpha=0.5)
    #
    # ax2.set_ylabel('SHCI', color='b')
    # ax2.tick_params('y', colors='b')
    # ax2.set_ylim(min([r['close'] for r in index_history_to_plot]) * 0.7,
    #             max([r['close'] for r in index_history_to_plot]) * 1.3)
    # print(profit)

    plt.text(0.02, 0.07, 'volume power: %.2f\nprice power: %.2f' % (volume_power, price_power),
             horizontalalignment='left',
             verticalalignment='center',
             transform=ax1.transAxes,
             color='#1d8450',
             alpha=0.9)
    fig.tight_layout()
    plt.show(block=not save)
    if save:
        plt.savefig('visualizations/record # %d.pdf' % record_index, format='pdf')
    plt.close()


def plot_history_day(trade_record, data_financial, pre=50, post=20, save=False, record_index=-1):

    if not trade_record:
        raise ValueError('Empty record. %s' % trade_record)

    symbol = trade_record[0]

    stock_history = dp.read(config.DATA_PATH_STOCK, symbol)
    index_history = dp.read(config.DATA_PATH_INDEX_DICT, 'SH#000001')

    dates = [trade_record[1], trade_record[1], trade_record[1]]
    stock_history_dates = [r['date'] for r in stock_history]
    dates_index = [bisect.bisect_left(stock_history_dates, date) for date in dates]

    stock_history_to_plot = stock_history[dates_index[0]-pre: dates_index[-1]+post]
    index_history_to_plot = [index_history[r['date']] for r in stock_history_to_plot]

    stock_history_dates = [r['date'] for r in stock_history_to_plot]
    dates_index = [bisect.bisect_left(stock_history_dates, date) for date in dates]

    marker_position = {
        0: 'open',
        1: 'open',
        2: 'open'
    }
    stock_history_markers = [stock_history_to_plot[j][marker_position[i]] for i, j in enumerate(dates_index)]
    profit = (stock_history_markers[2] / stock_history_markers[1] - 1.0) * 100
    hold_time = (dates[2] - dates[1]).days

    if profit > 0:
        return

    plt.rcParams['font.size'] = 15
    fig, ax1 = plt.subplots(figsize=(25, 10))
    ax1.grid(True)
    ax1.plot(
         [r['date'] for r in stock_history_to_plot],
         [r['ma10'] for r in stock_history_to_plot],
         '--', color='#0094af', alpha=0.7)
    ax1.plot(
         [r['date'] for r in stock_history_to_plot],
         [r['ma20'] for r in stock_history_to_plot],
         '--', color='#434051', alpha=0.7)
    ax1.plot(
         dates,
         stock_history_markers,
         'bo', alpha=0.7)
    quotes = [
        [
            date2num(stock_history_to_plot[i]['date']),
            stock_history_to_plot[i]['open'],
            stock_history_to_plot[i]['high'],
            stock_history_to_plot[i]['low'],
            stock_history_to_plot[i]['close'],
        ]
        for i in range(len(stock_history_to_plot))
    ]
    ax1.axhline(y=stock_history_to_plot[dates_index[0]]['lo50'],
                # xmin=stock_history_to_plot[0]['date'],
                # xmax=stock_history_to_plot[-1]['date'],
                # color='b',
                alpha=0.3,
                linewidth=2)
    candlestick_ohlc(ax1, quotes, width=0.7, colorup='#d81715', colordown='#0c8731', alpha=0.9)
    # ax1.set_xlim(dates[0] - datetime.timedelta(days=20),
    #              dates[-1] + datetime.timedelta(days=20))
    ax1.set_xlabel('date')
    # Make the y-axis label, ticks and tick labels match the line color.
    ax1.set_ylabel('stock price of %s' % stock_history[0]['symbol'], color='k')
    ax1.tick_params('y', colors='k')

    horizontal = {
        0: dates[0] - datetime.timedelta(days=pre // 3),
        1: dates[1] - datetime.timedelta(days=pre // 4),
        2: dates[2] - datetime.timedelta(days=(dates[2] - dates[1]).days // 3)
    }
    max_price = max([r['close'] for r in stock_history_to_plot])
    min_price = min([r['close'] for r in stock_history_to_plot])
    vertical = {
        0: (max_price - stock_history_markers[0]) / 3 + stock_history_markers[0],
        1: (max_price - stock_history_markers[1]) / 2 + stock_history_markers[1],
        2: (min_price - stock_history_markers[2]) / 2 + stock_history_markers[2]
    }
    # 个股基本面数据全，每股收益大于2毛，ROE大于10%，营收增长大于30%。
    stock_basic_info = ''
    report_index = dp.find_financial_report_index(data_financial, symbol, dates[1])
    if report_index > 0:  # 可以比较成长性
        current_report, previous_report = data_financial[symbol][report_index], \
                                          data_financial[symbol][report_index - 1]
        if any([r[item] == '' or float(r[item]) == 0
                for r in [current_report, previous_report]
                for item in ['每股收益TTM', '净资产收益率TTM', '营业总收入']]):
            pass
        else:
            stock_basic_info = 'EPSTTM: %.2f' % float(current_report['每股收益TTM']) \
                         + '\nROETTM: %.2f %%' % (float(current_report['净资产收益率TTM']) * 100) \
                         + '\nIncome growth: %.2f %%\n' % \
                           ((float(current_report['营业总收入']) / float(previous_report['营业总收入']) - 1.0) * 100)
    if stock_basic_info:
        plt.text(0.02, 0.90, stock_basic_info,
                 horizontalalignment='left',
                 verticalalignment='center',
                 transform=ax1.transAxes,
                 color='#1d8450',
                 alpha=0.8)
    annotate_text = {
        0: 'Watch',
        1: 'Buy',
        2: 'Sell',
    }
    for i in range(len(dates)):
        plt.annotate('%s: %s, %.2f' % (annotate_text[i], dates[i], stock_history_markers[i]),
                     xy=(dates[i], stock_history_markers[i]),
                     xytext=(horizontal[i], vertical[i]),
                     arrowprops=dict(width=1, headwidth=5, facecolor='black', shrink=0.15),
                     )

    ax2 = ax1.twinx()
    # ax1.rcParams['font.size'] = 13
    ax2.plot([r['date'] for r in index_history_to_plot],
             [r['close'] for r in index_history_to_plot],
             'b', alpha=0.5)

    ax2.set_ylabel('SHCI', color='b')
    ax2.tick_params('y', colors='b')
    # ax2.set_ylim(min([r['close'] for r in index_history_to_plot]) * 0.7,
    #             max([r['close'] for r in index_history_to_plot]) * 1.3)
    plt.title("record # %d: profit = %.2f %%, hold time = %d calendar days" % (record_index, profit, hold_time))
    fig.tight_layout()
    plt.show(block=not save)
    if save:
        plt.savefig('visualizations/record # %d.pdf' % record_index, format='pdf')
    plt.close()


def show_record(save=False, process_all=False, start_from_index=0, random_order=True, profit_condition=''):

    path = 'results'
    filename = read_details(path)
    data_financial = dp.financial_data_reader(config.DATA_PATH_FINANCIAL)

    if process_all:
        index_list = list(range(start_from_index, read_detail_get_index(path, filename, get_last_index=True)+1))
        # print(index_list)
        if random_order:
            random.shuffle(index_list)
        for i in index_list:
            record = read_trade_record(path, filename, record_index=i)[0]
            # print(record)
            if not profit_condition or eval('record[5] ' + profit_condition):
                plot_history_minute(record, save=save, record_index=i)
                plot_history_day(record, data_financial, save=save, record_index=i)
    else:
        record_index = read_detail_get_index(path, filename)
        record = read_trade_record(path, filename, record_index=record_index)
        plot_history_minute(record, save=save, record_index=record_index)
        plot_history_day(record, data_financial, save=save, record_index=record_index)


if __name__ == '__main__':
    show_record(save=False, process_all=True, random_order=False, profit_condition='')
    # show_record(save=False, process_all=True, random_order=False, profit_condition='> 3')
