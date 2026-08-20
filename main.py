import os
import time
import telebot

from telebot.types import (
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    KeyboardButton
)

from requests_forwarder import setup_proxy
from text import Texts
from DML import (
    insert_user_data,
    insert_attendance,
    update_checkout,
    insert_project_data,
    insert_task
)
from DQL import (
    get_user_by_id,
    get_all_projects,
    get_tasks_for_user,
    get_tasks_for_project,
    get_today_attendance,
    get_open_attendance
)

setup_proxy(proxy_token="c1c0a803aa19b59423874442ed3c2bc02281b348e73888987d0feb65f3b79c0c")

API_TOKEN =  "8526797112:AAE0BPAPr3NLfvMd6T2K1GVCIkaEUWfxVHI"

os.makedirs('Data', exist_ok=True)

bot = telebot.TeleBot(API_TOKEN, num_threads=10)

admins = [1428033749]

user_steps = dict()
user_data = dict()
spam_data = dict()

hideboard = ReplyKeyboardRemove()

commands = {
    'start': 'start the bot',
    'menu': 'show main menu',
    'help': 'show help menu',
    'attendance': 'attendance section',
    'monthly_report': 'show monthly report',
    'today_report': 'show today report',
    'projects': 'show projects menu',
    'tasks': 'show tasks menu',
    'profile': 'show profile menu',
    'support': 'send message to support',
    'req_contact': 'request user contact',
    'checkin': 'register check in',
    'checkout': 'register check out',
}

admin_commands = {
    'admin_panel': 'show admin panel',
}

profiles = dict()


def is_spam(cid) -> bool:
    lower_bound = 0.7
    upper_bound = 4.0
    max_score = 5

    now = time.time()

    if cid not in spam_data:
        spam_data[cid] = {
            'last_message_time': now,
            'score': 0
        }
        return False

    last_time = spam_data[cid]['last_message_time']
    score = spam_data[cid]['score']
    delta = now - last_time

    if delta < lower_bound:
        score += 2
    elif delta > upper_bound:
        score -= 1

    if score < 0:
        score = 0

    spam_data[cid]['last_message_time'] = now
    spam_data[cid]['score'] = score

    if score >= max_score:
        return True
    return False


def send_message(*args, **kwargs):
    try:
        return bot.send_message(*args, **kwargs)
    except:
        pass


def get_user_lang(cid):
    return 'fa'


def get_text(cid, key):
    lang = get_user_lang(cid)
    return Texts[lang][key]


def ensure_user_profile(cid):
    if cid not in profiles:
        db_user = get_user_by_id(cid)
        if db_user:
            profiles[cid] = {
                'name': db_user.get('FIRST_NAME') or '-',
                'lname': db_user.get('LAST_NAME') or '-',
                'job': '-',
                'age': '-',
                'dept': '-',
                'shift': '-',
            }
        else:
            profiles[cid] = {
                'name': '-',
                'lname': '-',
                'job': '-',
                'age': '-',
                'dept': '-',
                'shift': '-',
            }


def register_user_if_needed(message):
    cid = message.chat.id
    first_name = message.from_user.first_name or '-'
    last_name = message.from_user.last_name
    username = message.from_user.username

    user = get_user_by_id(cid)
    if not user:
        try:
            insert_user_data(
                cid=cid,
                first_name=first_name,
                last_name=last_name,
                username=username
            )
        except:
            pass


def get_main_menu(cid):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add(
        get_text(cid, 'attendance_btn'),
        get_text(cid, 'monthly_report_btn')
    )
    keyboard.add(
        get_text(cid, 'projects_btn'),
        get_text(cid, 'tasks_btn')
    )
    keyboard.add(
        get_text(cid, 'profile_btn'),
        get_text(cid, 'today_report_btn')
    )
    return keyboard


def get_inline_back(cid):
    return InlineKeyboardButton(
        get_text(cid, 'back_to_main'),
        callback_data='main_menu'
    )


def get_projects_inline(cid):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton(get_text(cid, 'my_projects_btn'), callback_data='my_projects'),
        InlineKeyboardButton(get_text(cid, 'total_progress_btn'), callback_data='total_progress'),
        InlineKeyboardButton(get_text(cid, 'team_info_btn'), callback_data='team_info'),
        get_inline_back(cid)
    )
    return markup


