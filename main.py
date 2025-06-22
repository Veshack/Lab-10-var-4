import speech_recognition as sr
import pyttsx3
import requests
import json
import webbrowser
from datetime import datetime

class VoiceAssistant:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', self.voices[0].id)
        self.engine.setProperty('rate', 150)
        
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        self.language = 'ru-RU' 
        self.commands = {
            'ru-RU': {
                'доллар': self.get_currency_rate,
                'евро': self.get_currency_rate,
                'сохранить': self.save_rates,
                'количество': self.show_count,
                'случайный': self.random_currency,
                'стоп': self.stop,
                'сменить язык': self.switch_language
            },
            'en-US': {
                'find': self.find_word,
                'meaning': self.word_meaning,
                'link': self.open_dictionary,
                'example': self.word_example,
                'save': self.save_word,
                'stop': self.stop,
                'switch language': self.switch_language
            }
        }

    def speak(self, text):
        """Озвучивание текста"""
        print(f"Ассистент: {text}")
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self):
        """Прослушивание и распознавание команд"""
        with self.microphone as source:
            print("Слушаю...")
            self.recognizer.adjust_for_ambient_noise(source)
            audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
            
        try:
            text = self.recognizer.recognize_google(audio, language=self.language).lower()
            print(f"Вы сказали: {text}")
            return text
        except sr.UnknownValueError:
            self.speak("Не удалось распознать речь")
            return ""
        except sr.RequestError:
            self.speak("Ошибка сервиса распознавания")
            return ""
        except Exception as e:
            self.speak(f"Ошибка: {str(e)}")
            return ""

    # Функции для работы с валютами
    def get_currency_rate(self, currency=None):
        """Получение курса валюты"""
        if not currency:
            currency = "доллар" if self.language == 'ru-RU' else "usd"
        
        currency_map = {
            'ru-RU': {'доллар': 'usd', 'евро': 'eur'},
            'en-US': {'dollar': 'usd', 'euro': 'eur'}
        }
        
        currency_code = currency_map.get(self.language, {}).get(currency, currency)
        
        try:
            response = requests.get(
                "https://cdn.jsdelivr.net/gh/fawazahmed0/currency-api@1/latest/currencies/rub.json"
            )
            data = response.json()
            rate = data['rub'].get(currency_code.lower())
            
            if rate:
                rate_text = f"1 рубль равен {1/rate:.4f} {currency_code.upper()}"
                self.speak(rate_text)
                return rate_text
            else:
                error_text = "Валюта не найдена" if self.language == 'ru-RU' else "Currency not found"
                self.speak(error_text)
                return error_text
                
        except Exception as e:
            error_text = f"Ошибка: {str(e)}" if self.language == 'ru-RU' else f"Error: {str(e)}"
            self.speak(error_text)
            return error_text

    def save_rates(self, *_):
        """Сохранение текущих курсов в файл"""
        try:
            response = requests.get(
                "https://cdn.jsdelivr.net/gh/fawazahmed0/currency-api@1/latest/currencies/rub.json"
            )
            data = response.json()
            
            with open("currency_rates.txt", "a", encoding="utf-8") as f:
                f.write(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                json.dump(data['rub'], f, indent=2, ensure_ascii=False)
                
            self.speak("Курсы сохранены" if self.language == 'ru-RU' else "Rates saved")
            return True
            
        except Exception as e:
            error_text = f"Ошибка сохранения: {str(e)}" if self.language == 'ru-RU' else f"Save error: {str(e)}"
            self.speak(error_text)
            return False

    def show_count(self, *_):
        """Показ количества доступных валют"""
        try:
            response = requests.get(
                "https://cdn.jsdelivr.net/gh/fawazahmed0/currency-api@1/latest/currencies/rub.json"
            )
            data = response.json()
            count = len(data['rub'])
            self.speak(f"Доступно {count} валют" if self.language == 'ru-RU' else f"Available {count} currencies")
            return count
        except Exception as e:
            error_text = f"Ошибка: {str(e)}" if self.language == 'ru-RU' else f"Error: {str(e)}"
            self.speak(error_text)
            return 0

    def random_currency(self, *_):
        """Случайная валюта"""
        try:
            response = requests.get(
                "https://cdn.jsdelivr.net/gh/fawazahmed0/currency-api@1/latest/currencies/rub.json"
            )
            data = response.json()
            import random
            currency = random.choice(list(data['rub'].keys()))
            rate = data['rub'][currency]
            self.speak(f"Случайная валюта: {currency.upper()}, курс: {1/rate:.4f}")
            return currency
        except Exception as e:
            error_text = f"Ошибка: {str(e)}" if self.language == 'ru-RU' else f"Error: {str(e)}"
            self.speak(error_text)
            return None

    # Функции для работы со словарем (допзадание)
    def find_word(self, word):
        """Поиск слова в словаре"""
        if not word:
            self.speak("Укажите слово для поиска" if self.language == 'ru-RU' else "Specify word to find")
            return
        
        try:
            response = requests.get(
                f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
            )
            
            if response.status_code == 404:
                self.speak("Слово не найдено" if self.language == 'ru-RU' else "Word not found")
                return None
                
            data = response.json()[0]
            meanings = data.get('meanings', [])
            
            result = {
                'word': data['word'],
                'phonetic': data.get('phonetic', ''),
                'meanings': [],
                'examples': []
            }
            
            for meaning in meanings:
                result['meanings'].append({
                    'partOfSpeech': meaning['partOfSpeech'],
                    'definition': meaning['definitions'][0]['definition']
                })
                if 'example' in meaning['definitions'][0]:
                    result['examples'].append(meaning['definitions'][0]['example'])
            
            self.speak(f"Слово: {result['word']}")
            self.speak(f"Транскрипция: {result['phonetic']}")
            
            for meaning in result['meanings']:
                self.speak(f"{meaning['partOfSpeech']}: {meaning['definition']}")
            
            if result['examples']:
                self.speak("Примеры использования:")
                for example in result['examples']:
                    self.speak(example)
            
            return result
            
        except Exception as e:
            error_text = f"Ошибка: {str(e)}" if self.language == 'ru-RU' else f"Error: {str(e)}"
            self.speak(error_text)
            return None

    def word_meaning(self, *_):
        """Получить значение слова"""
        self.speak("Скажите 'find слово'" if self.language == 'ru-RU' else "Say 'find word'")

    def word_example(self, *_):
        """Получить примеры использования слова"""
        self.speak("Скажите 'find слово'" if self.language == 'ru-RU' else "Say 'find word'")

    def open_dictionary(self, *_):
        """Открыть сайт словаря"""
        webbrowser.open("https://dictionaryapi.dev/")
        self.speak("Открываю словарь" if self.language == 'ru-RU' else "Opening dictionary")

    def save_word(self, word=None):
        """Сохранение слова в файл"""
        if not word:
            self.speak("Укажите слово для сохранения" if self.language == 'ru-RU' else "Specify word to save")
            return
        
        try:
            with open("saved_words.txt", "a", encoding="utf-8") as f:
                f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {word}\n")
            
            self.speak("Слово сохранено" if self.language == 'ru-RU' else "Word saved")
            return True
        except Exception as e:
            error_text = f"Ошибка сохранения: {str(e)}" if self.language == 'ru-RU' else f"Save error: {str(e)}"
            self.speak(error_text)
            return False


    def switch_language(self, *_):
        """Переключение языка"""
        self.language = 'en-US' if self.language == 'ru-RU' else 'ru-RU'
        lang_name = "английский" if self.language == 'en-US' else "русский"
        self.speak(f"Язык изменен на {lang_name}")

    def stop(self, *_):
        """Остановка ассистента"""
        self.speak("Завершаю работу" if self.language == 'ru-RU' else "Shutting down")
        return False

    def process_command(self, text):
        """Обработка распознанной команды"""
        if not text:
            return True
            
        for command, func in self.commands[self.language].items():
            if text.startswith(command):
                argument = text[len(command):].strip()
                return func(argument) if argument else func()
        
        self.speak("Команда не распознана" if self.language == 'ru-RU' else "Command not recognized")
        return True

    def run(self):
        """Основной цикл работы ассистента"""
        self.speak("Голосовой ассистент запущен. Готов к работе.")
        
        running = True
        while running:
            text = self.listen()
            if text:
                running = self.process_command(text)

if __name__ == "__main__":
    assistant = VoiceAssistant()
    assistant.run()
