import time
import math


def fix_sdat():
    filename = 'RKSA30_202006040000-202106070000.sDAT'
    f = open(filename, 'r', encoding='gbk')
    nf = open('tmp/' + filename, 'w', encoding='gbk')
    source_line = f.readline()
    nf.write(source_line)

    # ll = []
    # while source_line:
    #     source_line = f.readline()
    #     print(source_line)
    #     line = source_line.replace('\n', '')
    #     if line == '':
    #         continue
    #     key, value = line.split('||')
    #     if len(ll) > 100:
    #         ll = ll[50:]
    #     if key in ll:
    #         print(key)
    #     else:
    #         nf.write(source_line)
    #         ll.append(key)

    # ll = []
    #
    # while source_line:
    #     source_line = f.readline()
    #     line = source_line.replace('\n', '')
    #     if line == '':
    #         continue
    #     key, value = line.split('||')
    #     if len(ll) > 100:
    #         ll = ll[50:]
    #     if key in ll:
    #         print(key)
    #     ll.append(key)

    # while source_line:
    #     source_line = f.readline()
    #     line = source_line.replace('\n', '')
    #     if line == '':
    #         continue
    #     key, value = line.split('||')
    #     if float(value) > 600:
    #         print(key, ":", value)





def test_speed():
    start = time.time()
    filename = 'RKSA30_202006040000-202106070000.sDAT'
    f = open(filename, 'r', encoding='gbk')
    source_line = f.readline()
    whence = f.tell()
    total = 10972170
    # total = 100000
    while source_line:
        lines = []
        for i in range(1000000):
            source_line = f.readline()
            if not source_line:
                break
            lines.append(source_line)
        # print(len(lines))
        for line in lines:
            line = line.replace('\n', '')
            if line == '':
                return None, None
            key, value = line.split('||')
            value = float(value)

    # for i in range(math.floor(total / 1000000)):
    #     lines = []
    #     for j in range(1000000):
    #         lines.append(f.readline())
    #
    #     for line in lines:
    #         line = line.replace('\n', '')
    #         if line == '':
    #             return None, None
    #         key, value = line.split('||')
    #         value = float(value)



    # for i in range(total):
    #     f.seek(i * 43 + whence)
    #     line = f.readline()
    #     line = line.replace('\n', '')
    #     if line == '':
    #         return None, None
    #     key, value = line.split('||')
    #     value = float(value)
    end = time.time()
    print(end - start)



# 测试读取到具体行
# lines = 42 * row_len - 1
# 一百万行是 41MB

import os


