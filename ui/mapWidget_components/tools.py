# ui/mapWidget_components/tools.py
# 功能：提供地图工具的功能，包括属性查询、导出地图为图片或 PDF 文件等

from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtGui import QImage, QPainter, QImageWriter, QPen
from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtPrintSupport import QPrinter
import logging
from utils.utils import show_error_message

class ToolsMixin:
    def perform_attribute_query(self, field: str, value: str) -> list:
        """
        执行属性查询并高亮符合条件的要素
        参数:
            field (str): 要查询的字段名
            value (str): 要匹配的字段值
        返回:
            list: 符合条件的要素项列表
        """
        try:
            matching_items = []
            for item in self.polygon_items:
                if field in item.attributes and str(item.attributes[field]) == value:
                    matching_items.append(item)
            if matching_items:
                self.clear_highlights()  # 清除之前的高亮
                for item in matching_items:
                    self.highlight_feature(item)  # 高亮显示匹配的要素
                # 显示属性表
                self.attribute_table_requested.emit(
                    [item.attributes for item in matching_items])
                # 显示第一个匹配要素的属性信息
                self.display_feature_attributes(matching_items[0].attributes)
                return matching_items
            else:
                self.clear_highlights()
                QMessageBox.information(self, "查询结果", "未找到匹配的要素。")
                self.display_feature_attributes(None)
                return []
        except Exception as e:
            logging.error(f"Error during attribute query: {e}")
            show_error_message(self, "查询错误", f"执行属性查询时发生错误:\n{e}")
            return []

    def open_attribute_table(self) -> None:
        """
        打开属性表
        """
        try:
            if not hasattr(self.map_data, 'records') or not isinstance(self.map_data.records, list):
                raise ValueError("map_data.records 未定义或格式错误。")
            if not self.map_data.records:
                show_error_message(self, "属性表", "当前没有可用的属性表。请先导入 Shapefile。")
                return
            if not all(isinstance(record, dict) for record in self.map_data.records):
                raise ValueError("map_data.records 中存在非字典记录。")
            self.attribute_table_requested.emit(self.map_data.records)  # 发射属性表请求信号
        except Exception as e:
            logging.error(f"Error during opening attribute table: {e}")
            show_error_message(self, "属性表错误", f"打开属性表时发生错误:\n{e}")

    def export_to_png(self) -> None:
        """
        导出地图为 PNG 文件
        """
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出为 PNG", "", "PNG Files (*.png)", options=options)
        if file_path:
            try:
                rect = self.scene.itemsBoundingRect()  # 获取场景中所有项的边界矩形
                width, height = int(rect.width()), int(rect.height())
                if rect.isEmpty():
                    raise ValueError("场景内容为空，无法导出图像")
                if width <= 0 or height <= 0:
                    raise ValueError(f"场景矩形区域的尺寸无效: 宽度={width}, 高度={height}")
                max_size = 32767
                width = min(width, max_size)
                height = min(height, max_size)
                image = QImage(width, height, QImage.Format_ARGB32)
                image.fill(Qt.transparent)  # 填充透明色
                if image.isNull():
                    raise ValueError("创建的 QImage 对象为空")
                painter = QPainter(image)
                painter.scale(1, -1)  # 在垂直方向上翻转
                painter.translate(0, -height)
                self.scene.render(painter, QRectF(0, 0, width, height), rect)  # 将场景渲染到图像
                painter.end()
                if image.isNull():
                    raise ValueError("渲染后的 QImage 对象为空")
                image_writer = QImageWriter(file_path, b"PNG")
                if not image_writer.write(image):
                    error_string = image_writer.errorString()
                    raise IOError(f"无法保存图像到文件: {file_path}\n错误详情: {error_string}")
                QMessageBox.information(self, "导出成功", f"地图已成功导出到 {file_path}")
            except Exception as e:
                logging.error(f"导出地图失败: {e}")
                show_error_message(self, "导出错误", f"无法导出地图:\n{e}")

    def export_to_pdf(self) -> None:
        """
        导出地图为 PDF 文件
        """
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出为 PDF", "", "PDF Files (*.pdf)", options=options)
        if file_path:
            try:
                printer = QPrinter(QPrinter.HighResolution)  # 创建高分辨率打印机对象
                printer.setOutputFormat(QPrinter.PdfFormat)  # 设置输出格式为 PDF
                printer.setOutputFileName(file_path)  # 设置输出文件名
                painter = QPainter(printer)
                self.render(painter)  # 渲染场景到 PDF
                painter.end()
                QMessageBox.information(self, "导出成功", f"地图已成功导出到 {file_path}")
            except Exception as e:
                logging.error(f"导出地图失败: {e}")
                show_error_message(self, "导出错误", f"无法导出地图:\n{e}")

    def export_to_jpeg(self) -> None:
        """
        导出地图为 JPEG 文件
        """
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出为 JPEG", "", "JPEG Files (*.jpg;*.jpeg)", options=options)
        if file_path:
            try:
                rect = self.scene.itemsBoundingRect()  # 获取场景中所有项的边界矩形
                width, height = int(rect.width()), int(rect.height())
                if rect.isEmpty():
                    raise ValueError("场景内容为空，无法导出图像")
                if width <= 0 or height <= 0:
                    raise ValueError(f"场景矩形区域的尺寸无效: 宽度={width}, 高度={height}")
                max_size = 32767
                width = min(width, max_size)
                height = min(height, max_size)
                image = QImage(width, height, QImage.Format_ARGB32)
                image.fill(Qt.transparent)  # 填充透明色
                if image.isNull():
                    raise ValueError("创建的 QImage 对象为空")
                painter = QPainter(image)
                painter.scale(1, -1)  # 在垂直方向上翻转
                painter.translate(0, -height)
                self.scene.render(painter, QRectF(0, 0, width, height), rect)  # 将场景渲染到图像
                painter.end()
                if image.isNull():
                    raise ValueError("渲染后的 QImage 对象为空")
                image_writer = QImageWriter(file_path, b"JPEG")
                if not image_writer.write(image):
                    error_string = image_writer.errorString()
                    raise IOError(f"无法保存图像到文件: {file_path}\n错误详情: {error_string}")
                QMessageBox.information(self, "导出成功", f"地图已成功导出到 {file_path}")
            except Exception as e:
                logging.error(f"导出地图失败: {e}")
                show_error_message(self, "导出错误", f"无法导出地图:\n{e}")