def get_tasks_inline(cid):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton(get_text(cid, 'task_progress_btn'), callback_data='task_progress'),
        InlineKeyboardButton(get_text(cid, 'task_info_btn'), callback_data='task_info'),
        InlineKeyboardButton(get_text(cid, 'task_status_btn'), callback_data='task_status'),
        InlineKeyboardButton(get_text(cid, 'task_percent_btn'), callback_data='task_percent'),
        InlineKeyboardButton(get_text(cid, 'task_deadline_btn'), callback_data='task_deadline'),
        get_inline_back(cid)
    )
    return markup


def get_profile_inline(cid):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(get_text(cid, 'p_name_btn'), callback_data='p_name'),
        InlineKeyboardButton(get_text(cid, 'p_lname_btn'), callback_data='p_lname'),
        InlineKeyboardButton(get_text(cid, 'p_job_btn'), callback_data='p_job'),
        InlineKeyboardButton(get_text(cid, 'p_age_btn'), callback_data='p_age'),
        InlineKeyboardButton(get_text(cid, 'p_dept_btn'), callback_data='p_dept'),
        InlineKeyboardButton(get_text(cid, 'p_shift_btn'), callback_data='p_shift'),
        get_inline_back(cid)
    )
    return markup


def get_attendance_inline(cid):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton(get_text(cid, 'clock_in_btn'), callback_data='clock_in'),
        InlineKeyboardButton(get_text(cid, 'clock_out_btn'), callback_data='clock_out'),
        InlineKeyboardButton(get_text(cid, 'attendance_status_btn'), callback_data='attendance_status'),
        get_inline_back(cid)
    )
    return markup


def profile_text(cid):
    ensure_user_profile(cid)
    p = profiles[cid]
    return (
        f"{get_text(cid, 'profile_title')}\n\n"
        f"{get_text(cid, 'name_label')}: {p['name']}\n"
        f"{get_text(cid, 'lname_label')}: {p['lname']}\n"
        f"{get_text(cid, 'job_label')}: {p['job']}\n"
        f"{get_text(cid, 'age_label')}: {p['age']}\n"
        f"{get_text(cid, 'dept_label')}: {p['dept']}\n"
        f"{get_text(cid, 'shift_label')}: {p['shift']}"
    )


def projects_text():
    rows = get_all_projects()
    if not rows:
        return "📁 هنوز پروژه‌ای ثبت نشده است."

    text = "📁 لیست پروژه‌ها:\n\n"
    for project in rows:
        text += f"{project['ID']}. {project['NAME']} - {project['STATUS']}\n"
    return text


def projects_total_progress():
    rows = get_all_projects()
    if not rows:
        return "اطلاعاتی وجود ندارد."
    return f"📊 تعداد کل پروژه‌ها: {len(rows)}"


def projects_team_info():
    rows = get_all_projects()
    if not rows:
        return "👥 اطلاعاتی برای تیم پروژه‌ها وجود ندارد."

    text = "👥 اطلاعات پروژه‌ها:\n\n"
    for project in rows:
        text += (
            f"📁 {project['NAME']}\n"
            f"وضعیت: {project['STATUS']}\n"
            f"ددلاین: {project['DEADLINE']}\n\n"
        )
    return text


def tasks_progress_text(cid):
    rows = get_tasks_for_user(cid)
    if not rows:
        return "📈 هنوز تسکی برای شما ثبت نشده است."

    text = "📈 درصد پیشرفت تسک‌ها:\n\n"
    for task in rows:
        text += f"{task['ID']}. {task['TITLE']}: {task['PROGRESS']}٪\n"
    return text


def tasks_info_text(cid):
    rows = get_tasks_for_user(cid)
    if not rows:
        return "📄 هنوز تسکی برای شما ثبت نشده است."

    text = "📄 اطلاعات تسک‌ها:\n\n"
    for task in rows:
        text += (
            f"{task['ID']}. {task['TITLE']}\n"
            f"   توضیح: {task['DESCRIPTION']}\n"
            f"   وضعیت: {task['STATUS']}\n\n"
        )
    return text


def tasks_status_text(cid):
    rows = get_tasks_for_user(cid)
    if not rows:
        return "🔄 هنوز تسکی برای شما ثبت نشده است."

    text = "🔄 وضعیت تسک‌ها:\n\n"
    for task in rows:
        text += f"{task['ID']}. {task['TITLE']}: {task['STATUS']}\n"
    return text


