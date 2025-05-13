import os
import configparser

def check_dir(current_directory):

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

def natch_create_config():

    # Создаем объект ConfigParser
    config = configparser.ConfigParser()

    # Добавляем секцию Settings
    config['Settings'] = {
        'version': '8',
        'arch': 'x86_64',
        'mount': 'True',
        'ram': '4G',
        'emu_mode': 'graphic',
        'port_forwarding': 'True',
        'source_ports': 'True',
        'module_config': 'True',
        'tuning': 'True',
        'debug_info': 'True'
    }

    # Запрашиваем ввод пользователя для двух переменных
    ports_str_value = input("Введите значение для пометки и проброса портов: ")
    guest_module_dir_value = input("Введите путь для бинарными файлами в гостевой ОС: ")

    # Устанавливаем введенные значения
    config.set('Settings', 'ports_str', ports_str_value)
    config.set('Settings', 'guest_module_dir', guest_module_dir_value)

    # Сохраняем изменения в файле settings_test.ini
    with open('settings_test.ini', 'w') as configfile:
        config.write(configfile)

    print(f'Файл settings_test.ini успешно создан.')
    return

def natch_create_proj():
    return

def start():
    
    current_directory = os.getcwd()
    check_dir(current_directory)
    print("Начинается создание проекта natch.")
    natch_create_config()
    natch_create_proj()

    return
