import os
import json
import requests
from log.logger import get_logger
# from dotenv import load_dotenv  #  лучше добавить конфиг файловой структуры
from bs4 import BeautifulSoup
from env import CONFIG_FILE, CURRENT_PATH, URL


class parser():

    def __init__(self):
        """
        Инициализация логера и подгрузка конфигурационного файла
        """
        self.CURRENT_PATH = CURRENT_PATH
        
        self.__logs = get_logger()
        self.iter = 1
        self.new_data_from_file_struct = {}


        with open(CONFIG_FILE, "r") as file:
            self.config_files_struct = json.load(file)



    def get_respons_from_url(self, url : str):
        """
        Ункция выполняет get запрос по адресу указанному в передаваемом значении
        При возникновении ошибки вернет None

        Параметры: 
        url :str

        Возвращает: requests.Response | None 
        """
        try:
            respons = requests.get(url, timeout=10)
        except requests.exceptions.RequestException as e:
            self.__logs.error(f"get_respons_from_url | A request error occurred: {e}")
            respons = None
        except requests.exceptions.ConnectionError as e:
            self.__logs.error(f"get_respons_from_url | Connection error: {e}")
            respons = None
        except requests.exceptions.Timeout as e:
            self.__logs.error(f"get_respons_from_url | Timeout exceeded: {e}")
            respons = None
        except requests.exceptions.TooManyRedirects as e:
            self.__logs.error(f"get_respons_from_url | Too many redirects: {e}")
            respons = None
        except requests.exceptions.HTTPError as e:
            self.__logs.error(f"get_respons_from_url | HTTP error: {e}")
            respons = None
        else:
            self.__logs.info("get_respons_from_url | Request completed successfully")
        return respons


    def get_all_links_from_respons(self, response):
        """
        Функция ищет в теле ответа все ссылки
        При возникновении ошибки вернет None 

        Параметры: 
        respons : Respons

        return -> list | None
        """
        try:
            soup = BeautifulSoup(response.text, 'html.parser')
            links = [link.get('href') for link in soup.find_all('a', href=True)]
        except AttributeError as e:
            self.__logs.error(f"get_all_links_from_respons| Error getting href: {e}")
            links = None
        except Exception as e:
            self.__logs.error(f"get_all_links_from_respons | Other error: {e}")
            links = None
        else:
            self.__logs.info(f"get_all_links_from_respons | Done")

        self.__logs.debug(f"get_all_links_from_respons | links: {links}")
        return links


    def getting_links(self, URL : str):
        """
        Функция принимает URL с которого нужно получить ссылки все ссылки.
        Вызывает функцию которая делает get запрос.
        Возвращает None если ошибка запроса или ошибка с поиском ссылок на странице.
        Если ошибок нет вернет список всех ссылок со страницы

        Параметры: 
        URL : str

        return -> None | List
        """
        self.__logs.info(f"getting_links | Relise link : {URL}")
        response = self.get_respons_from_url(URL)

        if response is not None:
            self.__logs.info(f"getting_links | {URL} | Good Response, return links")
            links = self.get_all_links_from_respons(response)
        else:
            self.__logs.error(f"getting_links | {URL} | Respons is None Error")
            links = None

        return links


    def check_file_struct(self, file_name : str) -> dict:
        """
        Функция проверки наличия файла передаваемого в парматре file_name
        Если файла нет или файл не JSON, вернет пустой словарь
        Если файл есть, вернет словарь со значениями из файла

        Параметры: 
        file_name : str <- путь до файла

        return -> dict
        """
        data = {}
        if ".json" not in file_name:
            self.__logs.warning(f"file name: {file_name} < need .json")
            return data
        try:
            with open(file_name, "r") as file:
                data = json.load(file)
        except FileNotFoundError:
            self.__logs.warning(f"check_file_struct | file_name: {file_name} not found ALARM!!!!")  # вот тут надо буедет сделать логирование в телеграм потому что если этого файла нет программа запущена в первый раз или файл удалилс
        else:
            self.__logs.info(f" check_file_struct | file_name: {file_name} open")
        return data


    def write_dict_to_json_file(self, data, filename):
        """
        Записывает словарь в JSON файл, заменяя существующее содержимое.

        Параметры:
        data <- данные в формате dict
        filename <- относительный путь до файла

        result -> json файл
        """
        with open(filename, 'w') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)


    def search_new_links(self, links_list : list):
        """
        Фнукция делает get запрос по адресу указанному в параметре linls_list спику и возвращает список всех ссылкок по указанному адресу, 
        если в списке ошибка данных, вернет None, если не удалось выполнить get запрос вернет None

        Параметры:
        links_list : list <- пример: ["http://10.125.0.41/artifactory/aQsi-cube/release/cube-d/", "1.0.6-rc42/", "cube_image/"]

        return:
        <- list: если нет ошибок вернет список ссылок со страницы.
        <- None: если не удалось выполнить get запрос или проблема в ссылке
        """
        links_str : str = ""
        self.__logs.debug(f"search_new_links | links_list: {links_list}")
        for link in links_list:
            if type(link) != str:
                self.__logs.warning(f"search_new_links | Error link, {link} | type: {type(link)} | is not type str/ WTF??")
                return None
            else:
                links_str = links_str + link

        return_list_links_on_page = self.getting_links(links_str)

        if return_list_links_on_page is None:
            self.__logs.warning(f"search_new_links | return_list_links_on_page is None {return_list_links_on_page}")
            return return_list_links_on_page

        for link_on_page in return_list_links_on_page:
            if link_on_page == "../":
                self.__logs.debug(f"search_new_links | removing value: '{link_on_page}' from response")
                return_list_links_on_page.remove(link_on_page)

        return return_list_links_on_page

    def file_type_check(self, item : str, data_from_file_struct : list):  #  подкгружаем конфиги файлаов
        """
        Метод выполняет проверку файла на соответсвие конфигурации из файла указанном в CONFIG_FILE и в зависмости от указанных правил выполняет его добавление в data_from_file_struct

        Параметры:
        item : str <- элемент который мы проверяем
        data_from_file_struct : list <- 
        """
        for name_group_file_name, rules_all_files in self.config_file_struct.items():         # rules_all_files -> "1" : [[1, "at91bootstrap"], [1, ".swu.bin" ], [0, "100hz"]],
            self.__logs.debug(f"-----------file_type_check-----------")
            self.__logs.debug(f"{name_group_file_name} and {rules_all_files}")
            for number_file, rule_for_file in rules_all_files.items():                   # rule_for_file   -> [[1, "at91bootstrap"], [1, ".swu.bin" ], [0, "100hz"]]
                flag : int = 0
                sum_flags : int = 0
                for rule in rule_for_file:
                    if rule[0] == 1:   #   true то есть значение должно быть
                        if rule[1] in item:
                            flag = 1
                        else:
                            flag = 0
                    elif rule[0] == 0: #   flase то есть значения не должно быть
                        if rule[1] not in item:
                            flag = 1
                        else:
                            flag = 0
                    sum_flags = sum_flags + flag
                    self.__logs.debug(f"rule now: {rule} and item: {item} | flag: {flag}")

                if sum_flags == len(rule_for_file):
                    if name_group_file_name not in data_from_file_struct:
                        self.__logs.debug(f"file_type_check | {name_group_file_name} not in {data_from_file_struct}")
                        data_from_file_struct[name_group_file_name] = {number_file: item}
                    else:
                        self.__logs.debug(f"file_type_check | {name_group_file_name} in {data_from_file_struct}")
                        if number_file in data_from_file_struct[name_group_file_name]:
                            if data_from_file_struct[name_group_file_name][number_file] < item:
                                data_from_file_struct[name_group_file_name][number_file] = item
                        else:
                            data_from_file_struct[name_group_file_name][number_file] = item



    def populating_the_dictionary_with_get_queries(self, main_link : list, type_link : str, data_from_file_struct : dict) -> dict:
        """
        Метод для рекусривного поиска файлов и папок, делает запрос к main_link прибавляя к ней type_link (напрмиер cube-d/) на первой итерации data_from_file_struct будет пустым

        параметры:
        main_link <- массив ссылкок, при вызове должен состоять из массива с одной главной ссылкой [".../relise/"]
        type_link <- строка с ссылкой которая добавляется в main_link, при вызове например "cube-t-b/"
        data_from_file_struct <- словарь для хранения, при первом вызове пустой

        return -> dict: словарь состоящий из формата tree
        """

        main_link.append(type_link)
        self.__logs.debug(f"populating_the_dictionary_with_get_queries | main_link: {main_link}")

        list_links_on_page : list | None = self.search_new_links(main_link)
        self.__logs.debug(f"populating_the_dictionary_with_get_queries | list_links_on_page: {list_links_on_page}")
        if list_links_on_page is None:
            return None
        for item in list_links_on_page:
            self.__logs.debug(f"populating_the_dictionary_with_get_queries | item is not data_from_file_struct: {item}")
            if item[-1] == "/":
                self.__logs.debug(f"item[-1] == /")
                data_from_file_struct[item] = {}
                self.__logs.debug(f"populating_the_dictionary_with_get_queries | create item: {item} {data_from_file_struct[item]}")
                data_from_file_struct[item] = self.populating_the_dictionary_with_get_queries(main_link, item, data_from_file_struct[item])
            else:
                self.__logs.debug(f"-----------------------------------")
                self.__logs.debug(f"вызываю file type check item: {item} | data_from_file_struct: {data_from_file_struct}")
                self.file_type_check(item, data_from_file_struct)

        self.__logs.debug(f"populating_the_dictionary_with_get_queries | {main_link} pop {main_link[-1]}")
        main_link.pop()

        return data_from_file_struct

        # if list_links_on_page is None:
        #     pass
        # elif list_links_on_page[0] == "error":
        #     pass


    def parsing(self):
        """
        Главный метод, в цикле проходится по конфигу и в заивисмости от его содержимого делает запросы по ссылке указанной в URL
        Сначала вызывает метод для создания дерева, после вызывает метод для преобразования дерева в структуру result:

        Result ->
        {"1": [
        "samba",
        [
            "cube-t-b/",
            "1.0.3-rc9-723%2Bdev_gbbf1d56c-g4b815d4/",
            "cube-dev-image/"
        ],
        [
            "at91bootstrap.bin",
            "cube-dev-image-cube-t-b.ubifs.cube-dev-image-cube-t-b-1.0.3-rc9-723%2Bgbbf1d56c-g4b815d4.ubi",
            "u-boot.bin"
        ]],
        ...}
        """
        # URL = os.getenv("URL")
        list_url = [URL]
        FILE_STRUCT = os.getenv("FILE_STRUCT")

        # data_from_file_struct = self.check_file_struct(FILE_STRUCT)
        data_from_file_struct = {}
        self.__logs.debug(f"self.config_files_struct: {self.config_files_struct}")
        for cube_type, self.config_file_struct in self.config_files_struct.items():
            self.__logs.debug(f"cube_type: {cube_type} | config_file_struct: {self.config_file_struct}")
            list_url = [URL]
            tmp_data_from_file_struct = {}
            tmp_data_from_file_struct = self.populating_the_dictionary_with_get_queries(list_url, cube_type, tmp_data_from_file_struct)
            data_from_file_struct[cube_type] = tmp_data_from_file_struct
        
        # self.data_from_file_struct
        self.remake_file_struct(data_from_file_struct)
        
        self.write_dict_to_json_file(self.new_data_from_file_struct, FILE_STRUCT)


    def remake_file_struct(self, data_from_file_struct : dict, link_to_file = []):
        """
        data_from_file_struct <- dict: data_from_file_struct
        link_to_file <- list: 
        return -> None 
        result -> dict: 
        """
        if len(data_from_file_struct) != 0:
            for key, value in data_from_file_struct.items():
                if key == "samba":
                    if len(value) == 3 and len(link_to_file) == 3:   # or key == "swupdate" 
                        files : dict = {}
                        check_count_file : int = 0
                        
                        # files["freq"] = key
                        files["device-type"] = link_to_file[0]
                        files["firmware"] = link_to_file[1]
                        files["image"] = link_to_file[2]
                        files["dir"] = self.CURRENT_PATH + link_to_file[0] + link_to_file[1] + link_to_file[2]
    
                        for _, file in value.items():
                            if "at91bootstrap" in file:
                                files['at91bootstrap'] = file
                                check_count_file += 1
                            elif "u-boot" in file:
                                files['uboot'] = file
                                check_count_file += 2
                            elif ".ubi" in file:
                                files['rootfs'] = file
                                check_count_file += 4
    
                        if check_count_file == 7:  #  Если все три файла есть тогда добавляем его в список файлов
                            self.new_data_from_file_struct[self.iter] = files
                            self.iter = self.iter + 1
                elif key != "samba-100hz" and key != "swupdate-100hz" and key != "swupdate":
                    self.remake_file_struct(value, link_to_file + [key])
                
                # else:
                #     # link_to_file.append(key)
                #     self.remake_file_struct(value, link_to_file + [key])




if __name__ == "__main__":
    parser_link = parser()
    parser_link.parsing()