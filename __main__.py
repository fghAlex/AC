import os
import subprocess
import time
import noir_start
import natch_start

def check_start_containers():
    time.sleep(5)

    # Получаем статус контейнеров
    output = subprocess.check_output(['docker-compose', 'ps'])
    lines = output.decode().splitlines()

    # Проверяем, есть ли контейнеры в выводе (минимум 3 строки: заголовок, разделитель и данные)
    if len(lines) < 3:
        print("Ошибка: контейнеры не найдены.")
        while i < 100:
            time.sleep(10)

            output = subprocess.check_output(['docker-compose', 'ps'])
            lines = output.decode().splitlines()
            i=i+1
            print(f"Ожидание запуска контейнеров. Выполнено попыток проверки: {i}")

            if len(lines) > 3:
                return True
    return True

def main():
    # Получаем текущую директорию, где запущен скрипт
    current_dir = os.getcwd()
    
    # Получаем и сортируем список директорий в текущей папке
    directories = sorted([d for d in os.listdir() if os.path.isdir(d)])

    if not directories:
        print("В текущей папке нет директорий.")
        exit()

    # список директорий с номерами
    for i, dir in enumerate(directories, 1):
        print(f"{i}. {dir}")
    
    choice = int(input("Введите номер выбранного проекта: "))
    selected_proj = directories[choice - 1]
    flow_proj = os.path.join(current_dir, selected_proj)

    try:
        os.chdir(flow_proj)
    except FileNotFoundError:
        print(f"Директория '{flow_proj}' не найдена!")
        exit(1)

    ######################
    ###CONTAINRES START###
    ######################

    question = input("Запускать docker-compose? y/N: ")

    if question=="y":
        current_dir = os.getcwd()
        compose_file = os.path.join(current_dir, 'docker-compose.yml')

        # Проверяем, существует ли файл docker-compose.yml
        if not os.path.isfile(compose_file):
            print("docker-compose.yml не найден в текущей директории.")
            exit(1)
            compose_file = os.path.join(current_dir, 'compose.yml')
            if not os.path.isfile(compose_file):
                print("compose.yml не найден в текущей директории.")
                exit(1)
        
        # Запускаем docker-compose up -d
        print("Запуск контейнеров")
        try:
            subprocess.run(['docker-compose', 'up', '-d'], check=True)
            print("docker-compose up -d выполнено.")
        except subprocess.CalledProcessError as e:
            print(f"Ошибка при выполнении docker-compose up -d: {e}")
            exit(1)

        check_start_containers()

    ######################
    ###NOIR+PROXY START###
    ######################
    noir_start.check_dir(flow_proj) # в переменной flow_proj хранится директория с прокетом.
    print(f"Выбран проект: {flow_proj}.")

    #TO DO: Спросить нужно ли экспорт из прокси запросы в curl формат. 

    #################
    ###NATCH START###
    #################
    file_extension = '.qcow2'

    question = input("Запускать Natch? y/N: ")
    if question=="y":
        natch_start.start()

    return

if __name__ == '__main__':
    main()