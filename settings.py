import os
import json
import copy


class Settings:
    __config = {
        "login": {
            "username": None,
            "password": None
        },
        "auto_choices": []
    }
    __save_path = 'source/config.json'

    def __init__(self):
        if os.path.isfile(self.__save_path):
            try:
                with open(self.__save_path, 'r', encoding='utf8') as fp:
                    self.__config = json.load(fp)
            except:
                self.__save_config()
        else:
            self.__save_config()

    def __save_config(self):
        with open(self.__save_path, 'w') as fp:
            json.dump(self.__config, fp)

    # 修改用户名
    def change_login(self, username, password):
        '''
        修改用户名， 只存储上一次使用的密码
        :param username: 用户名
        :param password: 密码
        :return:
        '''
        self.__config['login']['username'] = username
        self.__config['login']['password'] = password
        self.__save_config()

    def change_auto_choice(self, choice_list):
        '''
        修改自动剔野设置, 只保存最近十条
        :param choice_list: 选择的数组
        :return:
        '''
        # 检查格式
        if choice_list == [] or choice_list is None:
            return
        if type(choice_list) != list:
            return
        for item in choice_list:
            if type(item) != int:
                return
        choice_list = list(set(choice_list))
        choice_list.sort()
        if choice_list in self.__config['auto_choices']:
            return
        self.__config['auto_choices'].insert(0, choice_list)
        self.__config["auto_choices"] = self.__config["auto_choices"][:10]

        self.__save_config()

    def get_login(self):
        return copy.deepcopy(self.__config['login'])

    def get_auto_choice_list(self):
        return copy.deepcopy(self.__config['auto_choices'])