def tasks_deadline_text(cid):
    rows = get_tasks_for_user(cid)
    if not rows:
        return "📅 هنوز تسکی برای شما ثبت نشده است."

    text = "📅 ددلاین تسک‌ها:\n\n"
    for task in rows:
        text += f"{task['ID']}. {task['TITLE']}: {task['DEADLINE']}\n"
    return text


def attendance_status_text(cid):
    row = get_open_attendance(cid)
    today_rows = get_today_attendance(cid)

    clock_in = 'ثبت نشده'
    clock_out = 'ثبت نشده'

    if today_rows:
        latest = today_rows[0]
        if latest.get('CHECKIN_TIME'):
            clock_in = str(latest.get('CHECKIN_TIME'))
        if latest.get('CHECKOUT_TIME'):
            clock_out = str(latest.get('CHECKOUT_TIME'))

    if row and row.get('CHECKIN_TIME'):
        clock_in = str(row.get('CHECKIN_TIME'))

    return (
        "🕒 وضعیت حضور و غیاب:\n\n"
        f"ورود امروز: {clock_in}\n"
        f"خروج امروز: {clock_out}\n"
    )


def listener(messages):
    for m in messages:
        try:
            if m.content_type == 'text':
                print(f'{m.chat.id} -> {m.text}')
            elif m.content_type == 'contact':
                print(f'{m.chat.id} -> contact')
            elif m.content_type == 'location':
                print(f'{m.chat.id} -> location')
            else:
                print(f'{m.chat.id} -> {m.content_type}')
        except:
            pass


bot.set_update_listener(listener)


