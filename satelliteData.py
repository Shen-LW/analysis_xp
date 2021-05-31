import os
import datetime
import time
import collections

from PyQt5.QtWidgets import QApplication

from myProgress import MyProgress


class SatelliteData:
    '''
    卫星数据类，负责下载数据的断点下载，状态保存，抽样，剔野操作标记等等功能
    '''
    file_path = None
    is_write_dataHead = False
    dataHead = {
        "status": None,
        'telemetry_name': None,
        'telemetry_num': None,
        'normal_range': None,
        'telemetry_source': None,
        'img_num': None,
        'table_num': None,
        'params_one': None,
        'params_two': None,
        'params_three': None,
        'params_four': None,
        'start_time': None,
        'end_time': None
    }
    star_cache_data = []
    star_data = []
    # 用于撤销的临时文件存储, item为file_path
    cache_list = []
    is_undo = False


    def __init__(self, file_path: str, dataHead: dict):
        '''
        初始化函数
        :param dataHead:
        :param file_path: 文件路径，在下载中为.tmp结尾，下载完成后为sDAT结尾
        '''
        if dataHead is None:  # 重新加载已有数据
            self.file_path = file_path
            self.reload(file_path)
        else:
            self.dataHead = dataHead
            self.file_path = file_path

    # 读取数据头信息
    def write_dataHead(self):
        '''
        初始化时，先写入文件头
        :return:
        '''
        self.dataHead['status'] = '爬取成功'
        with open(self.file_path, 'w', encoding='utf-8') as f:
            head = str(self.dataHead['status']) + '||' + str(self.dataHead['telemetry_name']) + '||' + str(
                self.dataHead['telemetry_num']) + '||' + str(self.dataHead['normal_range']) + '||' + str(
                self.dataHead['telemetry_source']) + '||' + str(self.dataHead['img_num']) + '||' + str(
                self.dataHead['table_num']) + '||' + str(self.dataHead['params_one']) + '||' + str(
                self.dataHead['params_two']) + '||' + str(self.dataHead['params_three']) + '||' + str(
                self.dataHead['params_four']) + '||' + str(self.dataHead['start_time']) + '||' + str(
                self.dataHead['end_time']) + '\n'
            f.write(head)

    def reload(self, file_path):
        '''
        从文件中加载数据
        :return:
        '''
        with open(file_path, 'r', encoding='utf-8') as f:
            head = f.readline()
            head = head.replace('\n', '')
            self.dataHead['status'], self.dataHead['telemetry_name'], self.dataHead['telemetry_num'], self.dataHead[
                'normal_range'], self.dataHead['telemetry_source'], self.dataHead['img_num'], self.dataHead[
                'table_num'], self.dataHead['params_one'], self.dataHead['params_two'], self.dataHead['params_three'], \
            self.dataHead['params_four'], self.dataHead['start_time'], self.dataHead['end_time'] = head.split('||')
            self.dataHead['table_num'] = float(self.dataHead['table_num'])
            self.dataHead['params_three'] = float(self.dataHead['params_three'])

    def add_data(self, data):
        '''
        追加写入数据
        :param data:
        :return:
        '''
        if not self.is_write_dataHead:
            self.write_dataHead()
            self.is_write_dataHead = True
        with open(self.file_path, 'a', encoding='utf-8') as f:
            lines = [k + '||' + str(v) + '\n' for k, v in data.items()]
            f.writelines(lines)



    def _get_next_time(self, start_time, sampling_grade):
        '''
        获取下一个抽样点，构成抽样区间
        :param start_time:
        :param sampling_grade: 抽样等级
        :return:  下一个事件节点的值  eg: '2020-10-11 18:25:27.454000'
        '''
        start_datetime = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S.%f")
        if sampling_grade == 0:  # 不抽样
            return None
        elif sampling_grade == 1: #  2分钟
            offset = datetime.timedelta(minutes=2)
        elif sampling_grade == 2:  # 15分钟
            offset = datetime.timedelta(minutes=15)
        elif sampling_grade == 3:  # 2小时
            offset = datetime.timedelta(hours=2)
        elif sampling_grade == 4:  # 6小时
            offset = datetime.timedelta(hours=6)
        elif sampling_grade == 5:  # 12小时
            offset = datetime.timedelta(hours=12)
        elif sampling_grade == 6:  # 24小时
            offset = datetime.timedelta(hours=24)
        else:
            return None
        next_time = (start_datetime + offset).strftime('%Y-%m-%d %H:%M:%S.%f')
        return next_time

    def resampling(self, start_time, end_time, progress, cache = None):
        '''
        对数据进行重新采样
        :param start_time:
        :param end_time:
        :return:
        '''
        if cache:
            resampling_file_path = cache['file_path']
            content = '---缓存数据加载中---'
        else:
            resampling_file_path = self.file_path
            content = '---原始数据加载中---'

        progress.setContent("进度", content)
        progress.setValue(1)
        progress.show()
        QApplication.processEvents()

        # 根据起止时间计算采样率
        start_datetime = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S.%f")
        end_datetime = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S.%f")

        space = end_datetime - start_datetime
        sampling_grade = None
        if space.days <= 1:
            # 一天之内，不抽样
            sampling_grade = 0
            progress_number = 2
        elif space.days > 1 and space.days <= 7 :
            # 一周之内，2分钟
            sampling_grade = 1
            progress_number = space.days * 720
        elif space.days > 7 and space.days <= 30:
            #  大于1周，小于一个月，每15分钟小时抽样
            sampling_grade = 2
            progress_number = space.days * 96
        elif space.days > 30 and space.days <= 90:
            #  1-3个月，每2小时抽样
            sampling_grade = 3
            progress_number = space.days * 12
        elif space.days > 90 and space.days <= 180:
            #  3-6个月， 每6小时抽样
            sampling_grade = 4
            progress_number = space.days * 4
        elif space.days > 180 and space.days <= 367:
            # 6-12个月， 每12小时抽样
            sampling_grade = 5
            progress_number = space.days * 2
        else:
            # 大于1年， 每24小时抽样
            progress_number = space.days
            sampling_grade = 6

        star_data = collections.OrderedDict()
        try:
            f = open(resampling_file_path, 'r', encoding='utf-8')
            line = f.readline()  # 跳过head行
            next_time = self._get_next_time(start_time, sampling_grade)
            if next_time is None:  # None表示不抽样
                progress.setValue(50)
                progress.show()
                QApplication.processEvents()
                while line:
                    line = f.readline()
                    line = line.replace('\n', '')
                    if line == '':
                        continue
                    key, value = line.split('||')
                    value = float(value)
                    if key < start_time:
                        continue
                    elif key > end_time:
                        break
                    else:
                        star_data[key] = float(value)
            else:
                min_point = None
                max_point = None
                # todo 这个循环应该还可以有优化的地方
                progress_index = 0
                while line:
                    line = f.readline()
                    line = line.replace('\n', '')
                    if line == '':
                        continue
                    key, value = line.split('||')
                    value = float(value)
                    if key < start_time:
                        continue
                    elif next_time > end_time:
                        break
                    elif key < next_time:
                        if min_point is None:
                            min_point = [key, value]
                        else:
                            if min_point is None or value < min_point[1]:
                                min_point = [key, value]
                            elif max_point is None or value > max_point[1]:
                                max_point = [key, value]
                    else:
                        next_time = self._get_next_time(next_time, sampling_grade)
                        if min_point is not None and max_point is not None:
                            # 考虑最大最小值两者的时间先后
                            if min_point[0] < max_point[0]:
                                star_data[min_point[0]] = min_point[1]
                                star_data[max_point[0]] = max_point[1]
                            else:
                                star_data[max_point[0]] = max_point[1]
                                star_data[min_point[0]] = min_point[1]
                        min_point = None
                        max_point = None
                        progress.setValue((progress_index / progress_number) * 100)
                        progress.show()
                        QApplication.processEvents()
                        progress_index = progress_index + 1
        finally:
            f.close()
        if cache:
            self.star_cache_data = star_data
        else:
            self.star_data = star_data
        progress.setValue(100)
        progress.hide()


    def manual_choice(self, left_time, right_time, min_value, max_value, progress):
        '''
        手动剔野，并保存缓存文件
        :param left_time: 起始时间
        :param right_time: 结束时间
        :param min_value: 最小值
        :param max_value: 最大值
        :param progress: 进度条
        :return:
        '''

        progress.setContent("进度", '手动剔野中---')
        progress.setValue(1)
        progress.show()
        QApplication.processEvents()

        if self.cache_list:
            choice_file = self.cache_list[-1]['file_path']
        else:
            choice_file = self.file_path

        filename, file_extension = os.path.splitext(os.path.basename(choice_file))
        new_cache_file = 'tmp/cache/' + filename + '_' + str(len(self.cache_list)) + '.cache'
        try:
            source_f = open(choice_file, 'r', encoding='utf-8')
            new_cache_f = open(new_cache_file, 'w', encoding='utf-8')

            line = source_f.readline()  # 跳过head行
            new_cache_f.write(line)

            progress_index = 0
            progress_number = self._bufcount(choice_file) - 1
            cache_lines = []  # 满10000行再开始写入，加快速度
            while line:
                source_line = source_f.readline()
                line = source_line.replace('\n', '')
                if line == '':
                    continue
                key, value = line.split('||')
                value = float(value)
                if key >= left_time and key <= right_time and value >= min_value and value <= max_value:
                    continue
                else:
                    cache_lines.append(source_line)
                if len(cache_lines) > 10000:
                    new_cache_f.writelines(cache_lines)
                    new_cache_f.flush()
                    cache_lines.clear()
                    # del cache_lines
                    progress.setValue((progress_index / progress_number) * 100)
                    progress.show()
                    QApplication.processEvents()
                    progress_index = progress_index + 10000

            star_data_list = list(self.star_data.keys())
            self.cache_list.append({'file_path': new_cache_file,
                                    'start_time': star_data_list[0],
                                    'end_time': star_data_list[-1]})
            self.is_undo = False
        finally:
            source_f.close()
            new_cache_f.close()

        progress.setValue(100)
        progress.hide()


    def rename_extension(self):
        '''
        完成后修改文件名结尾
        :return:
        '''
        filename, file_extension = os.path.splitext(self.file_path)
        new_filename = filename + '.sDAT'
        #  如果文件存在，则删除
        if os.path.isfile(new_filename):
            os.remove(new_filename)
        os.rename(self.file_path, new_filename)
        self.file_path = new_filename
        self.dataHead['status'] = '读取成功'


    def undo_cache(self):
        if self.is_undo:
            return self.cache_list.pop()
        else:
            self.is_undo = True
            curr_cache = self.cache_list.pop()
            if os.path.exists(curr_cache['file_path']):
                os.remove(curr_cache['file_path'])
            return self.cache_list.pop()


    def clear_cache_file(self):
        '''
        缓冲的方式获取总行数
        :return:
        '''
        for item in self.cache_list:
            filename = item['file_path']
            if os.path.exists(filename):
                os.remove(filename)
        self.cache_list = []

    def _bufcount(self, filename):
        f = open(filename, encoding='utf-8')
        lines = 0
        buf_size = 1024 * 1024
        read_f = f.read  # loop optimization

        buf = read_f(buf_size)
        while buf:
            lines += buf.count('\n')
            buf = read_f(buf_size)

        return lines

