"""
Прочее:
BackgroundCommand(command) – запустить фоновую команду
stop() или stop(hashMap) – точка останова для отладки
"""


def toast(message: str):
    """Вывести сообщение Андроид"""
    pass


def speak(message: str):
    """произнести текст (TTS engine)"""
    pass


def listen():
    """запустить ожидание распознавания речи"""
    pass


def vibrate(duration: int = 1):
    """вибрация и вибрация заданной длительности"""
    pass


def beep(tone: int = 1, beep_duration: int = 1, beep_volume: int = 1):
    """звуковой сигнал, т.ч. с возможностью выбрать тон (от 1 до 99), продолжительность
     и громкость (по умолчанию – 100)"""
    pass


def playsound(sound: int):
    pass


def RunEvent(handlers: str):
    """
    запустить массив обработчиков
    [{
    action: run|runasync|runprogress»,
    type: python|online|http|sql|pythonargs|…,
    method: handlerName|parameters,
    postExecute: {<handler description>}
    }]
    """
    pass


def notification(text: str, title: str = None, number: int = None):
    """уведомление в шторке уведомлений. Number – идентификатор уведомления, по которому к нему можно потом обратиться,
     чтобы либо убрать, либо перезаписать (обновить)"""
    pass


def notification_progress(text: str, title: str, number: int, progress: int):
    """уведомление с прогресс-баром (от 0 до 100)"""
    pass


def notification_cancel(number: int = None):
    """убрать уведомление"""
    pass


def refresh_screen(hash_map):
    """Обновить экран"""
    pass
