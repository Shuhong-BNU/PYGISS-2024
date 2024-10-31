# mainWindow.py
# 功能：实现 GIS 应用程序的主窗口类，包括与菜单和地图小部件的交互

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QMessageBox, QVBoxLayout, QWidget, QDockWidget, QTextEdit
)
from PyQt5.QtCore import Qt
import logging
from ui.menu import TGISMenu
from ui.mapWidget import MapWidget
from utils.utils import show_error_message


class TGIS_MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("地图应用")  # 设置主窗口标题
        self.resize(1000, 600)  # 设置主窗口大小

        # 创建菜单部件
        self.menu = TGISMenu(self)
        self.menu_widget = QWidget()
        self.menu_layout = QVBoxLayout(self.menu_widget)
        self.menu_layout.addWidget(self.menu)
        self.menu_widget.setFixedWidth(300)  # 增加菜单的固定宽度

        # 创建地图部件
        self.map_widget = MapWidget(self)

        # 设置主窗口的中心部件为地图部件
        self.setCentralWidget(self.map_widget)

        # 创建一个 QDockWidget 来包含菜单部件
        self.menu_dock_widget = QDockWidget("Menu", self)
        self.menu_dock_widget.setWidget(self.menu_widget)
        self.menu_dock_widget.setAllowedAreas(Qt.LeftDockWidgetArea)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.menu_dock_widget)

        # 创建属性信息窗口
        self.attribute_info_window = QDockWidget("Attribute Info", self)
        self.attribute_info_text = QTextEdit()
        self.attribute_info_text.setReadOnly(True)
        self.attribute_info_window.setWidget(self.attribute_info_text)
        self.attribute_info_window.setAllowedAreas(Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, self.attribute_info_window)

        # 创建属性表窗口
        self.attribute_table_window = None

        # 连接菜单信号和槽
        self.menu.import_shapefile_clicked.connect(self.import_shapefile)
        self.menu.import_nodes_clicked.connect(self.import_nodes)
        self.menu.projection_changed.connect(self.change_projection)
        self.menu.delete_map_clicked.connect(self.delete_map)
        self.menu.delete_selected_nodes_clicked.connect(self.delete_selected_nodes)
        self.menu.node_size_changed.connect(self.update_node_size)
        self.menu.output_button_clicked.connect(self.handle_output_button_clicked)
        self.menu.attribute_query_clicked.connect(self.perform_attribute_query)

        # 连接地图部件的信号和槽
        self.map_widget.shapefile_imported.connect(self.menu.enable_buttons)
        self.map_widget.attribute_table_requested.connect(self.show_attribute_table)
        self.map_widget.feature_attributes_updated.connect(self.update_attribute_info)

    def import_shapefile(self) -> None:
        """
        导入 Shapefile 文件
        """
        try:
            self.map_widget.import_shapefile()
            self.menu.import_nodes_button.setEnabled(True)
        except Exception as e:
            logging.error(f"Error importing shapefile: {e}")
            show_error_message(self, "导入错误", f"无法导入 Shapefile:\n{e}")

    def import_nodes(self) -> None:
        """
        导入节点文件
        """
        try:
            self.map_widget.import_nodes()
        except Exception as e:
            logging.error(f"Error importing nodes: {e}")
            show_error_message(self, "导入错误", f"无法导入节点文件:\n{e}")

    def change_projection(self, projection: str) -> None:
        """
        更改投影
        参数:
            projection (str): 新的投影字符串
        """
        try:
            self.map_widget.change_projection(projection)
        except Exception as e:
            logging.error(f"Error changing projection: {e}")
            show_error_message(self, "投影错误", f"无法更改投影:\n{e}")

    def delete_map(self) -> None:
        """
        删除地图和节点
        """
        self.map_widget.delete_map()
        self.menu.import_nodes_button.setEnabled(False)
        self.attribute_info_text.clear()

    def delete_selected_nodes(self) -> None:
        """
        删除选中的节点
        """
        self.map_widget.delete_selected_nodes()

    def update_node_size(self, value: int) -> None:
        """
        更新节点尺寸
        参数:
            value (int): 新的节点尺寸百分比
        """
        self.map_widget.update_node_size(value)

    def handle_output_button_clicked(self) -> None:
        """
        处理输出按钮的点击事件
        """
        format = self.menu.export_format_combo.currentText()
        if format.upper() == "PNG":
            self.export_to_png()
        elif format.upper() == "PDF":
            self.export_to_pdf()
        elif format.upper() == "JPG":
            self.export_to_jpeg()
        else:
            show_error_message(self, "导出错误", f"不支持的导出格式: {format}")

    def export_to_png(self) -> None:
        """
        导出地图为 PNG 文件
        """
        try:
            self.map_widget.export_to_png()
            QMessageBox.information(self, "导出成功", "地图已成功导出为 PNG 文件")
        except Exception as e:
            logging.error(f"Error exporting to PNG: {e}")
            show_error_message(self, "导出错误", f"无法导出地图为 PNG:\n{e}")

    def export_to_pdf(self) -> None:
        """
        导出地图为 PDF 文件
        """
        try:
            self.map_widget.export_to_pdf()
            QMessageBox.information(self, "导出成功", "地图已成功导出为 PDF 文件")
        except Exception as e:
            logging.error(f"Error exporting to PDF: {e}")
            show_error_message(self, "导出错误", f"无法导出地图为 PDF:\n{e}")

    def export_to_jpeg(self) -> None:
        """
        导出地图为 JPEG 文件
        """
        try:
            self.map_widget.export_to_jpeg()
            QMessageBox.information(self, "导出成功", "地图已成功导出为 JPEG 文件")
        except Exception as e:
            logging.error(f"Error exporting to JPEG: {e}")
            show_error_message(self, "导出错误", f"无法导出地图为 JPEG:\n{e}")

    def perform_attribute_query(self, field: str, value: str) -> None:
        """
        执行属性查询
        参数:
            field (str): 要查询的字段名
            value (str): 要匹配的字段值
        """
        try:
            matching_items = self.map_widget.perform_attribute_query(field, value)
            if not matching_items:
                QMessageBox.information(self, "查询结果", "未找到匹配的要素。")
        except Exception as e:
            logging.error(f"Error performing attribute query: {e}")
            show_error_message(self, "查询错误", f"执行属性查询时发生错误:\n{e}")

    def show_attribute_table(self, records: list) -> None:
        """
        显示属性表
        参数:
            records (list): 属性记录列表
        """
        try:
            if not records:
                show_error_message(self, "属性表", "当前没有可用的属性表。")
                return

            # 如果属性表窗口已存在，先关闭它
            if self.attribute_table_window is not None:
                self.removeDockWidget(self.attribute_table_window)
                self.attribute_table_window.deleteLater()
                self.attribute_table_window = None

            # 创建属性表窗口
            from PyQt5.QtWidgets import QDockWidget, QTableWidget, QTableWidgetItem
            self.attribute_table_window = QDockWidget("属性表", self)
            table_widget = QTableWidget()
            table_widget.setEditTriggers(QTableWidget.NoEditTriggers)
            table_widget.setSelectionBehavior(QTableWidget.SelectRows)
            table_widget.setSelectionMode(QTableWidget.SingleSelection)

            # 获取字段名称
            field_names = list(records[0].keys())
            table_widget.setColumnCount(len(field_names))
            table_widget.setHorizontalHeaderLabels(field_names)

            # 添加数据
            table_widget.setRowCount(len(records))
            for row, record in enumerate(records):
                for col, field in enumerate(field_names):
                    value = record.get(field, "")
                    item = QTableWidgetItem(str(value))
                    table_widget.setItem(row, col, item)

            table_widget.resizeColumnsToContents()

            self.attribute_table_window.setWidget(table_widget)
            self.attribute_table_window.setAllowedAreas(Qt.BottomDockWidgetArea | Qt.TopDockWidgetArea)
            self.addDockWidget(Qt.BottomDockWidgetArea, self.attribute_table_window)
        except Exception as e:
            logging.error(f"Error during showing attribute table: {e}")
            show_error_message(self, "属性表错误", f"显示属性表时发生错误:\n{e}")

    def update_attribute_info(self, attributes: dict) -> None:
        """
        更新属性信息面板
        参数:
            attributes (dict): 要素的属性字典
        """
        if attributes is None:
            self.attribute_info_text.setText("未选择任何要素")
        else:
            attr_text = "\n".join([f"{key}: {value}" for key, value in attributes.items()])
            self.attribute_info_text.setText(attr_text)

    def closeEvent(self, event) -> None:
        """
        关闭事件
        """
        reply = QMessageBox.question(self, "退出", "确定要退出程序吗？", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


def main() -> None:
    """
    设置日志记录并启动应用程序
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logging.info("GIS 应用程序启动")

    app = QApplication(sys.argv)
    window = TGIS_MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
