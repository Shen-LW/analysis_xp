import os
import datetime
import math
import time
import collections
import traceback
import shutil

from PyQt5.QtWidgets import QApplication

from myProgress import MyProgress


class SatelliteData:
    '''
    卫星数据类，负责下载数据的断点下载，状态保存，抽样，剔野操作标记等等功能
    '''

    def __init__(self, file_path: str, dataHead: dict):
        '''
        初始化函数
        :param dataHead:
        :param file_path: 文件路径，在下载中为.tmp结尾，下载完成后为sDAT结尾
        '''
        self.file_path = None
        self.is_write_dataHead = False
        self.dataHead = {
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
        self.star_cache_data = []
        self.star_data = []
        # 用于撤销的临时文件存储, item为file_path
        self.cache_list = []
        self.is_undo = False

        if dataHead is None:  # 重新加载已有数据
            self.file_path = file_path
            self.reload(file_path)
        else:
            self.dataHead = dataHead
            self.file_path = file_path

    # 写入数据头信息
    def write_dataHead(self):
        '''
        初始化时，先写入文件头
        :return:
        '''
        self.dataHead['status'] = '读取成功'
        with open(self.file_path, 'w', encoding='gbk') as f:
            head = self.get_headline()
            f.write(head)

        # 等到读取完成之后再修改状态，避免文件读取完成的判断出错
        self.dataHead['status'] = '未读取'

    def get_headline(self):
        head = str(self.dataHead['status']) + '||' + str(self.dataHead['telemetry_name']) + '||' + str(
            self.dataHead['telemetry_num']) + '||' + str(self.dataHead['normal_range']) + '||' + str(
            self.dataHead['telemetry_source']) + '||' + str(self.dataHead['img_num']) + '||' + str(
            self.dataHead['table_num']) + '||' + str(self.dataHead['params_one']) + '||' + str(
            self.dataHead['params_two']) + '||' + str(self.dataHead['params_three']) + '||' + str(
            self.dataHead['params_four']) + '||' + str(self.dataHead['start_time']) + '||' + str(
            self.dataHead['end_time']) + '\n'
        return head

    def reload(self, file_path):
        '''
        从文件中加载数据
        :return:
        '''
        with open(file_path, 'r', encoding='gbk') as f:
            head = f.readline()
            head = head.replace('\n', '')
            status, telemetry_name, telemetry_num, normal_range, telemetry_source, img_num, table_num, params_one, params_two, params_three, params_four, start_time, end_time = head.split(
                '||')
            table_num = float(table_num)
            dataHead = {
                "status": status,
                'telemetry_name': telemetry_name,
                'telemetry_num': telemetry_num,
                'normal_range': normal_range,
                'telemetry_source': telemetry_source,
                'img_num': img_num,
                'table_num': table_num,
                'params_one': params_one,
                'params_two': params_two,
                'params_three': params_three,
                "params_four": params_four,
                'start_time': start_time,
                'end_time': end_time
            }
            self.dataHead = dataHead

    def add_data(self, data):
        '''
        追加写入数据
        :param data:
        :return:
        '''
        if not self.is_write_dataHead:
            self.write_dataHead()
            self.is_write_dataHead = True
        with open(self.file_path, 'a', encoding='gbk') as f:
            lines = [k + '||' + str(v) + '\n' for k, v in data.items()]
            f.writelines(lines)

    def delete_file(self):
        # 删除文件，重置对象状态
        if os.path.exists(self.file_path):
            os.remove(self.file_path)
        self.dataHead['status'] = None

    def read_line(self, f, whence, line_index):
        f.seek(line_index * 43 + whence)
        line = f.readline()
        line = line.replace('\n', '')
        if line == '':
            return None, None
        key, value = line.split('||')
        value = float(value)
        return key, value

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
        elif sampling_grade == 1:  # 2分钟
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

    def resampling(self, start_time, end_time, progress, cache=None):
        '''
        对数据进行重新采样
        :param start_time:
        :param end_time:
        :return:
        '''
        if cache:
            resampling_file_path = cache['file_path']
            content = '---' + self.dataHead['telemetry_num'] + '缓存数据加载中---'
        else:
            resampling_file_path = self.file_path
            content = '---' + self.dataHead['telemetry_num'] + '原始数据加载中---'

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
        elif space.days > 1 and space.days <= 7:
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
            f = open(resampling_file_path, 'r', encoding='gbk')
            head = f.readline()  # 跳过head行
            next_time = self._get_next_time(start_time, sampling_grade)
            if next_time is None:  # None表示不抽样
                progress.setValue(50)
                progress.show()
                QApplication.processEvents()
                while 1:
                    tmp_lines = f.readlines(100 * 1024 * 1024)
                    if not tmp_lines:
                        break
                    for line in tmp_lines:
                        key = line[:23]
                        value = float(line[25:41])
                        if key < start_time:
                            continue
                        elif key > end_time:
                            break
                        else:
                            star_data[key] = float(value)
            else:
                min_point = None
                max_point = None
                progress_index = 0
                while 1:
                    tmp_lines = f.readlines(100 * 1024 * 1024)
                    if not tmp_lines:
                        break
                    # tmp_lines反转，方便pop
                    tmp_lines.reverse()
                    while 1:
                        if len(tmp_lines) == 0:
                            break
                        line = tmp_lines[-1]
                        key = line[:23]
                        value = float(line[25:41])
                        if key < start_time:
                            tmp_lines.pop()
                            continue
                        elif next_time > end_time:
                            break
                        elif key < next_time:
                            if min_point is None:
                                min_point = [key, value]
                                max_point = [key, value]
                            else:
                                if value < min_point[1]:
                                    min_point = [key, value]
                                elif value > max_point[1]:
                                    max_point = [key, value]
                            tmp_lines.pop()
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
                            progress_index = progress_index + 1
                            progress.setValue((progress_index / progress_number) * 100)
                            progress.show()
                            QApplication.processEvents()
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
        start = time.time()
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
            source_f = open(choice_file, 'r', encoding='gbk')
            new_cache_f = open(new_cache_file, 'w', encoding='gbk')

            source_line = source_f.readline()  # 跳过head行
            new_cache_f.write(self.get_headline())

            progress_index = 0
            # progress_number = self.bufcount(choice_file) - 1
            progress_number = os.path.getsize(choice_file) / 42
            cache_lines = []  # 满10000行再开始写入，加快速度
            is_end = False
            while 1:
                tmp_source_lines = source_f.readlines(100 * 1024 * 1024)
                if not tmp_source_lines:
                    break

                first_line = tmp_source_lines[0]
                last_line = tmp_source_lines[-1]
                firset_key, first_value = first_line.replace('\n', '').split('||')
                last_key, last_value = last_line.replace('\n', '').split('||')
                if firset_key > right_time or last_key < left_time:
                    new_cache_f.writelines(cache_lines)
                    new_cache_f.flush()
                    cache_lines.clear()
                    new_cache_f.writelines(tmp_source_lines)
                    progress_index = progress_index + len(cache_lines) + len(tmp_source_lines)
                    progress.setValue((progress_index / progress_number) * 100)
                    progress.show()
                    QApplication.processEvents()
                    continue

                for index, source_line in enumerate(tmp_source_lines):
                    progress_index = progress_index + 1
                    key = source_line[:23]
                    value = float(source_line[25:41])
                    if key < left_time:
                        cache_lines.append(source_line)
                    elif key > right_time:  # 已经越过右边界，剩下数据直接写入
                        is_end = True
                        break
                    elif value >= min_value and value <= max_value:
                        continue
                    else:
                        cache_lines.append(source_line)
                    if len(cache_lines) > 100000:
                        new_cache_f.writelines(cache_lines)
                        new_cache_f.flush()
                        cache_lines.clear()
                        # del cache_lines
                        progress.setValue((progress_index / progress_number) * 100)
                        progress.show()
                        QApplication.processEvents()
                if is_end:
                    progress_index = progress_index + len(tmp_source_lines[index:])
                    cache_lines = cache_lines + tmp_source_lines[index:]
                    break

            if cache_lines:
                new_cache_f.writelines(cache_lines)
                new_cache_f.flush()
                cache_lines.clear()

            if is_end:
                # 越过右边界，剩下数据直接写入
                while 1:
                    tmp_source_lines = source_f.readlines(100 * 1024 * 1024)
                    if not tmp_source_lines:
                        break
                    new_cache_f.writelines(tmp_source_lines)
                    new_cache_f.flush()
                    progress_index = progress_index + len(tmp_source_lines)
                    progress.setValue((progress_index / progress_number) * 100)
                    progress.show()
                    QApplication.processEvents()

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

        end = time.time()
        print('手动踢野耗时: ', end - start)

    def rate_choice(self, base_point, normal_rate, progress):
        try:
            # 获取基准点对应的时间, 统一取右边值
            startTime = time.time()
            print('变化率剔野开始', datetime.datetime.now())
            # 如果数据点太多的话，可以考虑用二叉搜索或者快速搜索
            if self.cache_list:
                filename = self.cache_list[-1]['file_path']
            else:
                filename = self.file_path

            progress.setContent("进度", '---数据准备中---')
            progress.setValue(0)
            progress.show()
            QApplication.processEvents()

            point_total = self.bufcount(filename) - 1
            start_time = datetime.datetime.strptime(self.dataHead['start_time'], "%Y-%m-%d %H:%M:%S.%f")
            end_time = datetime.datetime.strptime(self.dataHead['end_time'], "%Y-%m-%d %H:%M:%S.%f")

            f = open(filename, 'r', encoding='gbk')
            f.readline()
            whence = f.tell()

            base_point = [item for item in base_point if (item >= start_time and item < end_time)]
            base_point.reverse()
            correct_base_point = []
            tmp_point = base_point.pop()
            tmp_point_str = str(tmp_point)
            index = -1
            is_end = False
            while 1:
                t_lines = f.readlines(100 * 1024 * 1024)
                if not t_lines:
                    break
                for line in t_lines:
                    index = index + 1
                    # time_str, v = line.replace('\n', '').split('||')
                    time_str = line[:23]
                    if time_str >= tmp_point_str:
                        t = self.init_datetime(time_str)
                        # t = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S.%f")
                        correct_base_point.append((index, t))
                        if base_point:
                            tmp_point = base_point.pop()
                            tmp_point_str = str(tmp_point)
                        else:
                            is_end = True
                            break
                    if index % 10000 == 0:
                        progress.setValue((index / point_total) * 100)
                        progress.show()
                        QApplication.processEvents()
                if is_end:
                    break

            if not correct_base_point:
                progress.hide()
                f.close()
                return False, "未找到任何基准点"
            # 构建基准点结构数组
            base_point_struct_list = []
            for index, t in correct_base_point:
                base_point_struct_list.append({
                    "left_status": 1,  # 1: 运行剔野， 0: 剔野停止
                    "right_status": 1,
                    "left": index - 1,  # 左边位置指针
                    "right": index + 1,  # 右边位置指针
                    "left_outlier": None,  # 左边野点的最后位置
                    "right_outlier": None,  # 右边野点的最后位置
                    "left_outlier_point": None,
                    "right_outlier_point": None,
                    "left_normal": index,  # 左边最后一个正常点
                    "right_normal": index,  # 右边最后一个正常点
                    "left_normal_point": None,
                    "left_normal_point_time": None,
                    "right_normal_point": None,
                    "right_normal_point_time": None
                })

            # 对结构数组进行扩增，避免循环中的越界判断
            base_point_struct_list.insert(0, {
                "left_status": 0,
                "right_status": 0,
                "left": 0,
                "right": 0,
                "left_outlier": None,
                "right_outlier": None,
                "left_outlier_point": None,
                "right_outlier_point": None,
                "left_normal": None,
                "right_normal": None,
                "left_normal_point": None,
                "left_normal_point_time": None,
                "right_normal_point": None,
                "right_normal_point_time": None
            })
            base_point_struct_list.append({
                "left_status": 0,
                "right_status": 0,
                "left": point_total,
                "right": point_total,
                "left_outlier": None,
                "right_outlier": None,
                "left_outlier_point": None,
                "right_outlier_point": None,
                "left_normal": None,
                "right_normal": None,
                "left_normal_point": None,
                "left_normal_point_time": None,
                "right_normal_point": None,
                "right_normal_point_time": None
            })

            # 开始剔野
            progress.setContent("进度", '---变化率剔野中---')
            progress.setValue(0)
            progress.show()
            QApplication.processEvents()

            correct_index_list = []  # 需要剔除的野点
            cache_size = int(1000000 / len(correct_base_point))  # 总共默认缓存200万行数
            cache_lines = {}  # 缓存的行， key: line_index, value: line
            # 提前缓存行
            for n in range(1, len(base_point_struct_list) - 1):
                point_struct = base_point_struct_list[n]
                point_struct['left_normal_point'] = self.read_line(f, whence, point_struct["left_normal"])
                point_struct['right_normal_point'] = self.read_line(f, whence, point_struct["right_normal"])
                # 跳转到固定行
                start_line_index = point_struct['left_normal'] - cache_size
                if start_line_index < 0:
                    start_line_index = 0
                if start_line_index >= point_total:
                    continue
                f.seek(start_line_index * 43 + whence)
                source_lines = f.readlines(cache_size * 2 * 42 - 1)
                if not source_lines:
                    continue
                for offset_index, line in enumerate(source_lines):
                    key = line[:23]
                    value = float(line[25:41])
                    cache_lines[start_line_index + offset_index] = (key, value)

            # 更新缓存
            def update_cache_lines(line_index, direct):
                if direct == 'left':
                    new_index = line_index - cache_size
                    if new_index < 0:
                        new_index = 0
                    if new_index > point_total:
                        return
                    f.seek(new_index * 43 + whence)
                    source_lines = f.readlines((cache_size + 2) * 42 - 1)
                    for offset_index, line in enumerate(source_lines):
                        key = line[:23]
                        value = float(line[25:41])
                        cache_lines[new_index + offset_index] = (key, value)
                elif direct == 'right':
                    f.seek(line_index * 43 + whence)
                    source_lines = f.readlines((cache_size + 2) * 42 - 1)
                    for offset_index, line in enumerate(source_lines):
                        key = line[:23]
                        value = float(line[25:41])
                        cache_lines[line_index + offset_index] = (key, value)

            left_margin = base_point_struct_list[1]["left"]
            rigth_margin = point_total - base_point_struct_list[-2]["left"]
            margin_max = left_margin if left_margin >= rigth_margin else rigth_margin
            if len(base_point_struct_list) > 3:
                for i in range(len(base_point_struct_list) - 3):
                    tmp_len = base_point_struct_list[i + 2]['left'] - base_point_struct_list[i + 1]['left']
                    if tmp_len > margin_max:
                        margin_max = tmp_len
            number = margin_max  # 外部循环最大次数
            print(number)
            print(len(base_point_struct_list))
            for i in range(number):
                if i % 10000 == 0:
                    progress.setValue((i / number) * 100)
                    progress.show()
                    QApplication.processEvents()
                for n in range(1, len(base_point_struct_list) - 1):
                    point_struct = base_point_struct_list[n]
                    before_point_struct = base_point_struct_list[n - 1]
                    after_point_struct = base_point_struct_list[n + 1]
                    # 左右两边分别进行
                    # 左边
                    if point_struct["left_status"]:
                        if point_struct["left"] < 0:
                            point_struct["left_status"] = 0
                        else:
                            if point_struct["left"] >= before_point_struct['right']:
                                curr_point = cache_lines.get(point_struct["left"])
                                if not curr_point:
                                    update_cache_lines(point_struct["left"], 'left')
                                    curr_point = cache_lines[point_struct["left"]]
                                left_normal_point = point_struct['left_normal_point']
                                if curr_point[0] is None or left_normal_point[0] is None:
                                    continue

                                # 判断时间是否超过十分钟, 超过则停止该方向剔野
                                curr_point_time = self.init_datetime(curr_point[0])
                                left_normal_point_time = point_struct["left_normal_point_time"] if point_struct["left_normal_point_time"] is not None else self.init_datetime(
                                    left_normal_point[0])
                                # if (left_normal_point_time - curr_point_time) > datetime.timedelta(seconds=600):
                                #     point_struct["left_status"] = 0
                                # 判断变化率
                                space = left_normal_point_time - curr_point_time
                                space_s = space.seconds * 1000000 + space.microseconds
                                if abs((left_normal_point[1] - curr_point[1]) / (space_s / 1000000)) > abs(normal_rate):
                                    # 野点
                                    correct_index_list.append(point_struct["left"])
                                    # 判断野点数是否超过十分钟, 停止剔野
                                    if point_struct["left_outlier"]:
                                        pass
                                        # befor_outlier_point = self.read_line(f, whence, point_struct["left_outlier"])
                                        # befor_outlier_point = point_struct["left_outlier_point"]
                                        # befor_outlier_point = tmp_chice_data[point_struct["left_outlier"]]
                                        # befor_outlier_point_time = datetime.datetime.strptime(befor_outlier_point[0],
                                        #                                                       "%Y-%m-%d %H:%M:%S.%f")
                                        # if (befor_outlier_point_time - curr_point_time) > datetime.timedelta(seconds=600):
                                        #     point_struct["left_status"] = 0
                                    else:
                                        point_struct["left_outlier"] = point_struct["left"]
                                        point_struct['left_outlier_point'] = curr_point
                                else:
                                    # 正常点
                                    point_struct["left_normal"] = point_struct["left"]
                                    point_struct["left_normal_point"] = curr_point
                                    point_struct["left_normal_point_time"] = curr_point_time
                                    point_struct["left_outlier"] = None
                                del cache_lines[point_struct["left"]]
                                point_struct["left"] = point_struct["left"] - 1
                            else:
                                point_struct["left_status"] = 0

                    # 右边
                    if point_struct["right_status"]:
                        if point_struct["right"] >= point_total:
                            point_struct["right_status"] = 0
                        else:
                            if point_struct["right"] <= after_point_struct['left']:
                                curr_point = cache_lines.get(point_struct["right"])
                                if not curr_point:
                                    update_cache_lines(point_struct["right"], 'right')
                                    curr_point = cache_lines[point_struct["right"]]
                                right_normal_point = point_struct['right_normal_point']
                                left_normal_point = point_struct['left_normal_point']
                                if curr_point[0] is None or left_normal_point[0] is None:
                                    print('left_normal_point')
                                    continue

                                # 判断时间是否超过十分钟, 超过则停止该方向剔野
                                curr_point_time = self.init_datetime(curr_point[0])
                                right_normal_point_time = point_struct["right_normal_point_time"] if point_struct["right_normal_point_time"] is not None else self.init_datetime(
                                    right_normal_point[0])
                                # if (curr_point_time - right_normal_point_time) > datetime.timedelta(seconds=600):
                                #     point_struct["right_status"] = 0
                                # 判断变化率
                                space = curr_point_time - right_normal_point_time
                                space_s = space.seconds * 1000000 + space.microseconds
                                if abs((curr_point[1] - right_normal_point[1]) / (space_s / 1000000)) > abs(normal_rate):
                                    # 野点
                                    correct_index_list.append(point_struct["right"])
                                    # 判断野点数是否超过十分钟, 停止剔野
                                    if point_struct["right_outlier"]:
                                        pass
                                        # befor_outlier_point = self.read_line(f, whence, point_struct["right_outlier"])
                                        # befor_outlier_point = point_struct['right_outlier_point']
                                        # befor_outlier_point = tmp_chice_data[point_struct["right_outlier"]]
                                        # befor_outlier_point_time = datetime.datetime.strptime(befor_outlier_point[0],
                                        #                                                       "%Y-%m-%d %H:%M:%S.%f")
                                        # if (curr_point_time - befor_outlier_point_time) > datetime.timedelta(seconds=600):
                                        #     point_struct["right_status"] = 0
                                    else:
                                        point_struct["right_outlier"] = point_struct["right"]
                                        point_struct["right_outlier_point"] = curr_point
                                else:
                                    # 正常点
                                    point_struct["right_normal"] = point_struct["right"]
                                    point_struct["right_normal_point"] = curr_point
                                    point_struct["right_normal_point_time"] = curr_point_time
                                    point_struct["right_outlier"] = None
                                del cache_lines[point_struct["right"]]
                                point_struct["right"] = point_struct["right"] + 1
                            else:
                                point_struct["right_status"] = 0
            f.close()
            correct_index_list.sort()
            correct_index_list.reverse()
            print('correct_index_list_len:', len(correct_index_list))
            progress.hide()
            # 剔除野点, 保存缓存文件
            if self.cache_list:
                choice_file = self.cache_list[-1]['file_path']
            else:
                choice_file = self.file_path

            filename, file_extension = os.path.splitext(os.path.basename(choice_file))
            new_cache_file = 'tmp/cache/' + filename + '_' + str(len(self.cache_list)) + '.cache'
            try:
                source_f = open(choice_file, 'r', encoding='gbk')
                source_f.seek(0)
                new_cache_f = open(new_cache_file, 'w', encoding='gbk')

                source_line = source_f.readline()  # 跳过head行
                new_cache_f.write(self.get_headline())
                progress.setContent("进度", '---野点剔除中---')
                progress.setValue(0)
                progress.show()
                QApplication.processEvents()
                progress_number = self.bufcount(choice_file) - 1
                cache_lines = []  # 满10000行再开始写入，加快速度
                index = -1
                if correct_index_list:
                    cor_index = correct_index_list.pop()
                else:
                    cor_index = -1  # 无野点

                while 1:
                    source_line_list = source_f.readlines(100 * 1024 * 1024)
                    if not source_line_list:
                        break
                    for source_line in source_line_list:
                        index = index + 1
                        if index % 10000 == 0:
                            progress.setValue((index / progress_number) * 100)
                            progress.show()
                            QApplication.processEvents()
                        line = source_line.replace('\n', '')
                        if line == '' or (index == cor_index):
                            if correct_index_list:
                                cor_index = correct_index_list.pop()
                            continue
                        else:
                            cache_lines.append(source_line)

                        if len(cache_lines) > 100000:
                            new_cache_f.writelines(cache_lines)
                            new_cache_f.flush()
                            cache_lines.clear()

                if cache_lines:
                    new_cache_f.writelines(cache_lines)
                    new_cache_f.flush()
                    cache_lines.clear()
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
            endTime = time.time()
            print('变化率踢野耗时', endTime - startTime)
            return True, None
        except Exception as e:
            traceback.print_exc()
            return False, '变化率剔野遇见错误'

    def rename_extension(self, item_name):
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
        # 另存原始数据
        dst_dir = os.path.join('tmp/data_backup', item_name)
        dst_file = os.path.join(dst_dir, os.path.basename(self.file_path))
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        shutil.copyfile(new_filename, dst_file)

    def undo_cache(self):
        if self.is_undo:
            return self.cache_list.pop()
        else:
            self.is_undo = True
            curr_cache = self.cache_list.pop()
            if os.path.exists(curr_cache['file_path']):
                os.remove(curr_cache['file_path'])
            if self.cache_list:
                return self.cache_list.pop()
            else:
                return None

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
        self.star_cache_data = []
        self.star_data = []
        self.is_undo = False

    def bufcount(self, filename):
        f = open(filename, encoding='gbk')
        lines = 0
        buf_size = 1024 * 1024
        read_f = f.read  # loop optimization

        buf = read_f(buf_size)
        while buf:
            lines += buf.count('\n')
            buf = read_f(buf_size)

        return lines

    def get_data_range(self):
        minX = None
        maxX = None
        f = open(self.file_path, encoding='gbk')
        head = f.readline()
        # 设定初始值
        line = f.readline()
        if line:
            time_str, v = line.replace('\n', '').split('||')
            v = round(float(v), 3)
            minX = v
            maxX = v
        else:
            return None

        while 1:
            lines = f.readlines(100 * 1024 * 1024)
            if not lines:
                break
            for line in lines:
                time_str, v = line.replace('\n', '').split('||')
                v = round(float(v), 3)
                if v > maxX:
                    maxX = v
                elif v < minX:
                    minX = v
        return [minX, maxX]

    def get_last_data(self):
        '''
        获取最后一个参数, 用于生成表格二
        :return:
        '''
        f = open(self.file_path, 'rb')
        f.seek(-43, 2)
        last_line = f.readline().decode('gbk')
        last_line.replace('\r\n', '')
        time_str, value = last_line.split('||')
        # 默认只有一位数据，所以返回第一个字符
        return value[0]

    def init_datetime(self, time_str):
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
        d = datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second,
                              microsecond=mincrocecond)
        return d
