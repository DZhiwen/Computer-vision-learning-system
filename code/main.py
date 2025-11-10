import sys
from PySide6.QtWidgets import QApplication
from login_window import LoginWindow
from db_manager import get_user_data_dir

if __name__ == "__main__":

    user_data_dir = get_user_data_dir()
    
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())
