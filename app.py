import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os


DATA_FILE = "data/expenses.json"


# Хранение расходов в списке и загрузка из JSON
def load_expenses():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")
        return []


def save_expenses(expenses):
    try:
        os.makedirs("data", exist_ok=True)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(expenses, f, ensure_ascii=False, indent=4)
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")


class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("800x600")

        self.expenses = load_expenses()

        self.setup_ui()
        self.update_table()

    def setup_ui(self):
        # Фрейм для ввода нового расхода
        input_frame = ttk.Frame(self.root, padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(input_frame, text="Сумма").grid(row=0, column=0, sticky="w", padx=5)
        self.amount_entry = tk.Entry(input_frame, width=20)
        self.amount_entry.grid(row=0, column=1, padx=5)

        ttk.Label(input_frame, text="Категория").grid(row=0, column=2, sticky="w", padx=5)
        self.category_entry = tk.Entry(input_frame, width=20)
        self.category_entry.grid(row=0, column=3, padx=5)

        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД)").grid(row=0, column=4, sticky="w", padx=5)
        self.date_entry = tk.Entry(input_frame, width=15)
        self.date_entry.grid(row=0, column=5, padx=5)

        add_btn = ttk.Button(input_frame, text="Добавить расход", command=self.add_expense)
        add_btn.grid(row=0, column=6, padx=10)

        # Фрейм фильтров и подсчёта
        filter_frame = ttk.Frame(self.root, padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(filter_frame, text="Категория").grid(row=0, column=0, sticky="w", padx=5)
        self.filter_category = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.filter_category, width=20).grid(row=0, column=1, padx=5)

        ttk.Label(filter_frame, text="С даты (ГГГГ-ММ-ДД)").grid(row=0, column=2, sticky="w", padx=5)
        self.filter_date_from = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.filter_date_from, width=15).grid(row=0, column=3, padx=5)

        ttk.Label(filter_frame, text="По дату").grid(row=0, column=4, sticky="w", padx=5)
        self.filter_date_to = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.filter_date_to, width=15).grid(row=0, column=5, padx=5)

        apply_btn = ttk.Button(filter_frame, text="Применить фильтры", command=self.apply_filters)
        apply_btn.grid(row=0, column=6, padx=10)

        total_label = ttk.Label(filter_frame, text="Сумма за период:")
        total_label.grid(row=1, column=0, columnspan=1, sticky="w", padx=5)
        self.total_var = tk.StringVar(value="0.00")
        total_display = ttk.Label(filter_frame, textvariable=self.total_var)
        total_display.grid(row=1, column=6, padx=10, pady=5)

        # Таблица с расходами
        tree_frame = ttk.Frame(self.root)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("amount", "category", "date")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        self.tree.heading("amount", text="Сумма")
        self.tree.heading("category", text="Категория")
        self.tree.heading("date", text="Дата")

        self.tree.column("amount", width=100, anchor="e")
        self.tree.column("category", width=150, anchor="w")
        self.tree.column("date", width=100, anchor="w")

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

    def validate_input(self):
        amount_str = self.amount_entry.get().strip()
        category = self.category_entry.get().strip()
        date_str = self.date_entry.get().strip()

        if not amount_str or not amount_str.replace(".", "").isdigit():
            messagebox.showerror("Ошибка", "Сумма должна быть положительным числом.")
            return False
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Сумма должна быть положительным числом.")
            return False

        if not category:
            messagebox.showerror("Ошибка", "Введите категорию.")
            return False

        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Ошибка", "Дата должна быть в формате ГГГГ-ММ-ДД.")
            return False

        return True

    def add_expense(self):
        if not self.validate_input():
            return

        amount = float(self.amount_entry.get().strip())
        category = self.category_entry.get().strip()
        date_str = self.date_entry.get().strip()

        new_expense = {
            "amount": amount,
            "category": category,
            "date": date_str
        }

        self.expenses.append(new_expense)
        save_expenses(self.expenses)

        self.update_table()
        self.clear_inputs()

    def clear_inputs(self):
        self.amount_entry.delete(0, tk.END)
        self.category_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)

    def update_table(self, filtered=None):
        for row in self.tree.get_children():
            self.tree.delete(row)

        expenses = filtered or self.expenses
        total = 0.0

        for exp in expenses:
            self.tree.insert("", tk.END, values=(exp["amount"], exp["category"], exp["date"]))
            total += exp["amount"]

        self.total_var.set(f"{total:.2f}")

    def parse_date(self, date_str):
        if not date_str.strip():
            return None
        try:
            return datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
        except ValueError:
            return None

    def apply_filters(self):
        category = self.filter_category.get().strip()
        from_date = self.parse_date(self.filter_date_from.get())
        to_date = self.parse_date(self.filter_date_to.get())

        filtered = self.expenses

        if category:
            filtered = [e for e in filtered if category.lower() in e["category"].lower()]

        if from_date:
            filtered = [e for e in filtered if datetime.strptime(e["date"], "%Y-%m-%d").date() >= from_date]

        if to_date:
            filtered = [e for e in filtered if datetime.strptime(e["date"], "%Y-%m-%d").date() <= to_date]

        self.update_table(filtered)


if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTrackerApp(root)
    root.mainloop()