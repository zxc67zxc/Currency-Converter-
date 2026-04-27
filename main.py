import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
from datetime import datetime

# --- КОНФИГУРАЦИЯ ---
API_KEY = "YOUR_API_KEY" # <--- ВСТАВЬТЕ СЮДА
BASE_URL = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/"
HISTORY_FILE = "history.json"
CURRENCIES = ["USD", "EUR", "RUB", "GBP", "JPY", "CHF"]

# --- ЛОГИКА ---
def get_rate(base, target):
    """Получение курса через API"""
    try:
        response = requests.get(f"{BASE_URL}{base}")
        data = response.json()
        if data['result'] == 'success':
            return data['rates'][target]
        else:
            raise Exception("Ошибка API")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось получить курс: {e}")
        return None

def convert():
    """Конвертация и сохранение истории"""
    try:
        amount = float(entry_amount.get())
        if amount <= 0: raise ValueError
    except ValueError:
        messagebox.showwarning("Ошибка ввода", "Введите положительное число")
        return

    from_curr = combo_from.get()
    to_curr = combo_to.get()
    
    rate = get_rate(from_curr, to_curr)
    if not rate: return
    
    result = amount * rate
    label_result.config(text=f"{result:.2f} {to_curr}")
    
    # Добавление в историю
    save_to_history(from_curr, to_curr, amount, result, rate)
    update_history_table()

def save_to_history(from_c, to_c, amt, res, rate):
    """Сохранение истории в JSON"""
    record = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "from": from_c,
        "to": to_c,
        "amount": amt,
        "result": round(res, 2),
        "rate": rate
    }
    
    history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            try: history = json.load(f)
            except: history = []
            
    history.append(record)
    # Храним только последние 10 записей
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history[-10:], f, indent=4)

def update_history_table():
    """Обновление таблицы истории"""
    for i in tree.get_children():
        tree.delete(i)
        
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            try: history = json.load(f)
            except: history = []
            
        for record in reversed(history):
            tree.insert("", "end", values=(
                record["time"], 
                f"{record['amount']} {record['from']}", 
                f"{record['result']} {record['to']}"
            ))

# --- ИНТЕРФЕЙС (GUI) ---
app = tk.Tk()
app.title("Currency Converter")
app.geometry("500x450")

# Выбор валют
frame_select = ttk.Frame(app)
frame_select.pack(pady=10)

ttk.Label(frame_select, text="Из:").pack(side=tk.LEFT)
combo_from = ttk.Combobox(frame_select, values=CURRENCIES, width=5)
combo_from.current(0) # USD
combo_from.pack(side=tk.LEFT, padx=5)

ttk.Label(frame_select, text="В:").pack(side=tk.LEFT)
combo_to = ttk.Combobox(frame_select, values=CURRENCIES, width=5)
combo_to.current(2) # RUB
combo_to.pack(side=tk.LEFT, padx=5)

# Ввод суммы
entry_amount = ttk.Entry(app)
entry_amount.pack(pady=5)
entry_amount.insert(0, "100")

# Кнопка
btn_convert = ttk.Button(app, text="Конвертировать", command=convert)
btn_convert.pack(pady=10)

# Результат
label_result = ttk.Label(app, text="", font=("Helvetica", 16))
label_result.pack(pady=5)

# Таблица истории
columns = ("time", "from_val", "to_val")
tree = ttk.Treeview(app, columns=columns, show="headings", height=8)
tree.heading("time", text="Время")
tree.heading("from_val", text="Сумма")
tree.heading("to_val", text="Результат")
tree.column("time", width=150)
tree.pack(pady=10)

update_history_table()
app.mainloop()