@bot.callback_query_handler(func=lambda call: True)
def callback_query_handler_method(call):
    cid = call.message.chat.id
    mid = call.message.message_id
    data = call.data

    if is_spam(cid):
        bot.answer_callback_query(call.id, "لطفاً با فاصله پیام بفرستید.")
        return

    print(cid, 'callback ->', data)

    if data == 'main_menu':
        try:
            bot.delete_message(cid, mid)
        except:
            pass
        send_message(
            cid,
            get_text(cid, 'back_main_text'),
            reply_markup=get_main_menu(cid)
        )

    elif data == 'my_projects':
        bot.answer_callback_query(call.id, "پروژه‌ها بارگذاری شد.")
        bot.edit_message_text(
            projects_text(),
            cid,
            mid,
            reply_markup=get_projects_inline(cid)
        )

    elif data == 'total_progress':
        bot.answer_callback_query(call.id, "خلاصه پروژه‌ها نمایش داده شد.")
        bot.edit_message_text(
            projects_total_progress(),
            cid,
            mid,
            reply_markup=get_projects_inline(cid)
        )

    elif data == 'team_info':
        bot.answer_callback_query(call.id, "اطلاعات پروژه‌ها نمایش داده شد.")
        bot.edit_message_text(
            projects_team_info(),
            cid,
            mid,
            reply_markup=get_projects_inline(cid)
        )

    elif data == 'task_progress':
        bot.answer_callback_query(call.id, "پیشرفت تسک‌ها نمایش داده شد.")
        bot.edit_message_text(
            tasks_progress_text(cid),
            cid,
            mid,
            reply_markup=get_tasks_inline(cid)
        )

    elif data == 'task_info':
        bot.answer_callback_query(call.id, "اطلاعات تسک‌ها نمایش داده شد.")
        bot.edit_message_text(
            tasks_info_text(cid),
            cid,
            mid,
            reply_markup=get_tasks_inline(cid)
        )

    elif data == 'task_status':
        bot.answer_callback_query(call.id, "وضعیت تسک‌ها نمایش داده شد.")
        bot.edit_message_text(
            tasks_status_text(cid),
            cid,
            mid,
            reply_markup=get_tasks_inline(cid)
        )

    elif data == 'task_percent':
        bot.answer_callback_query(call.id, "درصد انجام تسک‌ها نمایش داده شد.")
        bot.edit_message_text(
            tasks_progress_text(cid),
            cid,
            mid,
            reply_markup=get_tasks_inline(cid)
        )

    elif data == 'task_deadline':
        bot.answer_callback_query(call.id, "ددلاین‌ها نمایش داده شد.")
        bot.edit_message_text(
            tasks_deadline_text(cid),
            cid,
            mid,
            reply_markup=get_tasks_inline(cid)
        )

    elif data == 'clock_in':
        today = time.strftime('%Y-%m-%d %H:%M:%S')
        work_date = time.strftime('%Y-%m-%d')

        open_row = get_open_attendance(cid)
        if open_row:
            bot.answer_callback_query(call.id, "برای امروز قبلاً ورود ثبت شده است.")
            bot.edit_message_text(
                attendance_status_text(cid),
                cid,
                mid,
                reply_markup=get_attendance_inline(cid)
            )
            return

        try:
            insert_attendance(cid, today, work_date)
            bot.answer_callback_query(call.id, "ورود ثبت شد.")
            bot.edit_message_text(
                f"✅ ورود شما ثبت شد.\n\n{attendance_status_text(cid)}",
                cid,
                mid,
                reply_markup=get_attendance_inline(cid)
            )
        except:
            bot.answer_callback_query(call.id, "خطا در ثبت ورود.")

    elif data == 'clock_out':
        work_date = time.strftime('%Y-%m-%d')
        now = time.strftime('%Y-%m-%d %H:%M:%S')

        open_row = get_open_attendance(cid)
        if not open_row:
            bot.answer_callback_query(call.id, "ورود بازی برای امروز پیدا نشد.")
            bot.edit_message_text(
                attendance_status_text(cid),
                cid,
                mid,
                reply_markup=get_attendance_inline(cid)
            )
            return

        try:
            update_checkout(cid, work_date, now)
            bot.answer_callback_query(call.id, "خروج ثبت شد.")
            bot.edit_message_text(
                f"✅ خروج شما ثبت شد.\n\n{attendance_status_text(cid)}",
                cid,
                mid,
                reply_markup=get_attendance_inline(cid)
            )
        except:
            bot.answer_callback_query(call.id, "خطا در ثبت خروج.")

    elif data == 'attendance_status':
        bot.answer_callback_query(call.id, "وضعیت حضور و غیاب نمایش داده شد.")
        bot.edit_message_text(
            attendance_status_text(cid),
            cid,
            mid,
            reply_markup=get_attendance_inline(cid)
        )

    elif data.startswith('p_'):
        ensure_user_profile(cid)

        if data == 'p_name':
            user_steps[cid] = 'profile_name'
            send_message(cid, get_text(cid, 'ask_name'))

        elif data == 'p_lname':
            user_steps[cid] = 'profile_lname'
            send_message(cid, get_text(cid, 'ask_lname'))

        elif data == 'p_job':
            user_steps[cid] = 'profile_job'
            send_message(cid, get_text(cid, 'ask_job'))

        elif data == 'p_age':
            user_steps[cid] = 'profile_age'
            send_message(cid, get_text(cid, 'ask_age'))

        elif data == 'p_dept':
            user_steps[cid] = 'profile_dept'
            send_message(cid, get_text(cid, 'ask_dept'))

        elif data == 'p_shift':
            user_steps[cid] = 'profile_shift'
            send_message(cid, get_text(cid, 'ask_shift'))

        bot.answer_callback_query(call.id, "فیلد پروفایل انتخاب شد.")

    else:
        bot.answer_callback_query(call.id, "این بخش به زودی فعال می‌شود.")


@bot.message_handler(commands=['start', 'menu'])
def send_welcome(message):
    cid = message.chat.id

    register_user_if_needed(message)

    if is_spam(cid):
        return

    send_message(
        cid,
        get_text(cid, 'welcome'),
        reply_markup=get_main_menu(cid)
    )


@bot.message_handler(commands=['help'])
def command_help_handler(message):
    cid = message.chat.id
    if is_spam(cid):
        return

    text = "Commands:\n\n"
    for command in commands:
        text += f'/{command}: {commands[command]}\n'

    if cid in admins:
        text += '\nAdmin Commands:\n\n'
        for command in admin_commands:
            text += f'/{command}: {admin_commands[command]}\n'

    send_message(cid, text)


@bot.message_handler(commands=['attendance'])
def command_attendance_handler(message):
    cid = message.chat.id
    if is_spam(cid):
        return

    send_message(
        cid,
        get_text(cid, 'attendance_title'),
        reply_markup=get_attendance_inline(cid)
    )


