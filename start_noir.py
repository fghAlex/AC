import os
import subprocess

### на случай если захочется редактировать содержимое трафика.
### его удобнее редактировать в формате списка curl запросов 
# def send_traffic():
#     # Формируем путь к файлу endpoints.flow в выбранной директории
#     flow_file = os.path.join(selected_dir, "endpoints.flow")
    
#     # Проверяем, существует ли файл endpoints.flow
#     if not os.path.isfile(flow_file):
#         print(f"Ошибка: файл {flow_file} не найден в директории {selected_dir}.")
#         return
    
#     # Формируем команду для mitmdump
#     command = [
#         "mitmdump",
#         "-r", flow_file,
#         "--set", "stream_large_bodies=0",
#         "--export-curl"
#     ]
    
#     # Путь к файлу requests.sh в выбранной директории
#     output_file = os.path.join(selected_dir, "requests.sh")
    
#     try:
#         # Выполняем команду и перенаправляем вывод в requests.sh
#         with open(output_file, "w") as f:
#             subprocess.run(command, stdout=f, check=True)
#         print(f"Команда mitmdump успешно выполнена, результат сохранен в {output_file}.")
#     except FileNotFoundError:
#         print("Ошибка: mitmdump не найден. Убедитесь, что mitmproxy установлен.")
#     except subprocess.CalledProcessError as e:
#         print(f"Ошибка при выполнении mitmdump: {e}")


def start_noir(noir_path: str, target_dir: str):
    target_domain_name = input("Укажите адрес и порт Объекта Оценки): ")

    if not os.path.isfile(noir_path):
        raise FileNotFoundError(f"Noir не найден по пути: {noir_path}")
    
    if not os.path.isdir(target_dir):
        raise NotADirectoryError(f"Указанный каталог не существует: {target_dir}")
    
    try:
        result = subprocess.run([noir_path, " -b ", target_dir, " -u ", 
                                target_domain_name, " --send-proxy http://localhost:8081 ", 
                                "--format", " json", " --output ", "noir_output.json"], check=False)
        return result.returncode
    except Exception as e:
        raise RuntimeError(f"Ошибка при запуске Noir: {e}")


def start_proxy(selected_dir):
    # TO DO:
    output_file = ""
    
    # Формируем команду для mitmproxy
    command = [
        "mitmproxy",
        "-w", "traffic.flow",
        "-p", "8081",
        "--set", "stream_large_bodies=0"
    ]
    # TO DO:
    print(f"Трафик записан в файл: {output_file}")


def check_dir():
    # Получаем и сортируем список директорий в текущей папке
    directories = sorted([d for d in os.listdir() if os.path.isdir(d)])

    if not directories:
        print("В текущей папке нет директорий.")
        exit()

    #список директорий с номерами
    for i, dir in enumerate(directories, 1):
        print(f"{i}. {dir}")

    try:
        choice = int(input("Введите номер директории с исходным кодом ОО: "))
        selected_dir = directories[choice - 1]
        
        ########################
        ###START PROXY & NOIR###
        ########################
        start_proxy(selected_dir)
        exit_code = start_noir("/opt/noir/bin/noir", selected_dir)
        if exit_code == 0:
            print("Анализ завершён успешно.")
        else:
            print(f"NOIR ERROR: {exit_code}")

    except IndexError:
        print("Неправильный номер директории.")


#
# --set stream_large_bodies=0 флаг для оптимизации работы прокси
#        subprocess.run(["mitmdump -r endpoints.flow --export-curl > requests.sh", selected_dir])
