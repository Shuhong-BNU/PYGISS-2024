# utils/utils.py
# 功能：提供实用函数，例如坐标验证和错误消息显示

from PyQt5.QtWidgets import QMessageBox


def is_valid_coordinate(x, y) -> bool:
    """
    判断坐标是否有效
    参数:
        x (float): x 坐标
        y (float): y 坐标
    返回:
        bool: 如果坐标有效则返回 True，否则返回 False
    """
    try:
        return isinstance(x, (int, float)) and isinstance(y, (int, float))
    except:
        return False


def show_error_message(parent, title: str, message: str) -> None:
    """
    显示错误信息对话框
    参数:
        parent: 父控件
        title (str): 对话框标题
        message (str): 错误信息内容
    """
    QMessageBox.critical(parent, title, message)