@bot.message_handler(commands=['monthly_report'])
def command_monthly_report_handler(message):
    cid = message.chat.id
    if is_spam(cid):
        return

    send_message(cid, get_text(cid, 'monthly_report_text'))


@bot.message_handler(commands=['today_report'])
def command_today_report_handler(message):
    cid = message.chat.id
    if is_spam(cid):
        return

    rows = get_today_attendance(cid)
    if not rows:
        send_message(cid, "امروز هنوز هیچ رکورد حضوری ثبت نشده است.")
        return

    latest = rows[0]
    text = (
        "📅 گزارش امروز\n\n"
        f"ورود: {latest.get('CHECKIN_TIME') or 'ثبت نشده'}\n"
        f"خروج: {latest.get('CHECKOUT_TIME') or 'ثبت نشده'}"
    )
    send_message(cid, text)


@bot.message_handler(commands=['projects'])
def command_projects_handler(message):
    cid = message.chat.id
    if is_spam(cid):
        return

    send_message(
        cid,
        get_text(cid, 'projects_title'),
        reply_markup=get_projects_inline(cid)
    )


@bot.message_handler(commands=['tasks'])
def command_tasks_handler(message):
    cid = message.chat.id
    if is_spam(cid):
        return

    send_message(
        cid,
        get_text(cid, 'tasks_title'),
        reply_markup=get_tasks_inline(cid)
    )


@bot.message_handler(commands=['profile'])
def command_profile_handler(message):
    cid = message.chat.id
    if is_spam(cid):
        return

    ensure_user_profile(cid)
    send_message(
        cid,
        profile_text(cid),
        reply_markup=get_profile_inline(cid)
    )


@bot.message_handler(commands=['support'])
def command_support_handler(message):
    cid = message.chat.id
    if is_spam(cid):
        return

    user_steps[cid] = 'support'
    send_message(cid, get_text(cid, 'support_text'))


@bot.message_handler(commands=['req_contact'])
def command_req_contact_handler(message):
    cid = message.chat.id
    if is_spam(cid):
        return

    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(
        KeyboardButton(get_text(cid, 'send_contact_btn'), request_contact=True)
    )
    send_message(cid, get_text(cid, 'req_contact_text'), reply_markup=markup)


@bot.message_handler(commands=['checkin'])
def command_checkin_handler(message):
    cid = message.chat.id
    if is_spam(cid):
        return

    work_date = time.strftime('%Y-%m-%d')
    checkin_time = time.strftime('%Y-%m-%d %H:%M:%S')

    if get_open_attendance(cid):
        send_message(cid, "برای امروز قبلاً ورود ثبت شده است.")
        return

    try:
        insert_attendance(cid, checkin_time, work_date)
        send_message(cid, "✅ ورود شما با موفقیت ثبت شد.")
    except:
        send_message(cid, "❌ خطا در ثبت ورود.")


@bot.message_handler(commands=['checkout'])
def command_checkout_handler(message):
    cid = message.chat.id
    if is_spam(cid):
        return

    work_date = time.strftime('%Y-%m-%d')
    checkout_time = time.strftime('%Y-%m-%d %H:%M:%S')

    if not get_open_attendance(cid):
        send_message(cid, "برای امروز ورودی بازی پیدا نشد.")
        return

    try:
        update_checkout(cid, work_date, checkout_time)
        send_message(cid, "✅ خروج شما با موفقیت ثبت شد.")
    except:
        send_message(cid, "❌ خطا در ثبت خروج.")


@bot.message_handler(commands=['admin_panel'])
def command_admin_panel_handler(message):
    cid = message.chat.id
    if is_spam(cid):
        return

    if cid not in admins:
        return echo_message(message)

    send_message(cid, "پنل ادمین فعال شد.")


@bot.message_handler(func=lambda m: user_steps.get(m.chat.id) == 'support')
def handle_support_messages_step(message):
    cid = message.chat.id
    text = message.text

    send_message(cid, "✅ پیام شما برای پشتیبانی ثبت شد.")
    print('SUPPORT MESSAGE:', cid, text)

    user_steps.pop(cid,None)


