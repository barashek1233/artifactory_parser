from loguru import logger

_instance = None

def get_logger():
    global _instance
    if _instance is None:
        logger.remove()  # Удаляем стандартный обработчик логирования
        logger.add("log/parser.log", format="{time} | {name} | {level} | {message}", rotation="10 MB")  # Добавляем обработчик для записи в файл
        _instance = logger
    return _instance