def source_choice(self, star_list):
    # {"index": "star"}
    # 长度小于5，直接返回
    if len(star_list) < 5:
        return

    total_file_size = 0
    source_f_list = []  # 文件指针列表
    tmp_f_list = []  # 新的临时文件指针列表
    threshold_list = []  # 阈值范围列表

    # 获取选择文件中，数据最多的行数作为循环次数. 同时创建文件
    for index_str, star in star_list.items():
        total_file_size = total_file_size + os.path.getsize(star.file_path)
        source_f_list.append(open(star.file_path, 'r', encoding='gbk'))
        tmp_file_name = star.file_path[:-5] + '.tmp'
        tmp_f_list.append(open(tmp_file_name, 'w', encoding='gbk'))
        params_one = star.dataHead['params_one']
        threshold = params_one.replace("[", '').replace("]", '').replace(' ', '').replace('，', ',')
        threshold = threshold.split(',')
        threshold_list.append(threshold)

    # 默认缓存总大小为200*1024*1024
    cache_total = 200 * 1024 * 1024
    cache_size = int(cache_total / len(star_list))

    # 推算总点数
    point_total = int(total_file_size / 42)

    self.progress.setContent("进度", '---源包剔野中---')
    self.progress.setValue(0)
    self.progress.show()
    QApplication.processEvents()

    # 写入文件头部信息
    # 并且读取第一次数据
    time_line_list = {}  # 当前条目的内容
    time_str_list = {}  # 当前条目的时间
    time_value_list = {}  # 当前条目的值
    source_lines_list = {}  # 缓存的源文件数据
    for index, source_f in enumerate(source_f_list):
        source_f.readline()
        tmp_f_list[index].write(list(star_list.values())[index].get_headline())
        time_line = source_f.readline()
        time_line_list[index] = time_line
        time_str, time_value = time_line.replace('\n', '').split('||')
        time_str_list[index] = time_str
        time_value_list[index] = time_value
        source_lines_list[index] = source_f.readlines(cache_size)

    point_index = 0
    show_index = 0
    while 1:
        show_index = show_index + 1
        if show_index % 100000 == 0:
            # print(point_index)
            self.progress.setValue((point_index / point_total) * 100)
            self.progress.show()
            QApplication.processEvents()
        # 处理条目清零或者小于5条，结束循环
        if not time_str_list:
            break
        # 如果长度小于5了，直接写入
        if len(time_str_list) < 5:
            for j in time_str_list.keys():
                # 写入缓存剩下的部分
                tmp_f_list[j].writelines(source_lines_list[j])
                point_index = point_index + len(source_lines_list[j])
                # 直接写入文件种剩下部分
                while 1:
                    source_lines = source_f_list[j].readlines(cache_size)
                    if not source_lines:
                        break
                    tmp_f_list[j].writelines(source_lines)
                    point_index = point_index + len(source_lines_list[j])
                tmp_f_list[j].flush()
            break
        else:
            # 依次步进
            # 判断当前最小值
            min_str = min(time_str_list.values())
            # 判断最小值的个数
            number = list(time_str_list.values()).count(min_str)
            if number >= 5:  # 同一时间段大于5个
                n = 0
                # 统计野点数量
                for index, time_str in time_str_list.items():
                    if time_str == min_str:
                        if float(time_value_list[index]) > float(threshold_list[index][1]) or float(
                                time_value_list[index]) < float(threshold_list[index][0]):
                            n = n + 1
                for index, time_str in time_str_list.items():
                    if time_str == min_str:
                        point_index = point_index + 1
                        if n < 5:  # 野点数小于5 直接写入
                            tmp_f_list[index].write(time_line_list[index])
                        # 刷新数据
                        if source_lines_list[index]:
                            source_line = source_lines_list[index].pop(0)
                            time_line_list[index] = source_line
                            time_str, value = source_line.replace('\n', '').split('||')
                            time_str_list[index] = time_str
                            time_value_list[index] = value
                        else:  # 读取新缓存
                            t_lines = source_f_list[index].readlines(cache_size)
                            if t_lines:
                                source_lines_list[index] = t_lines
                                source_line = source_lines_list[index].pop(0)
                                time_str, value = source_line.replace('\n', '').split('||')
                                time_line_list[index] = source_line
                                time_str_list[index] = time_str
                                time_value_list[index] = value
                            else:  # 文件已经读完
                                del time_line_list[index]
                                del time_str_list[index]
                                del time_value_list[index]
                                del source_lines_list[index]

            else:  # 最小值写入并步进
                for index, time_str in time_str_list.items():
                    if time_str == min_str:
                        tmp_f_list[index].write(time_line_list[index])
                        point_index = point_index + 1
                        if source_lines_list[index]:
                            source_line = source_lines_list[index].pop(0)
                            time_line_list[index] = source_line
                            time_str, value = source_line.replace('\n', '').split('||')
                            time_str_list[index] = time_str
                            time_value_list[index] = value
                        else:  # 读取新缓存
                            t_lines = source_f_list[index].readlines(cache_size)
                            if t_lines:
                                source_lines_list[index] = t_lines
                                source_line = source_lines_list[index].pop(0)
                                time_str, value = source_line.replace('\n', '').split('||')
                                time_line_list[index] = source_line
                                time_str_list[index] = time_str
                                time_value_list[index] = value
                            else:  # 文件已经读完
                                del time_line_list[index]
                                del time_str_list[index]
                                del time_value_list[index]
                                del source_lines_list[index]

    for s_f in source_f_list:
        s_f.close()
    for t_f in tmp_f_list:
        t_f.close()

    source_lines_list.clear()
    del source_line
    self.progress.hide()

    # 修改拷贝文件
    for index_str, star in star_list.items():
        if os.path.isfile(star.file_path):
            os.remove(star.file_path)
        tmp_file_name = star.file_path[:-5] + '.tmp'
        os.rename(tmp_file_name, star.file_path)


import sys
def speed_test():
    start = time.time()
    filename = 'RKSA30_202010110000-202110120000.sDAT'
    f = open(filename, 'r', encoding='gbk')
    source_line = f.readline()
    lines = f.readlines(42000000 - 1)
    # line1 = f.readlines(100*43)
    for line in lines:
        print(line)
    end = time.time()
    print(end - start)



def read_test():
    start = time.time()
    filename = 'RKSA30_202010110000-202110120000.sDAT'
    f = open(filename, 'r', encoding='gbk')
    source_line = f.readline()
    index = 0
    while 1:
        index = index + 1
        # print(index)
        lines = f.readlines(100 * 1024 * 1024)
        # print(len(lines))
        if not lines:
            # print(index)
            break

    end = time.time()
    print(end - start)



