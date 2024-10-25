# utils/utils.py

from PyQt5.QtWidgets import QMessageBox

def is_valid_coordinate(x, y):
    """判断坐标是否有效"""
    try:
        return isinstance(x, (int, float)) and isinstance(y, (int, float))
    except:
        return False

def show_error_message(parent, title, message):
    """显示错误信息对话框"""
    QMessageBox.critical(parent, title, message)
