import os
import configparser
import pexpect
import subprocess
from subprocess import Popen
import time
import noir_start
import sys

def check_dir(current_directory):

    # Расширение файла для проверки
    file_extension = '.qcow2'

    # Получаем список всех файлов в текущей директории
    files_in_directory = os.listdir(current_directory)

    # Проверяем наличие файлов с указанным расширением
    for file in files_in_directory:
        if file.endswith(file_extension):
            print(f"В {current_directory} найден образ ВМ: {file}")
            return file
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
        'emu_mode': 'text',
        'port_forwarding': 'True',
        'source_ports': 'True',
        'module_config': 'True',
        'tuning': 'True',
        'debug_info': 'True'
    }

    # Запрашиваем ввод пользователя для двух переменных
    ports_str_value = input("Введите порт, траффик которого требуется помечать: ")
    guest_module_dir_value = input("Введите путь для бинарными файлами в гостевой ОС: ")

    # Устанавливаем введенные значения
    config.set('Settings', 'ports_str', ports_str_value)
    config.set('Settings', 'guest_module_dir', guest_module_dir_value)

    # Сохраняем изменения в файле settings_test.ini
    with open('settings_test.ini', 'w') as configfile:
        config.write(configfile)

    print(f'Файл settings_test.ini успешно создан.')
    return

def natch_create_proj(flow_proj, projName, qcow2Path ):
    subprocess.run(["natch", "create", "-c",  "settings_test.ini", projName, qcow2Path], check=False)
    return

def natch_replay(sample, projName, choice):
    
    target_path = os.path.join(os.getcwd(), projName)

    child = pexpect.spawn(
        f'bash -c "cd \"{target_path}\" && natch replay -s \"{sample}\" -S auto"',
        timeout=2400
    )

    child.logfile = sys.stdout.buffer  # Перенаправляем stdout в буфер stdout
    
    try:
        while True:
            index = child.expect([
                'Continue?',   # подтверждение запрашивается
                'completed!',  # всё хорошо, завершение успешно
                'natch-qemu-', # ошибка во время воспроизведения
                pexpect.EOF    # конец вывода
            ])
            
            if index == 0:  # продолжение
                child.sendline('')
                
                subindex = child.expect(['completed!', 'natch-qemu-'])
                if subindex == 0:  # успешное завершение
                    break
                elif subindex == 1:  # ошибка
                    raise Exception('Error occurred during replay')
                    
            elif index == 1:  # успешное завершение
                break
            elif index == 2:  # ошибка
                raise Exception('Error occurred during replay')
            else:  # EOF
                break
        
    except pexpect.TIMEOUT as e:
        print("Timeout reached:", str(e))
    
    finally:
        log_file_path = f'/tmp/replaystdout_{sample}.log'
        if child.before is not None:
            log_file_path = f'/tmp/replaystdout_{sample}.log'
            with open(log_file_path, 'wb') as logfile:
                logfile.write(child.before)
        else:
            print("Нет данных для записи в лог.")
    return

def natch_record(sample, flow_proj, projName, choice):
        
    target_path = os.path.join(os.getcwd(), projName)

    child = pexpect.spawn(
        f'bash -c "cd \"{target_path}\" && natch record -s {sample}',
        timeout=2400
    )

    child.logfile = sys.stdout.buffer  # Перенаправляем stdout в буфер stdout

    # Обрабатываем диалог входа в систему
    try:
        index = child.expect(["login:", "Password:"], timeout=2400)
        username = ""
        password = ""

        if index == 0:  # Если увидели prompt "login:"
            username = input("Введите имя пользователя на ВМ:")
            child.sendline(username)  # Отсылаем имя пользователя
            
            # Ждем появления password prompt
            child.expect("Password:")
            password = input("Введите пароль:")
            child.sendline(password)  # Отсылаем пароль
        
        elif index == 1:  # Если сразу появился password prompt
            password = input("Введите пароль:")
            child.sendline(password)  # Отсылаем пароль
        
        # Первая проверка приглашения
       # child.expect([pexpect.EOF, pexpect.TIMEOUT, "\\$ ", "#", "%"], timeout=300)

        # Основной цикл для ввода команд
        #while True:
         #   print("Введите команду запуска ПП:")
          #  command = input()
         #   child.sendline(command)
         #   question = input("Программный продукт запущен? y/N: ").strip().lower()
         #   if question == "y":
         #        break

    except pexpect.TIMEOUT as e:
        print("Ошибка ожидания!")
    except Exception as ex:
        print(f"Произошла ошибка: {ex}")


    # Запускаем клиент Telnet
    mon_child = pexpect.spawn('telnet localhost 7799')

    # Получаем идентификатор текущего соединения
    #tnID = child.ptyproc.pid  # аналогично "$spawn_id" в Tcl

    # Ожидаем появления подсказки "(natch)" от QEMU
    # Запускаем клиент Telnet
    mon_child.expect('(natch)')

    # Отправляем команду "savevm autosave"
    mon_child.sendline('savevm auto')

    # Ещё раз ожидаем подсказку "(natch)", чтобы подтвердить успешное сохранение
    mon_child.expect('(natch)')

    # Выводим итоговый результат
    print("Состояние после выполнения команды:", mon_child.before.decode())




    # Запуск прокси
    output_file_noir = "traffic.flow"
    noir_start.start_proxy_for_send_traffic(flow_proj, output_file_noir)

    time.sleep(5)


    #  Отлючаем ВМ
    mon_child.sendline('quit')

    # Выводим итоговый результат
    print("Состояние после выполнения команды:", mon_child.before.decode())

    # Закрываем соединение
    mon_child.close()

    return

def start(flow_proj, choice):
    
    current_directory = os.getcwd()
    files_in_directory = check_dir(current_directory)
    print("Выполняется создание проекта natch.")
    natch_create_config()
    projName = "auto"
#    natch_create_proj(flow_proj, projName, files_in_directory)
    sample = "auto"
    natch_record(sample, flow_proj, projName, choice)
    natch_replay(sample, projName, choice)

    return
