from datetime import datetime
import re

class PaymentChecker:
    def __init__(self):
        self.payments = {}

class EventParser:
    def __init__(self):
        self.weekday_map = {
            'Monday': 'пн',
            'Tuesday': 'вт',
            'Wednesday': 'ср',
            'Thursday': 'чт',
            'Friday': 'пт',
            'Saturday': 'сб',
            'Sunday': 'вс'
        }

    def parse_event_text(self, text):
        """Парсинг текста события и получение списка участников"""
        participants = []
        current_date = None
        current_weekday = None
        current_year = 2025  # Задаем год по умолчанию из контекста
        
        lines = text.split('\n')
        for line in lines:
            # Ищем дату в формате YYYY-MM-DD
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', line)
            if date_match:
                date_str = date_match.group(1)
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                current_date = date_obj.strftime('%d.%m')
                current_weekday = self.weekday_map[date_obj.strftime('%A')]
                continue
            
            # Ищем дату в формате DD.MM (новый формат)
            short_date_match = re.search(r'┌\s*(\d{2}\.\d{2})\s*\((\w+)\)', line)
            if short_date_match:
                date_str = short_date_match.group(1)
                weekday_eng = short_date_match.group(2)
                current_date = date_str
                # Если есть день недели на английском, преобразуем его
                if weekday_eng in self.weekday_map:
                    current_weekday = self.weekday_map[weekday_eng]
                # Если день недели не распознан, пытаемся определить его через дату
                else:
                    try:
                        # Добавляем год к короткой дате для определения дня недели
                        full_date = f"{current_year}-{date_str.split('.')[1]}-{date_str.split('.')[0]}"
                        date_obj = datetime.strptime(full_date, '%Y-%m-%d')
                        current_weekday = self.weekday_map[date_obj.strftime('%A')]
                    except:
                        # В случае ошибки парсинга используем четверг (как в примере)
                        current_weekday = 'чт'
                continue

            # Ищем участников в формате с votes
            vote_match = re.search(r'[├└]?\s*(?:[\d.]+\s*)?([^(]+)\((\d+)\s*votes\)', line)
            if vote_match and current_date and current_weekday:
                name = vote_match.group(1).strip()
                votes = int(vote_match.group(2))
                for _ in range(votes):
                    participant_str = f"{current_date} {current_weekday} {name}"
                    participants.append(participant_str)
                continue

            # Ищем формат с total votes (новый формат)
            total_votes_match = re.search(r'[├└]?\s*\d+\.\s*([^(]+)\((\d+)\s*votes\s*total\)', line)
            if total_votes_match and current_date and current_weekday:
                name = total_votes_match.group(1).strip()
                votes = int(total_votes_match.group(2))
                for _ in range(votes):
                    participant_str = f"{current_date} {current_weekday} {name}"
                    participants.append(participant_str)
                continue

            # Ищем участников в формате с номером
            numbered_match = re.search(r'[├└]\s*\d+\.\s*([^└├\n]+)', line)
            if numbered_match and current_date and current_weekday:
                name = numbered_match.group(1).strip()
                participant_str = f"{current_date} {current_weekday} {name}"
                participants.append(participant_str)

        return participants