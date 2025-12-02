"""
Главный файл приложения - улучшенная медицинская диагностическая система
"""

from gui import MedicalDiagnosticGUI
import tkinter as tk

def main():
    """Основная функция запуска приложения"""
    try:


        # Создаем и запускаем GUI
        app = MedicalDiagnosticGUI()
        app.run()

    except Exception as e:
        print(f"Ошибка при запуске приложения: {e}")
        import traceback
        traceback.print_exc()
        tk.messagebox.showerror("Ошибка", f"Ошибка при запуске приложения:\n{str(e)}")

if __name__ == "__main__":
    main()