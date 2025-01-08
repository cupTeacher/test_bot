import datetime
from database import *
from handlers.modify import *
from handlers.student import student_menu, student_login, handle_student_menu, handle_show_student_info, return_to_student_menu


async def add_student(update: Update, context: CallbackContext):
    markup = ReplyKeyboardMarkup([['Вернуться в меню']], one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("Введите имя ученика или нажмите 'Вернуться в меню':", reply_markup=markup)
    return TYPING_NAME


# Обработка выбора в меню администратора
async def handle_choice(update: Update, context: CallbackContext):
    choice = update.message.text  # Текст выбранной кнопки

    if choice == 'Добавить ученика':
        return await add_student(update, context)
    elif choice == 'Удалить ученика':
        return await delete_student(update, context)
    elif choice == 'Выдать домашнее задание':
        await update.message.reply_text("Вы можете выдать домашнее задание!")
        return await start_give_homework(update, context)
    elif choice == 'Добавить вариант':
        return await add_variant(update, context)
    elif choice == 'Внести изменения':
        return await modify_student(update, context)
    elif choice == 'Информация об ученике':
        return await show_student_info(update, context)
    elif choice == 'Добавить домашнее задание':
        # 1) НЕ возвращаем ADD_EXAM!
        # 2) Либо предлагаем набрать /add_homework:
        await update.message.reply_text(
            "Чтобы добавить домашнее задание, введите команду /add_homework",
            reply_markup=ReplyKeyboardRemove()
        )
        # 3) Остаёмся в текущем состоянии (CHOOSING),
        #    или делаем что-то ещё, но главное — не возвращаем чужие состояния:
        return CHOOSING
    else:
        await update.message.reply_text("Я не ожидал такого действия. Попробуйте снова.")
        return CHOOSING


# Основная логика старта
async def start(update: Update, context: CallbackContext):
    """Обработчик команды /start."""
    # Сбрасываем данные пользователя и начинаем с нуля
    context.user_data.clear()
    user_id = update.message.from_user.id

    if user_id in ADMIN_IDS:
        # Администраторское меню
        return await return_to_menu(update, context)
    else:
        # Логика для учеников
        user = get_user_by_telegram_id(user_id)
        if user:
            user_id, name, exam = user
            await update.message.reply_text(f"Добро пожаловать, {name}!\nВы зарегистрированы на экзамен: {exam}.")
            return await student_menu(update, context)
        else:
            await update.message.reply_text("Добро пожаловать в личный кабинет ученика. Введите пароль для входа:")
            return STUDENT_LOGIN


async def return_to_menu(update: Update, context: CallbackContext):
    # Определяем пользователя: администратор или ученик
    user_id = update.callback_query.from_user.id if update.callback_query else update.message.from_user.id

    if user_id in ADMIN_IDS:
        # Администраторское меню
        reply_markup = ReplyKeyboardMarkup(
            [
                ['Выдать домашнее задание', 'Добавить вариант'],  # Первая строка
                ['Внести изменения', "Информация об ученике"],  # Вторая строка
                ['Добавить ученика', 'Удалить ученика'], # Третья строка
                ['Добавить домашнее задание', 'Удалить домашнее задание']  # Третья строка
            ],
            resize_keyboard=True
        )
        message = "Вы в меню администратора:"
        if update.message:
            await update.message.reply_text(message, reply_markup=reply_markup)
        elif update.callback_query:
            await update.callback_query.answer()
            await update.callback_query.edit_message_text(message)
        return CHOOSING
    else:
        # Вызываем функцию меню ученика
        return await student_menu(update, context)


# Обработка ввода имени ученика
async def handle_name(update: Update, context: CallbackContext):
    if update.message.text == 'Вернуться в меню':
        context.user_data.clear()  # Очищаем данные пользователя
        return await return_to_menu(update, context)

    # Сохраняем имя ученика в контексте
    context.user_data['student_name'] = update.message.text
    markup = ReplyKeyboardMarkup([['ОГЭ'], ['ЕГЭ'], ['Вернуться в меню']], one_time_keyboard=True,
                                 resize_keyboard=True)
    await update.message.reply_text("Выберите экзамен (ОГЭ или ЕГЭ) или нажмите 'Вернуться в меню':",
                                    reply_markup=markup)
    return TYPING_EXAM


# Обработка выбора экзамена
async def handle_exam_choice(update: Update, context: CallbackContext):
    if update.message.text == 'Вернуться в меню':
        context.user_data.clear()
        return await return_to_menu(update, context)

    exam = update.message.text
    context.user_data['exam'] = exam

    # Запрашиваем дату занятия
    await update.message.reply_text("Введите дату занятия в формате dd.mm.yyyy:")
    return TYPING_CLASS_DATE


async def handle_class_date(update: Update, context: CallbackContext):
    class_date = update.message.text
    try:
        # Проверяем формат даты
        datetime.datetime.strptime(class_date, "%d.%m.%Y")
    except ValueError:
        await update.message.reply_text("Неверный формат даты. Попробуйте снова (например, 25.12.2023):")
        return TYPING_CLASS_DATE

    context.user_data['class_date'] = class_date
    await update.message.reply_text("Введите ссылку для подключения к занятию:")
    return TYPING_CLASS_LINK


async def handle_class_link(update: Update, context: CallbackContext):
    class_link = update.message.text
    student_name = context.user_data.get('student_name')
    exam = context.user_data.get('exam')
    class_date = context.user_data.get('class_date')  # Получаем дату занятия из контекста

    if not student_name or not exam or not class_date:
        await update.message.reply_text("Ошибка: данные не найдены. Попробуйте снова.")
        return await return_to_menu(update, context)

    # Генерация пароля и сохранение ученика в базу данных
    password = add_user(student_name, exam)
    with sqlite3.connect('your_database.db') as conn:
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE users SET class_link = ?, class_date = ? WHERE name = ? AND exam = ?',
            (class_link, class_date, student_name, exam)
        )
        conn.commit()

    await update.message.reply_text(
        f"Ученик добавлен:\n"
        f"Имя: {student_name}\n"
        f"Экзамен: {exam}\n"
        f"Дата занятия: {class_date}\n"
        f"Ссылка на занятие: {class_link}\n"
        f"Пароль: {password}\n"
        "Сообщите эту информацию ученику."
    )

    context.user_data.clear()  # Очищаем данные пользователя
    return await return_to_menu(update, context)


