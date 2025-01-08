# Токен бота
# BOT_TOKEN = "7662603311:AAEY1zt0K9n-4fqmOqw8CgVlBgnlxtJERlE" # основной
BOT_TOKEN = "7763014026:AAHOr50tNNxvoGaoySjlqr8XPHTHiPciMTU" # тестовый

# IDs администраторов
ADMIN_IDS = [417644461]

HOMEWORK_OPTIONS = {
    "ЕГЭ": {
        "Задание 1": "https://forms.gle/Lmywfx3ayJxZLpZK9",
        "Задание 2": "https://forms.gle/Fkft5igc7wrujWqA8",
        "Задание 3": "https://forms.gle/eTgQ5RxsUefXFaiB7",
        "Задание 4": "https://forms.gle/adZB7nUJtZjGB9WV6",
        "Задание 5": "https://forms.gle/8zqoUhqJ9hGJvBGdA",
        "Задание 6": "https://forms.gle/6YMpBnQGZG5GC8Rr5",
        "Задание 7": "https://forms.gle/nmc27R5xmzkyiaBaA",
        "Задание 8": "https://forms.gle/vvr6WqZJn7ZDFE4s8",
        "Задание 10": "https://forms.gle/mMT1KptJZ4ZPNQzaA",
        "Задание 11": "https://forms.gle/M3UV82U4stsPm99t5",
        "Задание 12": "https://forms.gle/h3Rmh4LEY8HBKn7fA",
        "Задание 13": "https://forms.gle/Gt7UK4fKxxG3A83NA",
        "Задание 14": "https://forms.gle/y6V2bzCVGUvdDFPw8",
        "Задание 15": "https://forms.gle/YCFkQCGSdqQJqX6n7",
        "Задание 16": "https://forms.gle/frjL29ULrgH5uhUQ9",
        "Задание 18": "https://forms.gle/FQyVFykPigeU3XRu8",
        "Задание 19-21": "https://forms.gle/Xtzt5kqwpv5kvbmK6"
    },
    "ОГЭ": {
        "Задание 1": "https://clck.ru/3FNGf9",

    }
}

NOTES_OPTIONS = {
    "ЕГЭ": {
        "Задание 1": "https://drive.google.com/file/d/1bQg-sAg5Bst24XkmMO7XAaF9l3dh7c2c/view?usp=sharing",
        "Задание 2": "https://drive.google.com/file/d/17MiU9r4tNDCEhkmENAiaVsF0PPgomESU/view?usp=sharing",
        "Задание 3": "https://drive.google.com/file/d/1B_zZJRtCKpmtgqQxU160W_--Oivk1wzC/view?usp=sharing",
        "Задание 4": "https://drive.google.com/file/d/1B_zZJRtCKpmtgqQxU160W_--Oivk1wzC/view?usp=sharing",
        "Задание 7": "https://drive.google.com/file/d/1B_zZJRtCKpmtgqQxU160W_--Oivk1wzC/view?usp=sharing",
        "Задание 9": "https://drive.google.com/file/d/1B_zZJRtCKpmtgqQxU160W_--Oivk1wzC/view?usp=sharing",
        "Задание 10": "https://drive.google.com/file/d/1B_zZJRtCKpmtgqQxU160W_--Oivk1wzC/view?usp=sharing",
        "Задание 11": "https://drive.google.com/file/d/1B_zZJRtCKpmtgqQxU160W_--Oivk1wzC/view?usp=sharing",
        "Задание 12": "https://drive.google.com/file/d/1B_zZJRtCKpmtgqQxU160W_--Oivk1wzC/view?usp=sharing",
        "Задание 16": "https://drive.google.com/file/d/1B_zZJRtCKpmtgqQxU160W_--Oivk1wzC/view?usp=sharing",
        "Задание 19-21": "https://drive.google.com/file/d/1B_zZJRtCKpmtgqQxU160W_--Oivk1wzC/view?usp=sharing",
        "Задание 22": "https://drive.google.com/file/d/1B_zZJRtCKpmtgqQxU160W_--Oivk1wzC/view?usp=sharing"
    },
    "ОГЭ": {
        "Конспект 1": "https://drive.google.com/file/d/1bQg-sAg5Bst24XkmMO7XAaF9l3dh7c2c/view?usp=sharing",
        "Конспект 2": "https://example.com/ege_note2",
        "Конспект 3": "https://example.com/ege_note3"
    }
}

CHOOSING, TYPING_NAME, TYPING_EXAM, DELETING, STUDENT_LOGIN, STUDENT_MENU, ADD_VARIANT, ADD_VARIANT_LINK, \
 TYPING_CLASS_LINK, TYPING_CLASS_DATE, CHOOSING_FIELD, UPDATING_FIELD, CONFIRMATION, ADD_EXAM, ADD_TITLE, \
    ADD_LINK, CHOOSE_HOMEWORK_EXAM, CHOOSE_HOMEWORK_STUDENT, CHOOSE_HOMEWORK_ASSIGNMENT = range(19)



# Добавляем всё в __all__
__all__ = [
    "BOT_TOKEN",
    "ADMIN_IDS",
    "HOMEWORK_OPTIONS",
    "NOTES_OPTIONS",
    "CHOOSING", "TYPING_NAME", "TYPING_EXAM", "DELETING", "STUDENT_LOGIN", "STUDENT_MENU",
    "ADD_VARIANT", "ADD_VARIANT_LINK", "TYPING_CLASS_LINK", "TYPING_CLASS_DATE",
    "CHOOSING_FIELD", "UPDATING_FIELD", "CONFIRMATION",
    "ADD_EXAM", "ADD_TITLE", "ADD_LINK",
]
