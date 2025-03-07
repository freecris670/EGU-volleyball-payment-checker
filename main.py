from src.payment_checker import EventParser
from src.excluded_players import EXCLUDED_PLAYERS
import tkinter as tk
from tkinter import filedialog
from collections import defaultdict
from openpyxl import Workbook
from openpyxl.worksheet.datavalidation import DataValidation
import os
import sys
import re

# Словарь для персонализированных обращений
name_mappings = {
    "Maxim Зinovyev": "Макс",
    "Konstantin Podlesnyi": "Костя", 
    "Anya Vilkova": "Аня",
    "Kirill Kriukov": "Кирилл",
    "Ilya Kolomiytsev": "Илья",
    "Anna Kersilova": "Аня",
    "Kniazev Sergei": "Сергей",
    "Fedor Udalov": "Федя",
    "Sergey Konstantinov": "Сергей",
    "Ashot Gevorgyan": "Ашот",
    "Dmitry Kuznetsov": "Дмитрий",
    "Антирепрессант": "Араик",
    "Артем А": "Артем",
    "N": "Никита красивый",
    "Polina Matveeva": "Полина",
    "Daria Goltsova": "Дарья",
    "Viacheslav": "Слава",
    "Svetlana": "Светлана",
    "Valeriy": "Валерий",
    "Nikita Shabalin": "Никита",
    "Alice Koshechkina": "Алиса",
    "Matvey": "Матвей",
    "Ruslan": "Руслан",
    "Anatoliy Kudrin": "Толя",
    "Ivan": "Ваня",
    "Andrey Beloborodov": "Андрей",
    "Vanya": "Ваня",
    "Sergey Tkachuk": "Сергей",
    "Jek": "Женя",
    "Stas Maltsev": "Стас",
    "Noro Stambolyan": "Норо",
    "Narek Sargsyan": "Нарек",
    "Natali": "Натали",
    "Արարատ Մարտիրոսյան": "Арарат",
    "Artur Hovakanyan": "Артур",
    "Edgar": "Эдгар",
    "Greg": "Гриша",
    "Leonid": "Лёня",
    "Davo Abrahamyan": "Даво",
    "Dronte": "Андрей",
    "Lev Nikolsky": "Лев",
    "Vladimir": "Владимир",
    "Ivan Smirnov": "Иван",
    "Kristina Demirtshyan": "Кристина",
    "Ivan Nikolaev": "Ваня",
    # Добавьте другие соответствия имён по необходимости
}

def create_personal_message(name, dates):
    """Создание персонализированного сообщения"""
    # Получаем базовое имя без [2], [3] и т.д.
    base_name = re.sub(r'\s*\[\d+\]$', '', name)
    
    # Получаем персональное обращение или используем полное имя
    personal_name = name_mappings.get(base_name, base_name.split()[0])
    
    # Проверяем, есть ли игры с несколькими голосами
    multiple_votes_dates = []
    formatted_dates = []
    
    for date_info in dates:
        parts = date_info.split(' | ')
        date_display = parts[0]  # дата с днем недели
        votes = int(parts[-1]) if len(parts) > 2 else 1
        
        formatted_dates.append(date_display)
        
        if votes > 1:
            multiple_votes_dates.append((date_display, votes))
    
    # Форматируем даты для основного сообщения
    if len(formatted_dates) == 1:
        date_str = f"за игру в {formatted_dates[0]}"
    else:
        date_str = f"за игры в {', '.join(formatted_dates[:-1])} и {formatted_dates[-1]}"
    
    # Основное сообщение
    message = f"{personal_name}, привет!\n\nПодскажи, {date_str} картой оплачивал или наличкой?"
    
    # Если есть игры с несколькими голосами, добавляем дополнительный вопрос
    if multiple_votes_dates:
        multiple_votes_message = "\n\nКстати, заметил, что у тебя "
        
        if len(multiple_votes_dates) == 1:
            date, votes = multiple_votes_dates[0]
            multiple_votes_message += f"на игру в {date} поставлено {votes} голоса."
        else:
            vote_descriptions = []
            for date, votes in multiple_votes_dates:
                vote_descriptions.append(f"на игру в {date} - {votes} голоса")
            multiple_votes_message += f"есть несколько голосов: {', '.join(vote_descriptions)}."
        
        multiple_votes_message += " Подскажи, у них тоже всё оплачено?"
        message += multiple_votes_message
    
    return message