# Обработка кнопки "Удалить ученика"
async def delete_student(update: Update, context: CallbackContext):
    students = get_all_users()
    if not students:
        await update.message.reply_text("Нет зарегистрированных учеников.")
        return await return_to_menu(update, context)

    # Формируем Inline-клавиатуру с именами учеников и экзаменами
    keyboard = [[InlineKeyboardButton(student[1],
                                      callback_data=f"delete_student:{student[0]}")] for student in students]
    keyboard.append([InlineKeyboardButton("Вернуться в меню", callback_data="return_to_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Отправляем сообщение с клавиатурой
    await update.message.reply_text("Выберите ученика для удаления или вернитесь в меню:", reply_markup=reply_markup)
    return None  # Текущий шаг остается


# Обработка выбора для удаления ученика
async def handle_delete_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data

    if data == "return_to_menu":
        await query.answer("Возврат в меню.")
        await return_to_menu(update, context)
        return CHOOSING  # Возвращаемся в состояние CHOOSING

    if data.startswith("delete_student:"):
        student_id = int(data.split(":")[1])

        # Получаем информацию об ученике (включая описание)
        with sqlite3.connect('your_database.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT name, exam, description FROM users WHERE id = ?', (student_id,))
            student = cursor.fetchone()

            if not student:
                await query.answer("Ученик не найден.")
                return CHOOSING  # Возвращаемся в состояние CHOOSING

            # Распаковка данных ученика
            name, exam, description = student
            description_text = f"\nОписание: {description}" if description else ""

            # Удаляем ученика из базы данных
            cursor.execute('DELETE FROM users WHERE id = ?', (student_id,))
            conn.commit()

        # Отправляем сообщение об удалении ученика
        await query.answer()
        await query.edit_message_text(f"Ученик {name} с экзаменом {exam} был удален.{description_text}")

        # Возвращаемся в меню администратора
        await return_to_menu(update, context)
        return CHOOSING  # Возвращаемся в состояние CHOOSING


async def give_homework(update: Update, context: CallbackContext):
    students = get_all_users()
    if not students:
        await update.message.reply_text("Нет зарегистрированных учеников.")
        return await return_to_menu(update, context)

    # Создаём Inline-клавиатуру для выбора ученика
    keyboard = []
    row = []  # Хранение текущей строки

    for idx, student in enumerate(students, start=1):
        # Добавляем кнопку в текущую строку
        row.append(InlineKeyboardButton(student[1], callback_data=f"select_student:{student[0]}"))

        # Если в строке уже три кнопки или последний элемент, добавляем её в клавиатуру
        if len(row) == 2 or idx == len(students):
            keyboard.append(row)
            row = []  # Очищаем строку для следующей группы

    # Добавляем кнопку "Вернуться в меню" отдельной строкой
    keyboard.append([InlineKeyboardButton("Вернуться в меню", callback_data="return_to_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Выберите ученика для выдачи задания или вернитесь в меню:",
                                    reply_markup=reply_markup)
    return None


async def handle_select_student(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data

    if data == "return_to_menu":
        await query.answer("Возврат в меню.")
        return await return_to_menu(update, context)

    # Обработка выбора ученика
    selected_student_id = int(data.split(":")[1])

    # Сохраняем ID выбранного ученика в context.user_data
    context.user_data['selected_student_id'] = selected_student_id

    # Определяем экзамен и описание ученика
    with sqlite3.connect('your_database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT exam, description FROM users WHERE id = ?', (selected_student_id,))
        result = cursor.fetchone()

    if not result:
        await query.answer("Ошибка: данные ученика не найдены.")
        return await return_to_menu(update, context)

    exam, description = result  # Извлекаем экзамен и описание
    description_text = f"\nОписание: {description}" if description else ""

    # Формируем Inline-клавиатуру с номерами заданий для выбранного экзамена
    homework_options = HOMEWORK_OPTIONS.get(exam, {})
    keyboard = []
    row = []

    for idx, (name, link) in enumerate(homework_options.items(), start=1):
        # Добавляем кнопку в текущую строку
        row.append(InlineKeyboardButton(name, callback_data=f"assign_homework:{idx}"))

        # Если строка заполнилась или это последний элемент, добавляем её в клавиатуру
        if len(row) == 3 or idx == len(homework_options):
            keyboard.append(row)
            row = []

    # Добавляем кнопку "Вернуться в меню" отдельной строкой
    keyboard.append([InlineKeyboardButton("Вернуться в меню", callback_data="return_to_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Отправляем сообщение с описанием (если есть)
    await query.answer()
    await query.edit_message_text(
        f"Выберите задание для ученика ({exam}):{description_text}",
        reply_markup=reply_markup
    )

async def handle_assign_homework(update: Update, context: CallbackContext):
    query = update.callback_query
    homework_key = int(query.data.split(":")[1]) - 1  # Преобразуем ключ в индекс
    selected_student_id = context.user_data.get('selected_student_id')

    # Получаем экзамен ученика
    with sqlite3.connect('your_database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT exam, class_date, telegram_id FROM users WHERE id = ?', (selected_student_id,))
        result = cursor.fetchone()

    if not result:
        await query.answer("Ошибка: экзамен или дата занятия не найдены.")
        return await return_to_menu(update, context)

    exam, class_date, telegram_id = result  # Извлекаем экзамен, дату занятия и Telegram ID

    # Получаем задание по экзамену и ключу
    homework_options = HOMEWORK_OPTIONS.get(exam, {})
    selected_homework = list(homework_options.values())[homework_key]  # Получаем ссылку

    if not selected_student_id:
        await query.answer("Ошибка: ученик не выбран.")
        return await return_to_menu(update, context)

    # Сохраняем задание в базе данных
    with sqlite3.connect('your_database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET homework = ? WHERE id = ?', (selected_homework, selected_student_id))
        conn.commit()

    # Уведомляем ученика
    if telegram_id:
        try:
            keyboard = [[InlineKeyboardButton("Открыть задание", url=selected_homework)]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await context.bot.send_message(
                chat_id=telegram_id,
                text="У вас обновилось домашнее задание. Нажмите на кнопку ниже, чтобы открыть:",
                reply_markup=reply_markup
            )
        except Exception as e:
            print(f"Не удалось уведомить ученика с ID {telegram_id}: {e}")

    # Формируем сообщение для администратора
    message = f"Задание назначено: {selected_homework}\nДата занятия: {class_date if class_date else 'Не указана'}"

    await query.answer()
    await query.edit_message_text(message)
    return await return_to_menu(update, context)


async def receive_homework(update: Update, context: CallbackContext):
    student_name = context.user_data.get('selected_student')
    # Если ученик выбран, сохраняем задание
    if student_name:
        if update.message.text:
            homework = update.message.text
            await update.message.reply_text(
                f"Задание для {student_name} сохранено:\n{homework}\nВозврат в меню."
            )

        # Удаляем данные о выбранном ученике из user_data
        context.user_data.pop('selected_student', None)

        # Возвращаемся в меню
        return await return_to_menu(update, context)

    await update.message.reply_text("Произошла ошибка. Попробуйте снова.")
    return await return_to_menu(update, context)


# Функция для обработки нажатия на кнопку "Добавить вариант"
async def add_variant(update: Update, context: CallbackContext):
    markup = ReplyKeyboardMarkup([['ОГЭ', 'ЕГЭ'], ['Вернуться в меню']], one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("Выберите экзамен для добавления варианта:", reply_markup=markup)
    return ADD_VARIANT


# Обработка выбора экзамена для добавления варианта
async def handle_variant_exam(update: Update, context: CallbackContext):
    if update.message.text == 'Вернуться в меню':
        return await return_to_menu(update, context)

    exam = update.message.text
    if exam not in ['ОГЭ', 'ЕГЭ']:
        await update.message.reply_text("Выберите действительный экзамен (ОГЭ или ЕГЭ).")
        return ADD_VARIANT

    context.user_data['variant_exam'] = exam
    await update.message.reply_text(f"Вы выбрали {exam}. Пришлите ссылку на вариант:")
    return ADD_VARIANT_LINK


async def handle_variant_link(update: Update, context: CallbackContext):
    link = update.message.text
    exam = context.user_data.get('variant_exam')

    if not exam:
        await update.message.reply_text("Произошла ошибка. Попробуйте снова.")
        return await return_to_menu(update, context)

    # Сохраняем или обновляем вариант в базе данных
    db_execute('''
        INSERT INTO variants (exam, link) 
        VALUES (?, ?)
        ON CONFLICT(exam) DO UPDATE SET link = excluded.link
    ''', (exam, link))

    # Уведомляем всех учеников, относящихся к этому экзамену
    with sqlite3.connect('your_database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT telegram_id FROM users WHERE exam = ?', (exam,))
        students = cursor.fetchall()

    for student in students:
        telegram_id = student[0]
        if telegram_id:
            try:
                keyboard = [[InlineKeyboardButton("Открыть вариант", url=link)]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await context.bot.send_message(
                    chat_id=telegram_id,
                    text=f"У вас обновился вариант экзамена ({exam}). Нажмите на кнопку ниже, чтобы открыть:",
                    reply_markup=reply_markup
                )
            except Exception as e:
                print(f"Не удалось уведомить ученика с ID {telegram_id}: {e}")

    await update.message.reply_text(f"Ссылка на вариант для {exam} успешно добавлена или обновлена!")
    return await return_to_menu(update, context)


# Функция для выбора поля
async def modify_student(update: Update, context: CallbackContext):
    students = get_all_users()
    if not students:
        await update.message.reply_text("Нет зарегистрированных учеников.")
        return await return_to_menu(update, context)

    # Создаём клавиатуру с учениками
    keyboard = [[InlineKeyboardButton(student[1], callback_data=f"edit_student:{student[0]}")] for student in students]
    keyboard.append([InlineKeyboardButton("Вернуться в меню", callback_data="return_to_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Выберите ученика для изменения данных или вернитесь в меню:",
                                    reply_markup=reply_markup)
    return None


async def handle_edit_student(update: Update, context: CallbackContext):
    query = update.callback_query
    student_id = int(query.data.split(":")[1])
    context.user_data['editing_student_id'] = student_id  # Сохраняем ID ученика

    # Получаем информацию об ученике
    student_info = get_student_info(student_id)
    if not student_info:
        await query.answer("Ошибка: ученик не найден.")
        return

    name = student_info["name"]
    exam = student_info["exam"]
    class_date = student_info["class_date"] or "Не указана"
    class_link = student_info["class_link"] or "Не указана"
    description = student_info["description"] or "Не указана"

    # Формируем сообщение с текущей информацией
    info_message = (
        f"Текущая информация об ученике:\n"
        f"Имя: {name}\n"
        f"Экзамен: {exam}\n"
        f"Дата занятия: {class_date}\n"
        f"Ссылка на занятие: {class_link}\n"
        f"Описание: {description}\n\n"
        f"Выберите, что вы хотите изменить:"
    )

    keyboard = [
        [InlineKeyboardButton("Имя", callback_data="edit_field:name")],
        [InlineKeyboardButton("Экзамен", callback_data="edit_field:exam")],
        [InlineKeyboardButton("Дата занятия", callback_data="edit_field:class_date")],
        [InlineKeyboardButton("Ссылка на занятие", callback_data="edit_field:class_link")],
        [InlineKeyboardButton("Добавить описание", callback_data="edit_field:description")],
        [InlineKeyboardButton("Вернуться в меню", callback_data="return_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(info_message, reply_markup=reply_markup)


# Обработка подтверждения изменений
async def handle_confirmation(update: Update, context: CallbackContext):
    confirmation = update.message.text
    student_id = context.user_data.get('editing_student_id')
    field = context.user_data.get('editing_field')
    new_value = context.user_data.get('new_value')

    if confirmation == "Да":
        try:
            with sqlite3.connect('your_database.db') as conn:
                cursor = conn.cursor()
                cursor.execute(f"UPDATE users SET {field} = ? WHERE id = ?", (new_value, student_id))
                conn.commit()
            await update.message.reply_text("Данные успешно обновлены!")
        except sqlite3.Error as e:
            await update.message.reply_text(f"Ошибка при обновлении базы данных: {e}")
    else:
        await update.message.reply_text("Изменение данных отменено.")

    context.user_data.clear()  # Сбрасываем состояние
    return await return_to_menu(update, context)


async def handle_delete_description(update: Update, context: CallbackContext):
    # Получаем ID ученика из контекста
    student_id = context.user_data.get('editing_student_id')
    if not student_id:
        await update.message.reply_text("Ошибка: ID ученика не найден.")
        return

    # Удаляем описание (устанавливаем NULL)
    update_student_field(student_id, "description", None)

    # Сообщаем пользователю об удалении описания
    await update.message.reply_text("Описание удалено. Вы возвращены в меню.")
    await return_to_menu(update, context)


async def show_student_info(update: Update, context: CallbackContext):
    students = get_all_users()  # Извлекаем всех учеников
    if not students:
        await update.message.reply_text("Нет зарегистрированных учеников.")
        return await return_to_menu(update, context)

    # Создаём Inline-клавиатуру для выбора ученика
    keyboard = [
        [
            InlineKeyboardButton(
                text=f"{student[1]}",  # Имя ученика
                callback_data=f"show_info:{student[0]}"  # ID ученика
            )
        ]
        for student in students
    ]
    keyboard.append([InlineKeyboardButton("Вернуться в меню", callback_data="return_to_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Выберите ученика для просмотра информации или вернитесь в меню:",
        reply_markup=reply_markup
    )


def add_homework(exam: str, title: str, link: str):
    """Добавление нового задания в таблицу assignments."""
    db_execute('INSERT INTO assignments (exam, title, link) VALUES (?, ?, ?)', (exam, title, link))

def get_homework_by_exam(exam: str):
    """Получение всех заданий для указанного экзамена."""
    return db_execute('SELECT id, title, link FROM assignments WHERE exam = ?', (exam,), fetchall=True)

def delete_homework(homework_id: int):
    """Удаление задания по его ID."""
    db_execute('DELETE FROM assignments WHERE id = ?', (homework_id,))


async def start_add_homework(update: Update, context: CallbackContext) -> int:
    """Точка входа: предлагаем выбрать экзамен."""
    keyboard = [
        [
            InlineKeyboardButton("ОГЭ", callback_data="OGE"),
            InlineKeyboardButton("ЕГЭ", callback_data="EGE")
        ],
        [
            InlineKeyboardButton("Отмена", callback_data="return_to_menu")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите экзамен для задания:", reply_markup=reply_markup)
    return ADD_EXAM


async def handle_add_exam(update: Update, context: CallbackContext) -> int:
    """Обработка выбора экзамена, переход к названию."""
    query = update.callback_query
    if query.data == "return_to_menu":
        # Завершаем второй диалог (текущий):
        await query.message.reply_text("Отменено. Возвращаемся в меню.")
        return ConversationHandler.END

    exam = query.data
    context.user_data["exam"] = exam
    await query.message.reply_text("Введите название задания:")
    return ADD_TITLE


async def handle_add_title(update: Update, context: CallbackContext) -> int:
    context.user_data["title"] = update.message.text
    await update.message.reply_text("Теперь отправьте ссылку на задание:")
    return ADD_LINK


async def handle_add_link(update: Update, context: CallbackContext) -> int:
    link = update.message.text
    exam = context.user_data.get("exam")
    title = context.user_data.get("title")

    # Допустим, тут мы что-то сохраняем в базу:
    # add_homework(exam, title, link)
    await update.message.reply_text(
        f"Задание добавлено!\n\nЭкзамен: {exam}\nНазвание: {title}\nСсылка: {link}\n"
        "Возвращаемся в меню..."
    )
    return ConversationHandler.END

async def start_give_homework(update: Update, context: CallbackContext) -> int:
    """Начало выдачи домашнего задания: выбор экзамена."""
    keyboard = [
        [InlineKeyboardButton("ОГЭ", callback_data="OGE"), InlineKeyboardButton("ЕГЭ", callback_data="EGE")],
        [InlineKeyboardButton("Отмена", callback_data="cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Выберите экзамен для задания:", reply_markup=reply_markup)
    return CHOOSE_HOMEWORK_EXAM

async def handle_homework_exam(update: Update, context: CallbackContext) -> int:
    """Обработка выбора экзамена."""
    query = update.callback_query
    await query.answer()

    if query.data == "cancel":
        return await return_to_menu(update, context)

    context.user_data["exam"] = query.data  # Сохраняем выбранный экзамен

    # Получаем список учеников, привязанных к выбранному экзамену
    students = get_all_users()
    if not students:
        await query.message.reply_text(f"Нет учеников для экзамена {query.data}.")
        return await return_to_menu(update, context)

    # Создаем кнопки для выбора ученика
    keyboard = [
        [InlineKeyboardButton(student[1], callback_data=f"student:{student[0]}")] for student in students
    ]
    keyboard.append([InlineKeyboardButton("Отмена", callback_data="cancel")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("Выберите ученика для задания:", reply_markup=reply_markup)
    return CHOOSE_HOMEWORK_STUDENT


async def handle_homework_student(update: Update, context: CallbackContext) -> int:
    """Обработка выбора ученика."""
    query = update.callback_query
    await query.answer()

    if query.data == "cancel":
        return await return_to_menu(update, context)

    student_id = int(query.data.split(":")[1])
    context.user_data["student_id"] = student_id  # Сохраняем ID ученика

    # Получаем список заданий для выбранного экзамена
    exam = context.user_data["exam"]
    assignments = get_homework_by_exam(exam)
    if not assignments:
        await query.message.reply_text(f"Нет заданий для экзамена {exam}.")
        return await return_to_menu(update, context)

    # Создаем кнопки для выбора задания
    keyboard = [
        [InlineKeyboardButton(assignment[1], callback_data=f"assignment:{assignment[0]}")] for assignment in assignments
    ]
    keyboard.append([InlineKeyboardButton("Отмена", callback_data="cancel")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("Выберите задание:", reply_markup=reply_markup)
    return CHOOSE_HOMEWORK_ASSIGNMENT

async def handle_homework_assignment(update: Update, context: CallbackContext) -> int:
    """Обработка выбора задания и сохранение его для ученика."""
    query = update.callback_query
    await query.answer()

    if query.data == "cancel":
        return await return_to_menu(update, context)

    assignment_id = int(query.data.split(":")[1])
    student_id = context.user_data["student_id"]

    # Сохраняем задание для ученика в базу данных
    assignment = get_assignment_by_id(assignment_id)
    save_homework_for_student(student_id, assignment_id)

    await query.message.reply_text(
        f"Задание '{assignment[1]}' успешно назначено ученику с ID {student_id}."
    )
    return await return_to_menu(update, context)


async def handle_show_homework(update: Update, context: CallbackContext):
    """Показ всех заданий для выбранного экзамена."""
    query = update.callback_query
    await query.answer()

    if query.data == "return_to_menu":
        return await return_to_menu(update, context)

    assignments = get_homework_by_exam(query.data)
    if not assignments:
        await query.message.reply_text("Нет заданий для выбранного экзамена.")
        return await return_to_menu(update, context)

    text = "\n".join([f"{hw[1]}: {hw[2]}" for hw in assignments])
    await query.message.reply_text(f"Задания для {query.data}:\n{text}")


async def start_delete_homework(update: Update, context: CallbackContext):
    """Показ экзаменов для удаления заданий."""
    keyboard = [
        [InlineKeyboardButton("ОГЭ", callback_data="OGE"), InlineKeyboardButton("ЕГЭ", callback_data="EGE")],
        [InlineKeyboardButton("Вернуться в меню", callback_data="return_to_menu")]
    ]
    await update.message.reply_text("Выберите экзамен для удаления заданий:", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_delete_homework(update: Update, context: CallbackContext):
    """Показ заданий для удаления."""
    query = update.callback_query
    await query.answer()

    if query.data == "return_to_menu":
        return await return_to_menu(update, context)

    assignments = get_homework_by_exam(query.data)
    if not assignments:
        await query.message.reply_text("Нет заданий для удаления.")
        return await return_to_menu(update, context)

    keyboard = [
        [InlineKeyboardButton(f"{hw[1]}", callback_data=f"delete:{hw[0]}")] for hw in assignments
    ]
    keyboard.append([InlineKeyboardButton("Вернуться в меню", callback_data="return_to_menu")])
    await query.message.reply_text("Выберите задание для удаления:", reply_markup=InlineKeyboardMarkup(keyboard))

async def confirm_delete_homework(update: Update, context: CallbackContext):
    """Подтверждение удаления задания."""
    query = update.callback_query
    await query.answer()

    if query.data.startswith("delete:"):
        homework_id = int(query.data.split(":")[1])
        delete_homework(homework_id)
        await query.message.reply_text("Задание удалено.")
        return await return_to_menu(update, context)



# Обновляем основной обработчик, добавляем CallbackQueryHandler
def main():
    create_tables()

    # Ваш токен для бота
    application = Application.builder().token(BOT_TOKEN).build()

    # Определение ConversationHandler
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [MessageHandler(filters.Regex(
                 "^(Добавить ученика|Удалить ученика|Выдать домашнее задание|Добавить вариант|Внести изменения|"
                 "Информация об ученике)$"),
                handle_choice)],
            TYPING_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_name)],
            TYPING_EXAM: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_exam_choice)],
            STUDENT_LOGIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, student_login)],
            STUDENT_MENU: [MessageHandler(
                    filters.Regex("^(Домашнее задание|Конспекты|Актуальный вариант|Подключиться к занятию)$"),
                    handle_student_menu)
            ],
            ADD_VARIANT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_variant_exam)],
            ADD_VARIANT_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_variant_link)],
            TYPING_CLASS_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_class_link)],
            TYPING_CLASS_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_class_date)],
        },
        fallbacks=[
            CommandHandler('start', return_to_menu)  # Возврат в главное меню
        ],
    )

    modify_user_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(handle_edit_student,  pattern=r"^edit_student:\d+$")],
        states={
                CHOOSING_FIELD: [CallbackQueryHandler(handle_edit_field,
                                                      pattern=r"^edit_field:(name|exam|class_date|class_link)$")],
                UPDATING_FIELD: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_new_value)],
                CONFIRMATION: [MessageHandler(filters.Regex("^(Да|Нет)$"), handle_confirmation)]
                },
        fallbacks=[
            CommandHandler('start', return_to_menu)
        ]
    )

    # Добавление основного ConversationHandler
    application.add_handler(conversation_handler)  # Основной обработчик
    application.add_handler(modify_user_handler)  # Изолированный обработчик

    # Обработчики для CallbackQuery
    application.add_handler(CallbackQueryHandler(handle_delete_callback, pattern=r"^delete_student:"))
    application.add_handler(CallbackQueryHandler(handle_select_student, pattern=r"^select_student:"))
    application.add_handler(CallbackQueryHandler(handle_assign_homework, pattern=r"^assign_homework:"))
    application.add_handler(CallbackQueryHandler(handle_delete_callback, pattern="^return_to_menu$"))
    application.add_handler(CallbackQueryHandler(handle_edit_student, pattern=r"^edit_student:\d+$"))
    application.add_handler(CallbackQueryHandler(handle_edit_field, pattern=r"^edit_field:.*"))
    application.add_handler(CallbackQueryHandler(handle_new_exam, pattern=r"^new_exam:.*"))
    application.add_handler(CallbackQueryHandler(handle_show_student_info, pattern=r"^show_info:\d+$"))
    application.add_handler(CallbackQueryHandler(return_to_student_menu, pattern="^return_to_menu$"))

    # Обработчики для работы с домашними заданиями
    add_homework_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("add_homework", start_add_homework)],
        states={
            ADD_EXAM: [CallbackQueryHandler(handle_add_exam, pattern=r"^(OGE|EGE|return_to_menu)$")],
            ADD_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_add_title)],
            ADD_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_add_link)],
        },
        fallbacks=[
            CommandHandler("start", return_to_menu),  # Если вдруг /start
            # Или любые другие fallback'и, если нужно
        ]
    )
    application.add_handler(add_homework_conv_handler)

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, global_message_handler))
    application.add_handler(MessageHandler(filters.Regex("^/start$"), start))

    # Запуск приложения
    application.run_polling()


if __name__ == '__main__':
    main()
