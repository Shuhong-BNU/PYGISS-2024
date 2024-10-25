# mainWindow.py

import logging
from PyQt5.QtWidgets import (
    QMainWindow, QHBoxLayout, QWidget, QMessageBox, QApplication, QFileDialog, QTextEdit
)
from PyQt5.QtCore import Qt
from ui.menu import TGISMenu
from ui.mapWidget import MapWidget
from utils.utils import show_error_message

class TGIS_MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Extended PyGISS")

        try:
            # 获取屏幕大小
            screen_geometry = QApplication.primaryScreen().availableGeometry()
            screen_width = screen_geometry.width()
            screen_height = screen_geometry.height()

            # 设置主窗口大小
            self.resize(screen_width, screen_height)

            # 创建主布局，使用水平布局
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            self.layout = QHBoxLayout(central_widget)

            # 添加菜单和地图
            self.menu = TGISMenu(self)
            self.map_widget = MapWidget(self)  # 将主窗口对象 self 传递给 MapWidget

            self.layout.addWidget(self.menu, stretch=1)  # 左侧菜单栏
            self.layout.addWidget(self.map_widget, stretch=9)  # 地图显示区域

            # 添加属性信息显示区域
            self.attribute_display = QTextEdit()
            self.attribute_display.setReadOnly(True)
            self.attribute_display.setFixedWidth(200)  # 设置固定宽度
            self.layout.addWidget(self.attribute_display)  # 添加到主布局

            # 连接菜单信号到槽函数
            self.menu.import_shapefile_clicked.connect(self.import_shapefile)
            self.menu.import_nodes_clicked.connect(self.import_nodes)
            self.menu.projection_changed.connect(self.change_projection)
            self.menu.delete_map_clicked.connect(self.delete_map)
            self.menu.delete_selected_nodes_clicked.connect(self.delete_selected_nodes)
            self.menu.node_size_changed.connect(self.update_node_size)  # 连接节点尺寸调整信号
            self.menu.export_format_changed.connect(self.handle_export_format_changed)
            self.menu.attribute_query_clicked.connect(self.perform_attribute_query)  # 连接属性查询信号

            # 连接 shapefile_imported 信号来启用 Import Nodes 按钮
            self.map_widget.shapefile_imported.connect(self.enable_import_nodes)
            # 连接 MapWidget 的信号
            self.map_widget.feature_selected.connect(self.show_feature_attributes)

            logging.info("主窗口初始化完成")
        except Exception as e:
            logging.exception("初始化主窗口时发生错误")
            show_error_message(self, "初始化错误", f"无法初始化主窗口:\n{e}")
            self.close()

    def enable_import_nodes(self):
        try:
            logging.info("Shapefile imported, enabling Import Nodes button.")
            self.menu.import_nodes_button.setEnabled(True)
        except Exception as e:
            logging.exception("启用 Import Nodes 按钮时发生错误")
            show_error_message(self, "错误", f"无法启用 Import Nodes 按钮:\n{e}")

    def import_shapefile(self):
        """导入 Shapefile 底图"""
        try:
            logging.info("导入 Shapefile 功能被调用")
            self.map_widget.import_shapefile()
        except Exception as e:
            logging.exception("导入 Shapefile 时发生错误")
            show_error_message(self, "导入错误", f"无法导入 Shapefile:\n{e}")

    def import_nodes(self):
        """导入节点功能"""
        try:
            logging.info("导入节点功能被调用")
            self.map_widget.import_nodes()
        except Exception as e:
            logging.exception("导入节点时发生错误")
            show_error_message(self, "导入错误", f"无法导入节点:\n{e}")

    def change_projection(self, projection):
        """更改地图投影"""
        try:
            logging.info(f"切换投影到: {projection}")
            # 更新地图投影
            self.map_widget.change_projection(projection)
            self.menu.current_projection_label.setText(f"Current Coordinate System: {projection}")
        except Exception as e:
            logging.exception("更改地图投影时发生错误")
            show_error_message(self, "投影错误", f"无法更改地图投影:\n{e}")

    def delete_map(self):
        """删除地图"""
        try:
            logging.info("删除地图功能被调用")
            self.map_widget.delete_map()
        except Exception as e:
            logging.exception("删除地图时发生错误")
            show_error_message(self, "删除错误", f"无法删除地图:\n{e}")

    def delete_selected_nodes(self):
        """删除选中节点"""
        try:
            logging.info("删除选中节点功能被调用")
            self.map_widget.delete_selected_nodes()
        except Exception as e:
            logging.exception("删除选中节点时发生错误")
            show_error_message(self, "删除错误", f"无法删除选中节点:\n{e}")

    def update_node_size(self, value):
        """更新节点图片尺寸"""
        try:
            logging.info(f"更新节点图片尺寸为: {value}%")
            self.map_widget.update_node_size(value)
        except Exception as e:
            logging.exception("更新节点图片尺寸时发生错误")
            show_error_message(self, "更新错误", f"无法更新节点图片尺寸:\n{e}")

    def handle_export_format_changed(self, format):
        """处理导出格式变化的逻辑"""
        try:
            logging.info(f"导出地图为 {format} 功能被调用")
            file_dialog = QFileDialog(self)
            file_dialog.setNameFilter(f"{format.upper()} Files (*.{format.lower()})")
            file_path, _ = file_dialog.getSaveFileName(self, f"保存地图为 {format}", "", f"{format.upper()} Files (*.{format.lower()})")

            if file_path:
                try:
                    if format == "PNG":
                        self.map_widget.export_to_png(file_path)
                    elif format == "PDF":
                        self.map_widget.export_to_pdf(file_path)
                    elif format in ["JPG", "JPEG"]:
                        if format == "JPG":
                            self.map_widget.export_to_jpg(file_path)
                        else:
                            self.map_widget.export_to_jpeg(file_path)
                    logging.info(f"地图已成功导出为: {file_path}")
                    QMessageBox.information(self, "导出成功", f"地图已成功导出为: {file_path}")
                except Exception as e:
                    logging.error(f"导出地图失败: {e}")
                    self.show_error_message("导出错误", f"无法导出地图为 {format}:\n{e}")
            else:
                logging.info("用户取消了导出操作")
        except Exception as e:
            logging.exception(f"导出地图为 {format} 时发生错误")
            self.show_error_message("导出错误", f"无法导出地图为 {format}:\n{e}")

    def show_error_message(self, title, message):
        """显示错误消息框"""
        QMessageBox.critical(self, title, message)

    def show_feature_attributes(self, attributes):
        """显示要素的属性信息"""
        self.attribute_display.clear()
        for key, value in attributes.items():
            self.attribute_display.append(f"{key}: {value}")

    def perform_attribute_query(self, field, value):
        """执行属性查询并高亮符合条件的要素"""
        try:
            matching_items = self.map_widget.perform_attribute_query(field, value)
            if matching_items:
                QMessageBox.information(self, "查询结果", f"找到 {len(matching_items)} 个符合条件的要素。")
            else:
                QMessageBox.information(self, "查询结果", "未找到符合条件的要素。")
        except Exception as e:
            logging.exception("属性查询时发生错误")
            show_error_message(self, "查询错误", f"属性查询失败:\n{e}")