def seek_txt():
    filename = r'RKSA30_202010110000-202110120000.sDAT'
    f = open(filename, 'r', encoding='gbk')
    a = f.name
    total = 0
    while 1:
        lines = f.readlines(100*1024*1024)
        if lines:
            total = total + len(lines)
            print(lines[-1])
        else:
            break
    print(total)


def test_dict():
        start = time.time()
        filename = r'RKSA30_202010110000-202110120000.sDAT'
        f = open(filename, 'r', encoding='gbk')
        total = 31552800
        f.readline()
        whence = f.tell()
        for i in range(total):
            # f.seek(i * 43 + whence)
            f.readline()

        # a = {1:'aaa', 2: 'bbbb', 3: 'ccc', 4: 'dddd'}
        # c = ['aaa', 'bbb', 'ccc']
        # for i in range(10000000):
        #     b = a[2]
        #     # b = c[2]
        end = time.time()
        print('time: ', end - start)



def speed_test():
    start = time.time()
    filename = 'RKSA30_202006040000-202106070000.sDAT'
    f = open(filename, 'r', encoding='gbk')
    f.readline()
    while 1:
        line = f.readline()
        if not line:
            break
        key, value = line.replace('\n', '').split('||')
        value = float(value)
    f.close()
    end = time.time()
    print('顺序逐行读写耗时：', end - start)

    start = time.time()
    f = open(filename, 'r', encoding='gbk')
    f.readline()
    while 1:
        lines = f.readlines(100 * 1024 * 1024)
        if not lines:
            break
        for line in lines:
            key, value = line.replace('\n', '').split('||')
            value = float(value)
    f.close()
    end = time.time()
    print('顺序逐块读写耗时：', end - start)


def get_count():
    start = time.time()
    filename = 'RKSA30_202006040000-202106070000.sDAT'
    count = -1
    for count, line in enumerate(open(filename, encoding='gbk')):
        pass
        count += 1
    end = time.time()
    print('1.获取行数：', count, '耗时', end - start)

def bufcount():
    start = time.time()
    filename = 'RKSA30_202006040000-202106070000.sDAT'
    f = open(filename, encoding='gbk')
    lines = 0
    buf_size = 1024 * 1024
    read_f = f.read  # loop optimization

    buf = read_f(buf_size)
    while buf:
        lines += buf.count('\n')
        buf = read_f(buf_size)

    end = time.time()
    print('2.获取行数：', lines, '耗时', end - start)


def check_speed():
    start = time.time()
    for i in range(10000000):
        if '2020-01-01' > '2020-01-02':
            pass

    end = time.time()
    print('判断耗时', end - start)

def test_aaa():
    start = time.time()
    filename = 'RKSA30_202006040000-202106070000.sDAT'
    f = open(filename, encoding='gbk')
    f.readline()
    index = 0
    while 1:
        souece_lines = f.readlines(100 * 1024 * 1024)
        if not souece_lines:
            break
        for line in souece_lines:
            if line[:23] > '2020-12-27 11:43:07.715':
                index = index + 1
            # key, value = line.replace('\n', '').split('||')
            # value = float(value)
            # if key > '2020-12-27 11:43:07.715':
            #     index = index + 1

    end = time.time()
    print('解析时间耗时：', end - start)

import datetime

def init_datetime(time_str):
    '''
    使用该方法差不多为直接用datetime.datetime.strptime()耗时的三分之一
    :param time_str: eg: 2020-06-04 07:04:56.620
    :return:
    '''
    year = int(time_str[:4])
    month = int(time_str[5:7])
    day = int(time_str[8:10])
    hour = int(time_str[11:13])
    minute = int(time_str[14:16])
    second = int(time_str[17:19])
    mincrocecond = int(time_str[20:23] + '000')
    d = datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second, microsecond=mincrocecond)
    return d


def bbbbb():
    start = time.time()
    print('开始时间：', start)
    for i in range(1000000):
        a = '2020-06-04 07:04:56.620'
        aaa = init_datetime(a)
        # aaa = datetime.datetime.strptime('2020-06-04 07:04:56.620', "%Y-%m-%d %H:%M:%S.%f")


    end = time.time()
    print('基础耗时：', end - start)





if __name__ == '__main__':
    # test_speed()
    # speed_test()
    # read_test()
    # seek_txt()
    # test_dict()
    # get_count()
    # bufcount()
    # check_speed()
    # test_aaa()
    bbbbb()