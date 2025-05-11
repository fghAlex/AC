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

def run_mitm_command(command, working_dir):

    # Проверяем, существует ли директория
    if not os.path.isdir(working_dir):
        print(f"Ошибка: директория {working_dir} не существует.")
        return False

    try:
        # Выполняем команду с указанием рабочей директории
        subprocess.run(command, cwd=working_dir, check=True)
        print(f"Команда {command[0]} успешно выполнена в директории {working_dir}.")
        return True
    except FileNotFoundError:
        print(f"Ошибка: команда {command[0]} не найдена. Убедитесь, что она установлена.")
        return False
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при выполнении команды: {e}")
        return False




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


def start_proxy(flow_proj):
    output_file = "traffic.flow"

    # Формируем команду для mitmproxy
    record_command = [
        "mitmproxy",
        "-w", output_file,
        "-p", "8081",
        "--set", "stream_large_bodies=0", "&"
    ]
    print("Записываем трафик...")
    print(flow_proj)
    return run_mitm_command(record_command, flow_proj)


def stop_process(process):
    """
    Завершает процесс mitmproxy.

    :param process: Объект процесса Popen
    """
    if process:
        process.terminate()
        process.wait()
        print("mitmproxy остановлен.")
    else:
        print("Процесс не был запущен.")


def check_dir(flow_proj):
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
        print(selected_dir)
        ########################
        ###START PROXY & NOIR###
        ########################
        mitm_process = start_proxy(flow_proj)
        print(f"Трафик записан в файл.")

        exit_code = start_noir("/opt/noir/bin/noir", selected_dir)
        if exit_code == 0:
            print("Анализ завершён успешно.")
        else:
            print(f"NOIR ERROR: {exit_code}")
        stop_process(mitm_process)
    except IndexError:
        print("Неправильный номер директории.")


#
# --set stream_large_bodies=0 флаг для оптимизации работы прокси
#        subprocess.run(["mitmdump -r endpoints.flow --export-curl > requests.sh", selected_dir])
