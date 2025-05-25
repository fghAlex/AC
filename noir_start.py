import os
import subprocess
import time

def start_proxy_for_send_traffic(input_file="/tmp/all.sh", log_file="/tmp/curl_execution.log"):

        # Проверяем, существует ли входной файл
    if not os.path.isfile(input_file):
        print(f"Ошибка: файл {input_file} не найден.")
        return False

    # Открываем лог-файл для записи
    try:
        with open(log_file, 'w') as log:
            log.write(f"Начало выполнения cURL-команд из {input_file}\n")
            log.flush()

            # Читаем файл построчно
            with open(input_file, 'r') as file:
                for line_number, line in enumerate(file, 1):
                    line = line.strip()
                    # Проверяем, начинается ли строка с 'curl '
                    if line.startswith('curl '):
                        log.write(f"\n[Строка {line_number}] Выполняется: {line}\n")
                        log.flush()
                        try:
                            # Выполняем команду cURL
                            result = subprocess.run(
                                line,
                                shell=True,
                                capture_output=True,
                                text=True,
                                timeout=0.1
                            )
                            # Записываем результат в лог
                            log.write(f"Вывод (stdout): {result.stdout}\n")
                            log.write(f"Ошибки (stderr): {result.stderr}\n")
                            log.write(f"Код возврата: {result.returncode}\n")
                            if result.returncode != 0:
                                print(f"Предупреждение: команда в строке {line_number} завершилась с ошибкой (код {result.returncode})")
                        except subprocess.TimeoutExpired:
                            log.write(f"Ошибка: команда в строке {line_number} превысила таймаут\n")
                            print(f"Ошибка: команда в строке {line_number} превысила таймаут")
                        except subprocess.SubprocessError as e:
                            log.write(f"Ошибка выполнения команды в строке {line_number}: {e}\n")
                            print(f"Ошибка выполнения команды в строке {line_number}: {e}")
                    else:
                        log.write(f"[Строка {line_number}] Пропущена (не начинается с 'curl '): {line}\n")
                        log.flush()

            print(f"Выполнение завершено. Логи сохранены в {log_file}")
            return True

    except IOError as e:
        print(f"Ошибка работы с файлами: {e}")
        return False

    return 

def run_mitm_command(working_dir, output_file, docker_command, container_name):
    """
    Запускает Docker-контейнер с mitmdump в фоновом режиме.
    
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
                print(f"Контейнер mitmdump запущен с ID {container_id}, порт 8080, трафик записывается в {output_file}.")
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
    target_domain_name = input("Укажите протокол и адрес Объекта Оценки: ")

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

    docker_command = [
            "docker", "run", "-d",
            "--name", container_name,
            "-p", "8080:8080",
            "-v", "/tmp:/app/reports",
            "mitmproxy/mitmproxy:12",
            "mitmdump", "-q", "-w", f"/app/reports/{output_file}", "-p", "8080", "--set", "stream_large_bodies=0"
    ]
    run_mitm_command(flow_proj, output_file, docker_command, container_name)
    print(f"container start proxy name:{container_name}")
    return container_name

def export_proxy_traffic_to_curl(flow_proj, output_file):
        
    # Проверяем, существует ли директория
    if not os.path.isdir(flow_proj):
        print(f"Ошибка: директория {flow_proj} не существует.")
        return None

    container_name = f"mitmdump-{int(time.time())}"  # Уникальное имя контейнера
    
    # Формируем команду docker run
    # Формируем команду для экспорта в cURL
    docker_command = [
        "docker", "run", "--rm",
        "--name", container_name,
        "-v", f"/tmp:/app/reports",
        "--entrypoint", "/bin/sh",
        "mitmproxy/mitmproxy:12",
        "-c", f"mitmdump -r /app/reports/{output_file} -s /app/reports/curl_export.py > /app/reports/all.sh"
    ]
    return run_mitm_command(flow_proj, output_file, docker_command, container_name)

def stop_mitm_container(container_id):
    """
    Останавливает и удаляет Docker-контейнер.

    """
    print(f"container start proxy name:{container_id}")

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
    print(f"container start proxy name:{container_id}")

    exit_code = start_noir("/usr/local/sbin/noir", selected_dir)
    if exit_code == 0:
        print("Анализ завершён успешно.")
    else:
        print(f"NOIR ERROR: {exit_code}")

    if container_id:
        input("Нажмите Enter, чтобы остановить контейнер...")
        stop_mitm_container(container_id)

    question = input("Экспортировать ли записанный трафик в формате curl? y/N: ").strip().lower()
    if question=="y":
        export_proxy_traffic_to_curl(flow_proj, output_file)
    return 

