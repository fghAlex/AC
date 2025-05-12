import os

def check_dir():
    current_directory = os.getcwd()

    # Расширение файла для проверки
    file_extension = '.qcow2'

    # Получаем список всех файлов в текущей директории
    files_in_directory = os.listdir(current_directory)

    # Проверяем наличие файлов с указанным расширением
    for file in files_in_directory:
        if file.endswith(file_extension):
            print(f"В {current_directory} найден образ ВМ: {file}")
            return
    else:
        print(f"В текущей директории {current_directory} не найден образ ВМ.")
        exit(1)

def start():
    
    check_dir()
    
    return
