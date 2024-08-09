# aqrtifactory_parser

- loguru
- requests
- beautifulsoup4
- python-dotenv

в папке src создаем .env, добавляем туда строки:
```
URL = "http://10.125.0.41/artifactory/aQsi-cube/release/"
URL_T_B="http://10.125.0.41/artifactory/aQsi-cube/release/cube-t-b/"
URL_D="http://10.125.0.41/artifactory/aQsi-cube/release/cube-d/"
FILE_STRUCT="./struct_file/new_struct.json"
CURRENT_FILE_STRUCT="./struct_file/current_struct.json"
CONFIG_FOLDER_MAP="./config/config_folder_map.json"
CONFIG_FILE="./config/config_file_struct.json"
CURRENT_PATH="./test/"
```