@bot.message_handler(func=lambda m: user_steps.get(m.chat.id) == 'profile_name')
def profile_name_handler(message):
    cid = message.chat.id
    ensure_user_profile(cid)
    profiles[cid]['name'] = message.text
    user_steps.pop(cid, None)
    send_message(cid, profile_text(cid), reply_markup=get_profile_inline(cid))


@bot.message_handler(func=lambda m: user_steps.get(m.chat.id) == 'profile_lname')
def profile_lname_handler(message):
    cid = message.chat.id
    ensure_user_profile(cid)
    profiles[cid]['lname'] = message.text
    user_steps.pop(cid, None)
    send_message(cid, profile_text(cid), reply_markup=get_profile_inline(cid))


@bot.message_handler(func=lambda m: user_steps.get(m.chat.id) == 'profile_job')
def profile_job_handler(message):
    cid = message.chat.id
    ensure_user_profile(cid)
    profiles[cid]['job'] = message.text
    user_steps.pop(cid, None)
    send_message(cid, profile_text(cid), reply_markup=get_profile_inline(cid))


@bot.message_handler(func=lambda m: user_steps.get(m.chat.id) == 'profile_age')
def profile_age_handler(message):
    cid = message.chat.id
    ensure_user_profile(cid)
    profiles[cid]['age'] = message.text
    user_steps.pop(cid, None)
    send_message(cid, profile_text(cid), reply_markup=get_profile_inline(cid))


@bot.message_handler(func=lambda m: user_steps.get(m.chat.id) == 'profile_dept')
def profile_dept_handler(message):
    cid = message.chat.id
    ensure_user_profile(cid)
    profiles[cid]['dept'] = message.text
    user_steps.pop(cid, None)
    send_message(cid, profile_text(cid), reply_markup=get_profile_inline(cid))


@bot.message_handler(func=lambda m: user_steps.get(m.chat.id) == 'profile_shift')
def profile_shift_handler(message):
    cid = message.chat.id
    ensure_user_profile(cid)
    profiles[cid]['shift'] = message.text
    user_steps.pop(cid, None)
    send_message(cid, profile_text(cid), reply_markup=get_profile_inline(cid))


@bot.message_handler(func=lambda m: True)
def main_menu_logic(message):
    cid = message.chat.id
    text = message.text

    if is_spam(cid):
        return

    if text == get_text(cid, 'attendance_btn'):
        send_message(
            cid,
            get_text(cid, 'attendance_title'),
            reply_markup=get_attendance_inline(cid)
        )

    elif text == get_text(cid, 'monthly_report_btn'):
        send_message(cid, get_text(cid, 'monthly_report_text'))

    elif text == get_text(cid, 'projects_btn'):
        send_message(
            cid,
            get_text(cid, 'projects_title'),
            reply_markup=get_projects_inline(cid)
        )

    elif text == get_text(cid, 'tasks_btn'):
        send_message(
            cid,
            get_text(cid, 'tasks_title'),
            reply_markup=get_tasks_inline(cid)
        )

    elif text == get_text(cid, 'profile_btn'):
        ensure_user_profile(cid)
        send_message(
            cid,
            profile_text(cid),
            reply_markup=get_profile_inline(cid)
        )

    elif text == get_text(cid, 'today_report_btn'):
        rows = get_today_attendance(cid)
        if not rows:
            send_message(cid, "امروز هنوز هیچ رکورد حضوری ثبت نشده است.")
            return

        latest = rows[0]
        msg = (
            "📅 گزارش امروز\n\n"
            f"ورود: {latest.get('CHECKIN_TIME') or 'ثبت نشده'}\n"
            f"خروج: {latest.get('CHECKOUT_TIME') or 'ثبت نشده'}"
        )
        send_message(cid, msg)

    else:
        echo_message(message)


@bot.message_handler(content_types=['contact'])
def content_contact_handler(message):
    cid = message.chat.id
    contact = message.contact

    if contact.user_id == cid:
        send_message(
            cid,
            f"✅ شماره شما دریافت شد: {contact.phone_number}",
            reply_markup=hideboard
        )
    else:
        send_message(
            cid,
            "❌ لطفاً شماره خودتان را ارسال کنید.",
            reply_markup=hideboard
        )


@bot.message_handler(content_types=['location'])
def content_location_handler(message):
    cid = message.chat.id
    print(cid, message.location)


def echo_message(message):
    if message.text:
        bot.reply_to(message, message.text)


bot.infinity_polling()