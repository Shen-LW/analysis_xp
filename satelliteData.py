import os


class SatelliteData:
    '''
    卫星数据类，负责下载数据的断点下载，状态保存，抽样，剔野操作标记等等功能
    '''

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
        "params_four": None,
    }

    def __init__(self, dataHead: dict, file_path: str):
        '''
        初始化函数
        :param dataHead:
        :param file_path: 文件路径，在下载中为.tmp结尾，下载完成后为sDAT结尾
        '''
        self.dataHead = dataHead
        self.file_path = file_path
        self.write_dataHead()

    # 读取数据头信息

    def write_dataHead(self):
        '''
        初始化时，先写入文件头
        :return:
        '''
        with open(self.file_path, 'w', encoding='utf-8') as f:
            head = str(self.dataHead['status']) + '||' + str(self.dataHead['telemetry_name']) + '||' + str(
                self.dataHead['telemetry_num']) + '||' + str(self.dataHead['normal_range']) + '||' + str(
                self.dataHead['telemetry_source']) + '||' + str(self.dataHead['img_num']) + '||' + str(
                self.dataHead['table_num']) + '||' + str(self.dataHead['params_one']) + '||' + str(
                self.dataHead['params_two']) + '||' + str(self.dataHead['params_three']) + '||' + str(
                self.dataHead['params_four']) + '\n'
            f.write(head)

    def reload(self, file_path):
        '''
        从文件中加载数据
        :return:
        '''
        with open(file_path, 'r', encoding='utf-8') as f:
            head = f.readline()
            self.dataHead['status'], self.dataHead['telemetry_name'], self.dataHead['telemetry_num'], self.dataHead[
                'normal_range'], self.dataHead['telemetry_source'], self.dataHead['img_num'], self.dataHead[
                'table_num'], self.dataHead['params_one'], self.dataHead['params_two'], self.dataHead['params_three'], \
            self.dataHead['params_four'] = head.split('||')

    def add_data(self, data):
        '''
        追加写入数据
        :param data:
        :return:
        '''
        with open(self.file_path, 'a', encoding='utf-8') as f:
            lines = [k + '||' + str(v) + '\n' for k, v in data.items()]
            f.writelines(lines)

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


    def resampling(self, start_time, end_time):
        '''
        对数据进行重新采样
        :param start_time:
        :param end_time:
        :return:
        '''
        # 根据起止时间计算采样率






        try:
            f = open(self.file_path, 'r')
            line = f.readline()  #  跳过head行
            line = f.readline()
            while line:

                line = f.readline()
        finally:
            f.close()

