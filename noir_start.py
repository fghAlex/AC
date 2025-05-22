import os
import subprocess
import time

def start_proxy_for_send_traffic(flow_proj, output_file):
    # Проверяем, существует ли директория
    if not os.path.isdir(flow_proj):
        print(f"Ошибка: директория {flow_proj} не существует.")
        return None

    container_name = f"mitmdump-{int(time.time())}"  # Уникальное имя контейнера
    volume_path = os.path.join(flow_proj, "reports")  # Папка для тома

    # Создаем папку для тома, если её нет
    os.makedirs(volume_path, exist_ok=True)

    docker_command = [
    "docker", "run", "--rm",
    "--name", container_name,
    "-v", f"{volume_path}:/app/reports",
    "mitmproxy:1",
    "mitmdump",
    "-q",
    "-r", f"/app/reports/{output_file}",   # читаем из дампа
    "--mode", "transparent",               # отключает перехват, запросы идут напрямую
    "--set", "stream_large_bodies=0"
    ] 

    return run_mitm_command(flow_proj, output_file, docker_command, container_name, volume_path)

def run_mitm_command(working_dir, output_file, docker_command, container_name, volume_path):
    """
    Запускает Docker-контейнер с mitmdump в фоновом режиме.
    
    :param working_dir: Путь к директории на хосте для тома и логов
    :param output_file: Имя файла для записи трафика (внутри тома)
    :return: ID контейнера или None в случае ошибки
    """

    log_file = os.path.join(working_dir, "mitmproxy.log")

    try:
        # Запускаем контейнер
        with open(log_file, 'w') as log:
            process = subprocess.Popen(
                docker_command,
                stdout=log,
                stderr=log,
                text=True
            )
        # Ждем, чтобы убедиться, что процесс запустился
        time.sleep(3)  # Даем время на запуск контейнера

        # Проверяем, что процесс docker run завершился успешно
        if process.poll() is None or process.returncode == 0:
            # Получаем ID контейнера
            container_id = subprocess.check_output(
                ["docker", "ps", "-q", "-f", f"name={container_name}"],
                text=True
            ).strip()
            if container_id:
                print(f"Контейнер mitmdump запущен с ID {container_id}, порт 8080, трафик записывается в {os.path.join(volume_path, output_file)}.")
                print(f"Логи сохранены в {log_file}.")
                print("Записываем трафик...")
            else:
                print("Ошибка: контейнер не найден. Проверьте логи.")
                return None
        else:
            print("Ошибка: команда docker run завершилась с ошибкой. Проверьте логи.")
            return None

        return container_id
    except FileNotFoundError:
        print("Ошибка: Docker не найден. Убедитесь, что он установлен.")
        return None
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при запуске контейнера: {e}")
        return None



def start_noir(noir_path: str, target_dir: str):
    target_domain_name = input("Укажите протокол, адрес и порт Объекта Оценки: ")

    if not os.path.isfile(noir_path):
        raise FileNotFoundError(f"Noir не найден по пути: {noir_path}")   
    if not os.path.isdir(target_dir):
        raise NotADirectoryError(f"Указанный каталог не существует: {target_dir}")
    try:
        result = subprocess.run([noir_path, "-b", target_dir, "-u", 
                                target_domain_name, "--send-proxy",  "http://localhost:8080", 
                                "--format", "json", "--output", "noir_output.json"], check=False)
        return result.returncode
    except Exception as e:
        raise RuntimeError(f"Ошибка при запуске Noir: {e}")


def start_proxy(flow_proj, output_file):

    # Проверяем, существует ли директория
    if not os.path.isdir(flow_proj):
        print(f"Ошибка: директория {flow_proj} не существует.")
        return None

    container_name = f"mitmdump-{int(time.time())}"  # Уникальное имя контейнера
    volume_path = os.path.join(flow_proj, "reports")  # Папка для тома

    # Создаем папку для тома, если её нет
    os.makedirs(volume_path, exist_ok=True)

    docker_command = [
            "docker", "run", "-d",
            "--name", container_name,
            "-p", "8080:8080",
            "-v", f"{volume_path}:/app/reports",
            "mitmproxy:1",
            "mitmdump", "-q", "-w", f"/app/reports/{output_file}", "-p", "8080", "--set", "stream_large_bodies=0"
    ]
    return run_mitm_command(flow_proj, output_file, docker_command, container_name, volume_path)

def export_proxy_traffic_to_curl(flow_proj, output_file):
        
    # Проверяем, существует ли директория
    if not os.path.isdir(flow_proj):
        print(f"Ошибка: директория {flow_proj} не существует.")
        return None

    container_name = f"mitmdump-{int(time.time())}"  # Уникальное имя контейнера
    volume_path = os.path.join(flow_proj, "reports")  # Папка для тома

    # Создаем папку для тома, если её нет
    os.makedirs(volume_path, exist_ok=True)
    
    # Формируем команду docker run
    docker_command = [
    "docker", "run", "--rm",
    "--name", container_name,
    "-v", f"{volume_path}:/app/reports",
    "mitmproxy:1",
    "sh", "-c",
    "mitmdump -r /app/reports/{output_file} --export-curl > /app/reports/all.sh"
    ]
    return run_mitm_command(flow_proj, output_file, docker_command, container_name, volume_path)

def stop_mitm_container(container_id):
    """
    Останавливает и удаляет Docker-контейнер.
    
    :param container_id: ID контейнера
    """
    if container_id:
        try:
            subprocess.run(["docker", "stop", container_id], check=True)
            subprocess.run(["docker", "rm", container_id], check=True)
            print(f"Контейнер {container_id} остановлен и удален.")
        except subprocess.CalledProcessError as e:
            print(f"Ошибка при остановке контейнера: {e}")
    else:
        print("Контейнер не был запущен.")


def check_dir(flow_proj):
    # Получаем и сортируем список директорий в текущей папке
    directories = sorted([d for d in os.listdir() if os.path.isdir(d)])

    if not directories:
        print("В текущей папке нет директорий.")
        exit()

    #список директорий с номерами
    for i, dir in enumerate(directories, 1):
        print(f"{i}. {dir}")

    choice = int(input("Введите номер директории с исходным кодом ОО: "))
    selected_dir = directories[choice - 1]
    print(selected_dir)
    ########################
    ###START PROXY & NOIR###
    ########################
    output_file = "traffic.flow"
    container_id = start_proxy(flow_proj, output_file)

    exit_code = start_noir("/opt/noir/bin/noir", selected_dir)
    if exit_code == 0:
        print("Анализ завершён успешно.")
    else:
        print(f"NOIR ERROR: {exit_code}")

    #TO DO нужна ли еще эта проверка?
    if container_id:
        input("Нажмите Enter, чтобы остановить контейнер...")
        stop_mitm_container(container_id)

    question = input("Экспортировать ли записанный трафик в формате curl? y/N").strip().lower()
    if question=="y":
        export_proxy_traffic_to_curl(flow_proj, output_file)
    return 

