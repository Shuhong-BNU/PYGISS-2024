# main.py

import sys
import logging
from PyQt5.QtWidgets import QApplication, QMessageBox
from mainWindow import TGIS_MainWindow

def main():
    # 配置日志记录
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("app.log", mode='w'),  # 每次运行时覆盖旧的日志文件
            logging.StreamHandler(sys.stdout)
        ]
    )

    logging.info("GIS 应用程序启动")

    try:
        app = QApplication(sys.argv)
        window = TGIS_MainWindow()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        logging.exception("应用程序运行时发生错误")
        QMessageBox.critical(None, "应用程序错误", f"无法启动应用程序:\n{e}")

if __name__ == "__main__":
    main()
