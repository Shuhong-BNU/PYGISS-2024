# main.py
# 功能：GIS 应用程序的入口文件，设置日志记录并启动主窗口

import sys
import logging
from PyQt5.QtWidgets import QApplication, QMessageBox
from mainWindow import TGIS_MainWindow


def main() -> None:
    """
    应用程序的入口函数，配置日志记录并启动主窗口
    """
    # 配置日志记录
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("app.log", mode='w'),  # 每次运行时覆盖旧的日志文件
            logging.StreamHandler(sys.stdout)  # 输出日志到控制台
        ]
    )

    logging.info("GIS 应用程序启动")

    try:
        app = QApplication(sys.argv)  # 创建应用程序对象
        window = TGIS_MainWindow()  # 创建主窗口对象
        window.show()  # 显示主窗口
        sys.exit(app.exec_())  # 进入应用程序主循环
    except Exception as e:
        logging.exception("应用程序运行时发生错误")
        QMessageBox.critical(None, "应用程序错误", f"无法启动应用程序:\n{e}")


if __name__ == "__main__":
    main()
