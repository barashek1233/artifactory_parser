import os
import json
from dotenv import load_dotenv

import requests

class creator_folder():
    
    def __init__(self):
        """
        config_folder_map    ->    конфиг который определяет файлы которые мы должены скачивать
        new_files_struct     ->    новая файловая струтктура которую мы вытягиваем из artifactory
        current_files_struct ->    текущая файловая структура
        """
        load_dotenv()
        self.URL = os.getenv("URL")
        CONFIG_FOLDER_MAP = os.getenv("CONFIG_FOLDER_MAP")
        FILE_STRUCT = os.getenv("FILE_STRUCT")
        self.CURRENT_FILE_STRUCT=os.getenv("CURRENT_FILE_STRUCT")
        self.CURRENT_PATH = os.getenv("CURRENT_PATH")

        with open(CONFIG_FOLDER_MAP, "r") as file1:
            self.config_folder_map = json.load(file1)
        with open(FILE_STRUCT, "r") as file2:
            self.new_files_struct = json.load(file2)
        try:
            with open(self.CURRENT_FILE_STRUCT, "r") as file3:
                self.current_files_struct = json.load(file3)
        except json.JSONDecodeError:
            #  добавить сюда вывод в лог ошибку что файл пуст (или первый запуск или беды)
            self.current_files_struct = {}


    def write_to_current_file(self):
        """
        Метод записи данных в текущую файловую структуру
        """
        with open(self.CURRENT_FILE_STRUCT, 'w') as file:
            json.dump(self.new_files_struct, file, ensure_ascii=False, indent=4)


    def download_file(self, path : str, link : str, name_file : str):
        """
        Метод для скачивания файла name_file по пути path из link
        параметры:
        path: str <- путь куда скачивать
        link: str <- путь откуда скачивать
        name_file <- название скачиваемого файла
        """
        path_file = self.CURRENT_PATH + path + name_file
        link_file = self.URL + link + name_file
        response = requests.get(link_file)
        if response.status_code == 200:
            with open(path_file, 'wb') as file:
                file.write(response.content)


    def make_dir(self, path : str):
        """
        Метод создания папок по пути path
        Игнорирует наличие папки
        Можно передавать полный путь /www/relise/1.0.6-rc43/.../

        параметры path : str <- название папко
        """
        path_dir = self.CURRENT_PATH + path

        os.makedirs(path_dir, exist_ok=True)

    def make_link(self):
        pass


    def check_config_folder_map(self, type_packeg : str, list_link : list) -> dict:
        """
        Метод получения правил для скачивания пакетов
        Доработать
        {
            "version": "latest",
            "items": ["samba"]
        }
        """
        if len(list_link) != 3:
            return {}
        if list_link[0] in self.config_folder_map:
            if list_link[2] in self.config_folder_map[list_link[0]]:
                return self.config_folder_map[list_link[0]][list_link[2]]["settings"]
            else:
                return {}
        else:
            return {}




    def download_files_and_make_folders(self, new_link : dict):
        """
        Метод для скачивания файлов из структуры new_link
        
        Параметры:
        new_link : dict <- словарь по которому проивзодится докачка файлов
        """
        for number, value in new_link.items():
            settings : dict = self.check_config_folder_map(value[0], value[1])
            if len(settings) != 0:
                if "items" in settings:
                    if value[0] == settings["items"][0]:
                        path_dir : str = value[1][0] + value[1][1] + value[1][2]  #  cube-d/rc-42/cube-image/
                        print("path_dir: ", path_dir)
                        self.make_dir(path_dir)
                        for name_file in value[2]:
                            self.download_file(path_dir, path_dir, name_file)

                    


    def find_new_link(self):
        """
        Метод сравнивает текущую файловую структру и новую, создает на ее основе словарь в котором хранится новые элементы и производит их загрузку
        """
        new_link = {}
        for number, value in self.new_files_struct.items():
            if number in self.current_files_struct.items():
                if value != self.current_files_struct[number]:
                    pass   #   Добавить удаление файлов их текущей директории и ошибку
            else:
                new_link[number] = value
        self.write_to_current_file()
        self.download_files_and_make_folders(new_link)

    


if __name__ == "__main__":
    test = creator_folder()
    test.find_new_link()
    pass