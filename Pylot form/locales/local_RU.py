#RU local for Pylot form

cmds_dict = {
    "связь": "command",
    "взлёт": "takeoff",
    "взлет": "takeoff",
    "приземление": "land",
    "камера_вкл": "streamon",
    "камера_выкл": "streamoff",
    "авария": "emergency",
    "вверх": "up",
    "вниз": "down",
    "влево": "left",
    "вправо": "right",
    "вперёд": "forward",
    "вперед": "forward",
    "назад": "back",
    "по_часовой": "cw",
    "против_часовой": "ccw",
    "кувырок": "flip",
    "лети": "go",
    "дуга": "curve",
    "скорость": "speed",
    "снимок": "snapshot",
    "запись": "scanning",
    "ждать": "sleep",
    "повтори": "repeat",
    "повторить": "repeat",
    "конец_цикла": "done",
    "кц": "done",
}

tello_params_dict = {
    "pitch": "Тангаж",
    "roll": "Крен",
    "yaw": "Рысканье",
    "vgx": "Скрость X",
    "vgy": "Скрость Y",
    "vgz": "Скрость Z",
    "templ": "Температура мин",
    "temph": "Температура макс",
    "tof": "Высота (см)",
    "h": "Вертикальное ускорение",
    "bat": "Батарея",
    "baro": "Барометр",
    "time": "Время",
    "agx": "Ускорение X",
    "agy": "Ускорение Y",
    "agz": "Ускорение Z",
}


end_of_init = "Конец инициализации"

took_photo_ok = "Сделал фото"
took_photo_not_ok = "Не смог сделать фото"
skanning_stop = "Остановил сканирование"
skanning_start = "Начал сканирование с частотой (сек):"

clean_log = "Очистить лог"

open_file = "Открыть"
save_file = "Сохранить"

run_code_break = "Прервать"
run_code_start = "Запустить"

run_code_sleep = "Сплю секунд:"
run_code_begin = "Начинаю выполнение кода"
run_code_command = "Выполняю команду:"
run_code_response = "Статус завершения:"
run_code_finished = "Завершил выполнение кода"

disconnect_dron = "Отключить"
connect_to_dron = "Подключить"

tello_connected = "Tello подключён"
tello_disconnected = "Tello отключён"

cant_connect_drone = "Не могу подключиться к дрону"

norun_syntax_error = "Не могу начать выполнение, ошибка: "
norun_not_connected = "Не могу начать выполнение, дрон не подключён"