def group_by_player(results):
    """Группировка дат игр по игрокам, учитывая разные игры в один день"""
    player_dates = defaultdict(list)
    
    # Структура для определения уникальных игр и подсчета голосов
    # формат: {(дата, время, имя): счетчик_голосов}
    vote_tracking = {}
    
    for result in results:
        # Разбираем результат, который теперь включает и время игры
        parts = result.split(' | ')
        if len(parts) >= 2:
            date_info = parts[0]  # дата и день недели
            event_time = parts[1]  # время игры
            full_name = ' '.join(parts[2:])  # имя игрока
            
            date_parts = date_info.split()
            date = date_parts[1] if len(date_parts) > 1 else date_parts[0]
            weekday = date_parts[0] if len(date_parts) > 1 else ""
            
            # Формируем уникальный ключ для игры и игрока
            event_player_key = (date, event_time, full_name)
            
            # Пропускаем исключённых игроков
            base_name = re.sub(r'\s*\[\d+\]$', '', full_name)
            
            if base_name not in EXCLUDED_PLAYERS:
                # Формируем отображаемую дату с временем
                display_date = f"{weekday} {date} | {event_time}"
                
                # Учитываем количество голосов
                if event_player_key in vote_tracking:
                    vote_tracking[event_player_key] += 1
                else:
                    vote_tracking[event_player_key] = 1
                    # Добавляем дату только при первом обнаружении
                    player_dates[full_name].append(display_date)
    
    # Обогащаем информацию о датах количеством голосов
    # Создаем новую структуру данных с информацией о голосах
    enriched_player_dates = {}
    for player, dates in player_dates.items():
        enriched_dates = []
        for date in dates:
            date_parts = date.split(' | ')
            date_info = date_parts[0]
            date_parts_split = date_info.split()
            date_only = date_parts_split[1] if len(date_parts_split) > 1 else date_parts_split[0]
            event_time = date_parts[1] if len(date_parts) > 1 else ""
            
            event_player_key = (date_only, event_time, player)
            votes = vote_tracking.get(event_player_key, 1)
            
            # Формат: "дата | время | количество_голосов"
            enriched_date = f"{date} | {votes}"
            enriched_dates.append(enriched_date)
            
        enriched_player_dates[player] = enriched_dates
    
    return enriched_player_dates

