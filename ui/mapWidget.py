# ui/mapWidget.py
# 功能：实现地图小部件类，包括与菜单的交互和地图操作功能

from PyQt5.QtWidgets import (
    QGraphicsView, QWidget, QVBoxLayout, QLabel, QToolButton, QHBoxLayout,
    QPushButton, QGraphicsScene, QGraphicsItem
)
from PyQt5.QtGui import QIcon, QTransform, QPainter, QPainterPath, QPen
from PyQt5.QtCore import pyqtSignal, Qt, QRectF
from ui.mapWidget_components.render import RenderMixin
from ui.mapWidget_components.interaction import InteractionMixin
from ui.mapWidget_components.tools import ToolsMixin
import os
import logging


class MapWidget(QGraphicsView, RenderMixin, InteractionMixin, ToolsMixin):
    shapefile_imported = pyqtSignal()  # 信号：Shapefile 文件导入完成
    attribute_table_requested = pyqtSignal(list)  # 信号：请求属性表
    feature_attributes_updated = pyqtSignal(dict)  # 信号：要素属性更新

    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window
        self.scene = QGraphicsScene(self)  # 创建场景对象
        self.setScene(self.scene)  # 将场景设置为视图的场景
        self.setRenderHint(QPainter.Antialiasing)  # 启用抗锯齿
        self.init_ui()  # 初始化用户界面
        self.setup_scene()  # 初始化场景
        self.load_node_image()  # 加载节点图片
        self.is_panning = False  # 是否处于平移模式
        self.last_pan_point = None  # 记录平移起点
        self.set_drag_mode('pan')  # 设置默认拖拽模式
        self.setTransform(QTransform().scale(1, -1))  # 翻转 Y 轴
        self.highlighted_items = []  # 初始化高亮项列表

    def init_ui(self) -> None:
        """
        初始化界面和控件
        """
        container = QWidget(self)  # 创建控件容器
        container.setFixedWidth(100)  # 设置固定宽度
        container.setStyleSheet("background-color: rgba(255, 255, 255, 150);")  # 设置背景颜色
        layout = QVBoxLayout(container)  # 垂直布局
        layout.setContentsMargins(5, 5, 5, 5)

        # 平移按钮
        self.pan_button = QToolButton()
        self.pan_button.setIcon(QIcon(os.path.join(
            os.path.dirname(__file__), '..', 'images', 'hand_icon.png')))
        self.pan_button.setCheckable(True)
        self.pan_button.setChecked(True)
        self.pan_button.clicked.connect(lambda: self.set_drag_mode('pan'))
        self.pan_button.setToolTip("Pan Mode")

        # 选择按钮
        self.select_button = QToolButton()
        self.select_button.setIcon(QIcon(os.path.join(
            os.path.dirname(__file__), '..', 'images', 'arrow_icon.png')))
        self.select_button.setCheckable(True)
        self.select_button.clicked.connect(lambda: self.set_drag_mode('select'))
        self.select_button.setToolTip("Select Mode")

        # 添加按钮到布局
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.pan_button)
        button_layout.addWidget(self.select_button)
        layout.addLayout(button_layout)

        # 属性表按钮
        self.show_attribute_table_button = QPushButton("显示属性表")
        self.show_attribute_table_button.clicked.connect(self.open_attribute_table)
        layout.addWidget(self.show_attribute_table_button)

        # 提示标签
        self.hint_label = QLabel("使用按钮切换模式")
        layout.addWidget(self.hint_label)

        container.move(10, 10)  # 设置控件容器的位置

    def resizeEvent(self, event) -> None:
        """
        窗口大小改变时调整控件位置
        """
        super().resizeEvent(event)
        container = self.findChild(QWidget)
        if container:
            container.move(10, 10)

    def highlight_feature(self, item) -> None:
        """
        高亮显示选中的要素
        参数:
            item: 要高亮的项
        """
        try:
            # 清除之前的高亮
            self.clear_highlights()
            # 保存原始的 Pen
            if hasattr(item, 'original_pen'):
                return  # 已经高亮，不需要再次处理
            item.original_pen = item.pen() if hasattr(item, 'pen') else None
            # 创建高亮的 Pen
            highlighted_pen = QPen(Qt.red, 2.0)
            if hasattr(item, 'setPen'):
                item.setPen(highlighted_pen)
            self.highlighted_items.append(item)
        except Exception as e:
            logging.error(f"Error during feature highlighting: {e}")

    def clear_highlights(self) -> None:
        """
        清除高亮显示
        """
        try:
            for item in self.highlighted_items:
                if hasattr(item, 'original_pen') and item.original_pen is not None:
                    if hasattr(item, 'setPen'):
                        item.setPen(item.original_pen)
                    del item.original_pen
            self.highlighted_items.clear()
        except Exception as e:
            logging.error(f"Error during clearing highlights: {e}")

    def display_feature_attributes(self, attributes: dict) -> None:
        """
        显示要素的属性信息
        参数:
            attributes (dict): 要素的属性字典
        """
        if attributes is None:
            attributes = {}  # 确保属性字典不为 None
        self.feature_attributes_updated.emit(attributes)  # 发射信号以更新属性信息

    def mousePressEvent(self, event) -> None:
        """
        鼠标按下事件，用于选择多个要素
        参数:
            event: 鼠标事件对象
        """
        if event.button() == Qt.LeftButton and self.select_button.isChecked():
            self.selection_start = self.mapToScene(event.pos())
        elif event.button() == Qt.MiddleButton or (event.button() == Qt.LeftButton and self.pan_button.isChecked()):
            # 支持中键拖拽和平移按钮拖拽
            self.is_panning = True
            self.last_pan_point = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        """
        鼠标移动事件，用于处理拖拽
        参数:
            event: 鼠标事件对象
        """
        if self.is_panning and self.last_pan_point is not None:
            delta = event.pos() - self.last_pan_point
            self.last_pan_point = event.pos()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        """
        鼠标释放事件，用于处理矩形选择框
        参数:
            event: 鼠标事件对象
        """
        if event.button() == Qt.LeftButton and self.select_button.isChecked():
            selection_end = self.mapToScene(event.pos())
            selection_rect = QRectF(self.selection_start, selection_end).normalized()
            selected_items = self.scene.items(selection_rect, Qt.IntersectsItemShape)

            self.clear_highlights()
            selected_features = []
            for item in selected_items:
                if isinstance(item, QGraphicsItem):
                    self.highlight_feature(item)
                    if hasattr(item, 'attributes'):
                        selected_features.append(item.attributes)

            if selected_features:
                self.feature_attributes_updated.emit(selected_features[0])  # 发射第一个选中要素的属性
            else:
                self.feature_attributes_updated.emit({})
        elif event.button() == Qt.MiddleButton or (event.button() == Qt.LeftButton and self.pan_button.isChecked()):
            # 结束平移
            self.is_panning = False
            self.setCursor(Qt.OpenHandCursor)
        super().mouseReleaseEvent(event)
