import datetime
import json
import time
import math
import matplotlib.pyplot as plt
import data_processing as dp
import os
import config


def get_profit(record, variable):

    # 给定分钟线，应用日内交易逻辑，返回收益
    pass

    # print(record)
    # print(record['detail'])
    #
    # plt.plot([each['price'] for each in record['detail']])
    # plt.plot([each['average_price'] for each in record['detail']])
    # plt.show()

    # 非ST，低开5%以上，开盘五分钟均超均价99%，按下一分钟价格买入，第二日开盘价卖出。
    # if 'ST' not in record['symbol'] and record['open'] / record['last_close'] < 0.95 and \
    # if all([(not v['average_price'] or v['price'] < v['average_price'] * 0.95) for v in record['detail'][:10]]):

    # 捕捉主力买入的时机，前稳定，后突破时买入，按下一分钟成交价计算。
    hi, lo = None, None
    detail = record['detail']
    for i, val in enumerate(detail[:-5]):
        previous_detail = detail[:i]
        p = val['price']
        pa = val['average_price']
        v = val['volume']
        va = val['average_volume']
        previous_prices = [each['price'] for each in previous_detail]
        hi = p if not hi else max(previous_prices)
        lo = p if not lo else min(previous_prices)
        if hi/lo-1 > 0.09:  # 前面波动小于3%
            return
        volume_power = sum([(math.log(each['volume']/each['average_volume'], 2) if each['average_volume'] > 0 and each['volume'] > 0 else -10) for each in previous_detail[-3:]])
        price_power = sum([(each['price']/each['average_price']-1)*100 for each in previous_detail[-3:] if each['average_price']])
        if volume_power > 3 * 2 and price_power > 5 and p/hi-1 > 0.01:  # 有连续买盘且突破
            # if any([each['price'] < detail[i]['price'] for each in detail[i+1:]]):  # 使用第五分钟价格限价买入
                profit = (record['next_open'] / detail[i+1]['price'] - 1) * 100
                res = [record['symbol'], record['date'], i+1, detail[i+1]['price'], record['next_open'], profit, volume_power, price_power]
                return res
    pass

    # 捕捉主力卖出的时机，前稳定，后突破时买入，按下一分钟成交价计算。
    # hi, lo = None, None
    # detail = record['detail']
    # for i, val in enumerate(detail[:-5]):
    #     previous_detail = detail[:i]
    #     p = val['price']
    #     pa = val['average_price']
    #     v = val['volume']
    #     va = val['average_volume']
    #     previous_prices = [each['price'] for each in previous_detail]
    #     hi = p if not hi else max(previous_prices)
    #     lo = p if not lo else min(previous_prices)
    #     if hi/lo-1 > 0.02:  # 前面波动小于2%
    #         break
    #     volume_power = [(math.log(each['volume']/each['average_volume'], 2) if each['average_volume'] > 0 and each['volume'] > 0 else -10) for each in previous_detail[-5:]]
    #     price_power = [(each['price']/each['average_price']-1)*100 for each in previous_detail[-5:] if each['average_price']]
    #     if sum(volume_power) > 5 * 3 and sum(price_power) < -1 and p/lo-1 < -0.01:  # 有连续买盘且突破
    #         # if any([each['price'] < detail[i]['price'] for each in detail[i+1:]]):  # 使用第五分钟价格限价买入
    #             profit = (record['next_open'] / detail[i+1]['price'] - 1) * 100
    #             res = [record['symbol'], record['date'], i+1, detail[i+1]['price'], record['next_open'], profit]
    #             return res
    pass


def plot_distribution_of_up_percent(data_stock, variable, test=True):

    # iterate through all the stocks and records after 1990 and calculate the profit
    profit = []
    executions = []
    hold_time = [1]
    details = []

    for stock in data_stock:
        report_index = 0
        for index, record in enumerate(stock):

            date = record['date']
            symbol = record['symbol']
            # print(record)

            result = get_profit(record, variable)
            if result:
                profit.append(result[5])
                executions.append(record['date'])
                details.append(result)

        if test and len(profit) > 10:
            break

    if not test and len(executions) < 1000:
        print('WARNING: # of trades (%d) is below 1000.' % len(executions))

    if len(profit) == 0:
        print('No trades.')
        return

    # plot profit distribution
    plt.clf()
    plt.cla()
    plt.close()
    plt.hist(profit, bins=100)
    # plt.hist([10 * math.log(1 + 0.01 * p, 10) for p in profit], bins=100, range=(-5, 10))
    plt.xlabel('profit [%]')
    # plt.xlabel('profit [dB]')
    plt.ylabel('frequency')

    # cal expectation
    expectation = sum(profit) / len(profit)
    gain = len([x for x in profit if x > 0.0]) / len(profit) * 100
    print(len(executions))
    print(expectation)
    print(gain)
    plt.title('expectation of profit %% : %.2f %%, gain frequency: %.2f %%' % (expectation, gain))
    plt.savefig('results/'
                'profit_distribution(var=%.2f).pdf' % variable, format='pdf')
    plt.show(block=False)

    # plot execution time distribution
    plt.clf()
    plt.cla()
    plt.close()
    plt.hist(executions, bins=333)
    plt.yscale('log')
    plt.xlabel('date')
    plt.ylabel('frequency')
    avg_hold_time = sum(hold_time) / len(hold_time)
    plt.title('total # of trades: %d, average hold time: %.2f days' % (len(executions), avg_hold_time))
    print(avg_hold_time)
    plt.show(block=False)
    plt.savefig('results/'
                'execution_time_distribution(var=%.2f).pdf' % variable, format='pdf')

    # save details
    with open('results/details(var=%.2f).txt' % variable, 'w') as f:
        for i, detail in enumerate(details):
            content = detail.copy()
            f.write('Trade # %d:\n' % i)
            date = content[1]
            year, month, day = date.year, date.month, date.day
            content[1] = (year, month, day)
            f.write(json.dumps(content) + '\n')
            f.write('\n')


def analysis(test=True):

    variables = [-1]  # range(2000, 2019)  # [-1]

    # load data
    print('loading data...')
    t0 = time.time()
    if test or len(variables) <= 1:
        data_stock_minute = dp.stock_data_generator(config.DATA_PATH_STOCK_MINUTE)
    else:
        data_stock_minute = [x for x in dp.stock_data_generator(config.DATA_PATH_STOCK_MINUTE)]
    t1 = time.time()
    print('read complete. duration: %.2f s.' % (t1-t0))

    # analysis
    for variable in variables:
        print('testing variable = %.2f' % variable)
        plot_distribution_of_up_percent(data_stock_minute, variable, test=test)

    t2 = time.time()
    print('analysis complete. duration: %.2f s.' % (t2-t1))


def verify_index_data():

    data_index = dp.index_data_reader('../data/index/dict')
    szzs = data_index['SH#000001']
    for date in szzs:
        record_szzs = szzs[date]  # 当日沪指
        if any(not record_szzs[each] for each in ['ma10', 'ma20', 'ma50', 'ma200']):
            continue
        # print(record_szzs['ma10'], record_szzs['ma20'], record_szzs['ma50'], record_szzs['ma200'])
        dtpl = record_szzs['ma10'] > record_szzs['ma20'] > record_szzs['ma50'] > record_szzs['ma200']
        if dtpl:
            print(record_szzs)


if __name__ == '__main__':

    analysis(test=False)

    os.system('say "analysis completed"')

    # test_find_financial_report()