def create_excel_report(player_dates):
    """Создание Excel-отчета с результатами"""
    wb = Workbook()
    
    # Создаем первую вкладку с оплатами
    ws_payments = wb.active
    ws_payments.title = "Оплаты"

    # Заголовки столбцов
    headers = ["Дата", "Время", "Имя", "Реальное имя", "Голоса", "Вид оплаты", "Статус"]
    for col, header in enumerate(headers, 1):
        ws_payments.cell(row=1, column=col, value=header)

    # Создаем выпадающие списки
    payment_type_dv = DataValidation(
        type="list",
        formula1='"картой,наличкой"',
        allow_blank=True
    )
    
    status_dv = DataValidation(
        type="list",
        formula1='"Запрос оплаты,Оплачено,Отсутствовал"',
        allow_blank=True
    )

    ws_payments.add_data_validation(payment_type_dv)
    ws_payments.add_data_validation(status_dv)

    # Словарь для отслеживания общего количества голосов на каждую игру
    event_total_votes = {}

    # Собираем данные для сортировки
    payment_data = []
    for player, dates in player_dates.items():
        # Получаем базовое имя без [2], [3] и т.д.
        base_name = re.sub(r'\s*\[\d+\]$', '', player)
        
        # Получаем персональное обращение или используем полное имя
        personal_name = name_mappings.get(base_name, base_name.split()[0])
        
        for date_info in dates:
            # Разделяем дату и время
            parts = date_info.split(' | ')
            display_date = parts[0]
            event_time = parts[1] if len(parts) > 1 else ""
            votes = int(parts[-1]) if len(parts) > 2 else 1
            
            # Разбиваем дату на части для сортировки
            day_month = display_date.split()[-1]  # получаем только "DD.MM"
            day, month = day_month.split('.')
            
            # Формируем дату для сортировки (месяц.день)
            sort_date = f"{month}.{day}"
            
            # Ключ для отслеживания уникальной игры для данного игрока
            event_key = (display_date, event_time, player)
            
            # Сохраняем информацию о количестве голосов
            event_total_votes[event_key] = votes
            
            # Создаем отдельную запись для КАЖДОГО голоса
            for vote_index in range(votes):
                payment_data.append({
                    'sort_date': sort_date,
                    'display_date': display_date,
                    'event_time': event_time,
                    'player': player,
                    'personal_name': personal_name,
                    'votes': votes,  # Общее количество голосов этого игрока в этой игре
                    'event_key': event_key  # Уникальный ключ события для этого игрока
                })
    
    # Сортируем данные по дате
    payment_data.sort(key=lambda x: (int(x['sort_date'].split('.')[0]), int(x['sort_date'].split('.')[1])))
    
    # Заполняем данные на первой вкладке в отсортированном порядке
    row = 2
    for entry in payment_data:
        ws_payments.cell(row=row, column=1, value=entry['display_date'])
        ws_payments.cell(row=row, column=2, value=entry['event_time'])
        ws_payments.cell(row=row, column=3, value=entry['player'])  # Оригинальное имя
        ws_payments.cell(row=row, column=4, value=entry['personal_name'])  # Персонализированное имя
        ws_payments.cell(row=row, column=5, value=entry['votes'])  # Общее количество голосов
        
        # Применяем валидацию к ячейкам
        payment_type_dv.add(f'F{row}')
        status_dv.add(f'G{row}')
        
        row += 1

    # Автоматическая настройка ширины столбцов
    for column in ws_payments.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2)
        ws_payments.column_dimensions[column_letter].width = adjusted_width

    # Создаем вторую вкладку с личными сообщениями
    ws_messages = wb.create_sheet(title="Личные сообщения")
    ws_messages.column_dimensions['A'].width = 30
    ws_messages.column_dimensions['B'].width = 70

    # Заголовки для личных сообщений
    ws_messages.cell(row=1, column=1, value="Имя")
    ws_messages.cell(row=1, column=2, value="Сообщение")

    # Заполняем личные сообщения
    row = 2
    for player, dates in player_dates.items():
        message = create_personal_message(player, dates)
        ws_messages.cell(row=row, column=1, value=player)
        ws_messages.cell(row=row, column=2, value=message)
        row += 1

    # Изменяем логику сохранения файла
    try:
        # Получаем путь к директории, где находится исполняемый файл
        if getattr(sys, 'frozen', False):
            # Если это скомпилированный exe
            application_path = os.path.dirname(sys.executable)
        else:
            # Если это python скрипт
            application_path = os.path.dirname(os.path.abspath(__file__))
            
        # Создаем директорию для отчетов, если её нет
        reports_dir = os.path.join(application_path, 'reports')
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)
            
        # Предлагаем сохранить файл
        file_path = filedialog.asksaveasfilename(
            initialdir=reports_dir,
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            title="Сохранить отчет как..."
        )
        
        if file_path:
            wb.save(file_path)
            print(f"\nОтчет сохранен в файл: {file_path}")
        else:
            print("\nСохранение отчета отменено")
            
    except Exception as e:
        print(f"\nОшибка при сохранении файла: {e}")

def main():
    # Создаём корневое окно и сразу скрываем его
    root = tk.Tk()
    root.withdraw()

    # Открываем диалоговое окно выбора файла
    print("Выберите текстовый файл с данными события...")
    file_path = filedialog.askopenfilename(
        title="Выберите файл с данными события",
        filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
    )

    if not file_path:
        print("Файл не выбран. Программа завершена.")
        return

    try:
        # Читаем содержимое файла
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()

        # Создаём парсер и обрабатываем текст
        parser = EventParser()
        results = parser.parse_event_text(text)
        
        # Группируем результаты по игрокам
        player_dates = group_by_player(results)
        
        # Выводим результаты и создаём личные сообщения
        print("\nРезультаты обработки и личные сообщения:")
        print("=" * 50)
        for player, dates in player_dates.items():
            print(f"\nИгрок: {player}")
            print(f"Даты игр: {', '.join(dates)}")
            message = create_personal_message(player, dates)
            print("\nЛичное сообщение:")
            print(message)
            print("-" * 30)

        # Создаем Excel-отчет
        create_excel_report(player_dates)

    except FileNotFoundError:
        print("Ошибка: Файл не найден.")
    except Exception as e:
        print(f"Произошла ошибка при чтении файла: {e}")

if __name__ == "__main__":
    main() 