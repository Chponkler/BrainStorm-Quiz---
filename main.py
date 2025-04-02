import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import random
import os
import requests
from datetime import datetime

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BrainStorm Quiz")
        self.root.geometry("800x600")
        
        # Настройки API
        self.API_KEY = "sk-d75b3a64d82042918ffefc966200a5a0"  # Замените на ваш ключ
        self.API_URL = "https://api.deepseek.com/v1/chat/completions"
        
        # Цветовая схема
        self.bg_color = "#2D2D2D"
        self.fg_color = "#FFFFFF"
        self.btn_color = "#3D3D3D"
        self.hover_color = "#4D4D4D"
        self.correct_color = "#81C784"
        self.wrong_color = "#FF8A80"
        self.normal_color = "#424242"
        
        self.root.configure(bg=self.bg_color)
        
        # Инициализация игры
        self.questions = []
        self.current_question = 0
        self.time_left = 30
        self.timer_id = None
        self.current_difficulty = ""
        self.num_players = 1
        self.players = []
        self.current_player = 0
        self.scores = {}
        
        # Подсказки
        self.hint_50_50_used = False
        self.hint_skip_used = False
        
        self.setup_welcome_screen()
    
    def clear_screen(self):
        """Очищает все виджеты с экрана"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def setup_welcome_screen(self):
        """Главное меню"""
        self.clear_screen()
        
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(expand=True, padx=20, pady=20)
        
        # Заголовок
        tk.Label(
            main_frame,
            text="BrainStorm Quiz",
            font=("Arial", 24, "bold"),
            bg=self.bg_color,
            fg=self.fg_color
        ).pack(pady=20)
        
        # Основные кнопки
        buttons_frame = tk.Frame(main_frame, bg=self.bg_color)
        buttons_frame.pack(pady=20)
        
        tk.Button(
            buttons_frame,
            text="Начать игру",
            width=20,
            command=self.setup_difficulty_screen,
            bg=self.btn_color,
            fg=self.fg_color
        ).pack(pady=10)
        
        tk.Button(
            buttons_frame,
            text="Добавить вопросы",
            width=20,
            command=self.setup_question_editor,
            bg=self.btn_color,
            fg=self.fg_color
        ).pack(pady=10)
        
        tk.Button(
            buttons_frame,
            text="Генератор ИИ",
            width=20,
            command=self.setup_ai_generator,
            bg=self.btn_color,
            fg=self.fg_color
        ).pack(pady=10)
    
    def setup_difficulty_screen(self):
        """Экран выбора сложности"""
        self.clear_screen()
        
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(expand=True, padx=20, pady=20)
        
        tk.Label(
            main_frame,
            text="Выберите уровень сложности",
            font=("Arial", 16),
            bg=self.bg_color,
            fg=self.fg_color
        ).pack(pady=20)
        
        levels = [("Легкий", "easy"), ("Средний", "medium"), ("Сложный", "hard")]
        
        for text, level in levels:
            tk.Button(
                main_frame,
                text=text,
                width=20,
                command=lambda l=level: self.select_difficulty(l),
                bg=self.btn_color,
                fg=self.fg_color
            ).pack(pady=10)
    
    def select_difficulty(self, difficulty):
        """Обработка выбора сложности"""
        self.current_difficulty = difficulty
        self.setup_player_selection_screen()
    
    def setup_player_selection_screen(self):
        """Экран выбора количества игроков"""
        self.clear_screen()
        
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(expand=True, padx=20, pady=20)
        
        tk.Label(
            main_frame,
            text="Выберите количество игроков",
            font=("Arial", 16),
            bg=self.bg_color,
            fg=self.fg_color
        ).pack(pady=20)
        
        for i in range(1, 4):
            tk.Button(
                main_frame,
                text=f"{i} игрок{'а' if i > 1 else ''}",
                width=20,
                command=lambda n=i: self.start_game(n),
                bg=self.btn_color,
                fg=self.fg_color
            ).pack(pady=10)
    
    def start_game(self, num_players):
        """Начало игры"""
        self.num_players = num_players
        self.players = [f"Игрок {i+1}" for i in range(num_players)]
        self.scores = {i: 0 for i in range(num_players)}
        self.current_player = 0
        
        # Проверка наличия вопросов
        if not self.load_questions(self.current_difficulty):
            messagebox.showerror("Ошибка", "Нет вопросов для выбранного уровня сложности!")
            self.setup_welcome_screen()
            return
        
        self.setup_quiz_ui()
        self.update_ui()
    
    def load_questions(self, difficulty):
        """Загрузка вопросов из файла"""
        try:
            filename = f"questions/{difficulty}.json"
            if os.path.exists(filename):
                with open(filename, "r", encoding="utf-8") as f:
                    self.questions = json.load(f)
                random.shuffle(self.questions)
                return len(self.questions) > 0
            return False
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить вопросы: {str(e)}")
            return False
    
    def setup_quiz_ui(self):
        """Настройка игрового интерфейса"""
        self.clear_screen()
        
        # Верхняя панель
        top_frame = tk.Frame(self.root, bg=self.bg_color)
        top_frame.pack(fill="x", padx=20, pady=10)
        
        self.player_label = tk.Label(
            top_frame,
            text=f"Ход: {self.players[self.current_player]}",
            font=("Arial", 12, "bold"),
            bg=self.bg_color,
            fg=self.fg_color
        )
        self.player_label.pack(side="left")
        
        self.timer_label = tk.Label(
            top_frame,
            text="Время: 30",
            font=("Arial", 12, "bold"),
            bg=self.bg_color,
            fg=self.fg_color
        )
        self.timer_label.pack(side="right")
        
        # Вопрос
        self.question_label = tk.Label(
            self.root,
            text="",
            wraplength=700,
            font=("Arial", 14, "bold"),
            bg=self.bg_color,
            fg=self.fg_color,
            pady=20
        )
        self.question_label.pack()
        
        # Варианты ответов
        self.option_buttons = []
        for i in range(4):
            btn = tk.Button(
                self.root,
                text="",
                width=60,
                font=("Arial", 12),
                bg=self.normal_color,
                fg=self.fg_color,
                activebackground=self.hover_color,
                command=lambda idx=i: self.check_answer(idx)
            )
            btn.pack(pady=5, ipady=5)
            self.option_buttons.append(btn)
        
        # Нижняя панель
        bottom_frame = tk.Frame(self.root, bg=self.bg_color)
        bottom_frame.pack(fill="x", pady=20)
        
        self.hint_50_50 = tk.Button(
            bottom_frame,
            text="50/50",
            command=self.use_50_50,
            bg=self.btn_color,
            fg=self.fg_color
        )
        self.hint_50_50.pack(side="left", padx=20)
        
        self.hint_skip = tk.Button(
            bottom_frame,
            text="Пропуск",
            command=self.skip_question,
            bg=self.btn_color,
            fg=self.fg_color
        )
        self.hint_skip.pack(side="right", padx=20)
    
    def update_ui(self):
        """Обновление интерфейса"""
        if self.current_question < len(self.questions):
            q = self.questions[self.current_question]
            self.question_label.config(text=q["question"])
            
            for i, option in enumerate(q["options"]):
                self.option_buttons[i].config(
                    text=option,
                    state="normal",
                    bg=self.normal_color
                )
            
            self.player_label.config(text=f"Ход: {self.players[self.current_player]}")
            self.start_timer()
        else:
            self.show_results()
    
    def start_timer(self):
        """Запуск таймера"""
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        
        self.time_left = 30
        self.update_timer()
    
    def update_timer(self):
        """Обновление таймера"""
        if self.time_left > 5:
            color = self.fg_color
        else:
            color = "#FF5252"
        
        self.timer_label.config(text=f"Время: {self.time_left}", fg=color)
        
        if self.time_left > 0:
            self.time_left -= 1
            self.timer_id = self.root.after(1000, self.update_timer)
        else:
            self.next_question()
    
    def check_answer(self, selected_idx):
        """Проверка ответа"""
        correct_idx = self.questions[self.current_question]["correct_answer"]
        
        # Подсветка ответов
        self.option_buttons[correct_idx].config(bg=self.correct_color)
        if selected_idx != correct_idx:
            self.option_buttons[selected_idx].config(bg=self.wrong_color)
        else:
            self.scores[self.current_player] += 1
        
        # Блокировка кнопок
        for btn in self.option_buttons:
            btn.config(state="disabled")
        
        # Переход к следующему вопросу через 2 секунды
        self.root.after(2000, self.next_question)
    
    def next_question(self):
        """Переход к следующему вопросу"""
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        
        self.current_player = (self.current_player + 1) % self.num_players
        self.current_question += 1
        
        # Сброс подсказок
        self.hint_50_50_used = False
        self.hint_50_50.config(state="normal")
        self.hint_skip_used = False
        self.hint_skip.config(state="normal")
        
        self.update_ui()
    
    def use_50_50(self):
        """Подсказка 50/50"""
        if not self.hint_50_50_used:
            correct_idx = self.questions[self.current_question]["correct_answer"]
            options_to_keep = [correct_idx]
            
            wrong_options = [i for i in range(4) if i != correct_idx]
            options_to_keep.append(random.choice(wrong_options))
            
            for i in range(4):
                if i not in options_to_keep:
                    self.option_buttons[i].config(state="disabled")
            
            self.hint_50_50_used = True
            self.hint_50_50.config(state="disabled")
    
    def skip_question(self):
        """Пропуск вопроса"""
        if not self.hint_skip_used:
            self.next_question()
            self.hint_skip_used = True
            self.hint_skip.config(state="disabled")
    
    def show_results(self):
        """Показ результатов"""
        result_text = "Игра окончена!\n\n"
        
        for i in range(self.num_players):
            result_text += f"{self.players[i]}: {self.scores[i]}\n"
        
        # Определение победителя
        max_score = max(self.scores.values())
        winners = [i for i, score in self.scores.items() if score == max_score]
        
        if len(winners) > 1:
            result_text += "\nНичья между: " + ", ".join(self.players[i] for i in winners)
        else:
            result_text += f"\nПобедитель: {self.players[winners[0]]}"
        
        # Окно результатов
        result_window = tk.Toplevel(self.root)
        result_window.title("Результаты")
        result_window.geometry("400x300")
        result_window.configure(bg=self.bg_color)
        
        tk.Label(
            result_window,
            text=result_text,
            font=("Arial", 14),
            bg=self.bg_color,
            fg=self.fg_color,
            pady=20
        ).pack()
        
        tk.Button(
            result_window,
            text="Новая игра",
            command=lambda: [result_window.destroy(), self.setup_welcome_screen()],
            bg=self.btn_color,
            fg=self.fg_color
        ).pack(pady=20)
    
    def setup_question_editor(self):
        """Редактор вопросов"""
        self.clear_screen()
        
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(expand=True, padx=20, pady=20)
        
        # Заголовок
        tk.Label(
            main_frame,
            text="Редактор вопросов",
            font=("Arial", 16),
            bg=self.bg_color,
            fg=self.fg_color
        ).pack(pady=20)
        
        # Выбор сложности
        tk.Label(
            main_frame,
            text="Уровень сложности:",
            bg=self.bg_color,
            fg=self.fg_color
        ).pack()
        
        self.difficulty_var = tk.StringVar(value="medium")
        difficulties = [("Легкий", "easy"), ("Средний", "medium"), ("Сложный", "hard")]
        
        for text, level in difficulties:
            tk.Radiobutton(
                main_frame,
                text=text,
                variable=self.difficulty_var,
                value=level,
                bg=self.bg_color,
                fg=self.fg_color,
                selectcolor=self.bg_color
            ).pack(anchor="w")
        
        # Поля для вопроса
        tk.Label(
            main_frame,
            text="Текст вопроса:",
            bg=self.bg_color,
            fg=self.fg_color
        ).pack(pady=(10,0))
        
        self.question_entry = tk.Text(
            main_frame,
            height=4,
            width=50,
            bg=self.normal_color,
            fg=self.fg_color
        )
        self.question_entry.pack()
        
        # Поля для вариантов ответов
        tk.Label(
            main_frame,
            text="Варианты ответов:",
            bg=self.bg_color,
            fg=self.fg_color
        ).pack(pady=(10,0))
        
        self.option_entries = []
        for i in range(4):
            tk.Label(
                main_frame,
                text=f"Вариант {i+1}:",
                bg=self.bg_color,
                fg=self.fg_color
            ).pack()
            
            entry = tk.Entry(
                main_frame,
                width=50,
                bg=self.normal_color,
                fg=self.fg_color
            )
            entry.pack()
            self.option_entries.append(entry)
        
        # Поле для правильного ответа
        tk.Label(
            main_frame,
            text="Номер правильного ответа (1-4):",
            bg=self.bg_color,
            fg=self.fg_color
        ).pack(pady=(10,0))
        
        self.correct_answer_entry = tk.Entry(
            main_frame,
            width=5,
            bg=self.normal_color,
            fg=self.fg_color
        )
        self.correct_answer_entry.pack()
        
        # Кнопки
        buttons_frame = tk.Frame(main_frame, bg=self.bg_color)
        buttons_frame.pack(pady=20)
        
        tk.Button(
            buttons_frame,
            text="Сохранить вопрос",
            command=self.save_manual_question,
            bg=self.btn_color,
            fg=self.fg_color
        ).pack(side="left", padx=10)
        
        tk.Button(
            buttons_frame,
            text="Назад",
            command=self.setup_welcome_screen,
            bg=self.btn_color,
            fg=self.fg_color
        ).pack(side="right", padx=10)
    
    def save_manual_question(self):
        """Сохранение вопроса, добавленного вручную"""
        difficulty = self.difficulty_var.get()
        question_text = self.question_entry.get("1.0", "end").strip()
        options = [entry.get().strip() for entry in self.option_entries]
        correct_answer = self.correct_answer_entry.get().strip()
        
        # Проверка ввода
        if not question_text:
            messagebox.showerror("Ошибка", "Введите текст вопроса")
            return
        
        if not all(options):
            messagebox.showerror("Ошибка", "Заполните все варианты ответов")
            return
        
        try:
            correct_idx = int(correct_answer) - 1
            if correct_idx not in range(4):
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Правильный ответ должен быть числом от 1 до 4")
            return
        
        # Формируем вопрос
        new_question = {
            "question": question_text,
            "options": options,
            "correct_answer": correct_idx,
            "category": "Пользовательский"
        }
        
        # Сохраняем в файл
        filename = f"questions/{difficulty}.json"
        questions = []
        
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                questions = json.load(f)
        
        questions.append(new_question)
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)
        
        messagebox.showinfo("Успех", "Вопрос успешно сохранен!")
        self.setup_question_editor()
    
    def setup_ai_generator(self):
        """Генератор вопросов через ИИ"""
        self.clear_screen()
        
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(expand=True, padx=20, pady=20)
        
        # Интерфейс генератора
        tk.Label(
            main_frame,
            text="Генератор вопросов ИИ",
            font=("Arial", 16),
            bg=self.bg_color,
            fg=self.fg_color
        ).pack(pady=20)
        
        # Поля ввода
        tk.Label(
            main_frame,
            text="Тема вопросов:",
            bg=self.bg_color,
            fg=self.fg_color
        ).pack()
        self.ai_topic_entry = tk.Entry(
            main_frame,
            width=50,
            bg=self.normal_color,
            fg=self.fg_color
        )
        self.ai_topic_entry.pack(pady=5)
        
        tk.Label(
            main_frame,
            text="Количество (1-10):",
            bg=self.bg_color,
            fg=self.fg_color
        ).pack()
        self.ai_count_entry = tk.Entry(
            main_frame,
            width=50,
            bg=self.normal_color,
            fg=self.fg_color
        )
        self.ai_count_entry.insert(0, "5")
        self.ai_count_entry.pack(pady=5)
        
        tk.Label(
            main_frame,
            text="Уровень сложности:",
            bg=self.bg_color,
            fg=self.fg_color
        ).pack()
        
        self.ai_difficulty = tk.StringVar(value="medium")
        difficulties = [("Легкий", "easy"), ("Средний", "medium"), ("Сложный", "hard")]
        
        for text, level in difficulties:
            tk.Radiobutton(
                main_frame,
                text=text,
                variable=self.ai_difficulty,
                value=level,
                bg=self.bg_color,
                fg=self.fg_color,
                selectcolor=self.bg_color
            ).pack(anchor="w")
        
        # Кнопки
        buttons_frame = tk.Frame(main_frame, bg=self.bg_color)
        buttons_frame.pack(pady=20)
        
        tk.Button(
            buttons_frame,
            text="Сгенерировать",
            command=self.generate_ai_questions,
            bg=self.btn_color,
            fg=self.fg_color
        ).pack(side="left", padx=10)
        
        tk.Button(
            buttons_frame,
            text="Назад",
            command=self.setup_welcome_screen,
            bg=self.btn_color,
            fg=self.fg_color
        ).pack(side="right", padx=10)
    
    def generate_ai_questions(self):
        """Генерация вопросов через API"""
        topic = self.ai_topic_entry.get()
        count = self.ai_count_entry.get()
        difficulty = self.ai_difficulty.get()
        
        if not topic:
            messagebox.showerror("Ошибка", "Введите тему вопросов")
            return
        
        try:
            count = int(count)
            if count < 1 or count > 10:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Введите число от 1 до 10")
            return
        
        # Окно загрузки
        progress = tk.Toplevel(self.root)
        progress.title("Генерация")
        tk.Label(progress, text="Генерация вопросов...").pack(pady=20)
        progress.update()
        
        try:
            # Реальный вызов DeepSeek API
            questions = self.call_deepseek_api(topic, count)
            self.save_ai_questions(questions, difficulty)
            messagebox.showinfo("Успех", f"Добавлено {len(questions)} вопросов!")
            self.setup_welcome_screen()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка генерации: {str(e)}")
        finally:
            progress.destroy()
    
    def call_deepseek_api(self, topic, count):
        """Запрос к DeepSeek API"""
        headers = {
            "Authorization": f"Bearer {self.API_KEY}",
            "Content-Type": "application/json"
        }
        
        prompt = f"""Сгенерируй {count} вопросов викторины на тему "{topic}" в формате JSON.
        Каждый вопрос должен содержать:
        - question (текст вопроса)
        - options (ровно 4 варианта ответа)
        - correct_answer (индекс 0-3)
        - category (категория)
        
        Пример:
        {{
            "question": "Как называется спутник Земли?",
            "options": ["Фобос", "Ио", "Луна", "Титан"],
            "correct_answer": 2,
            "category": "Астрономия"
        }}
        Верни ТОЛЬКО JSON-массив без каких-либо пояснений."""
        
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        response = requests.post(self.API_URL, headers=headers, json=data, timeout=30)
        
        # Проверка статуса ответа
        if response.status_code == 402:
            raise Exception("Payment Required - Проверьте ваш API-ключ и баланс")
        elif response.status_code != 200:
            raise Exception(f"API Error: {response.status_code} - {response.text}")
        
        try:
            content = response.json()["choices"][0]["message"]["content"]
            questions = self.parse_ai_response(content)
            
            if len(questions) != count:
                raise ValueError(f"Ожидалось {count} вопросов, получено {len(questions)}")
                
            return questions
        except Exception as e:
            raise ValueError(f"Ошибка обработки ответа API: {str(e)}")
    
    def parse_ai_response(self, text):
        """Парсинг ответа от API"""
        try:
            # Ищем начало и конец JSON
            start = text.find('[')
            end = text.rfind(']') + 1
            json_str = text[start:end]
            
            # Удаляем возможные markdown-символы ```json ```
            json_str = json_str.replace('```json', '').replace('```', '')
            
            questions = json.loads(json_str)
            
            # Валидация структуры
            for q in questions:
                if not all(k in q for k in ["question", "options", "correct_answer"]):
                    raise ValueError("Неверный формат вопроса")
                if len(q["options"]) != 4:
                    raise ValueError("Должно быть 4 варианта ответа")
                if q["correct_answer"] not in [0, 1, 2, 3]:
                    raise ValueError("correct_answer должен быть 0-3")
            
            return questions
        except Exception as e:
            raise ValueError(f"Ошибка парсинга JSON: {str(e)}\nПолученный текст:\n{text}")
    
    def save_ai_questions(self, questions, difficulty):
        """Сохранение вопросов в файл"""
        filename = f"questions/{difficulty}.json"
        
        # Загрузка существующих вопросов
        existing = []
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                existing = json.load(f)
        
        # Добавление новых
        existing.extend(questions)
        
        # Сохранение
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    # Создание папки и файлов вопросов
    os.makedirs("questions", exist_ok=True)
    for level in ["easy", "medium", "hard"]:
        if not os.path.exists(f"questions/{level}.json"):
            with open(f"questions/{level}.json", "w", encoding="utf-8") as f:
                json.dump([], f)
    
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()
