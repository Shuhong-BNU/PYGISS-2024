# ui/menu.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QComboBox, QGroupBox, QGridLayout,
    QLabel, QSlider, QMessageBox, QMenu, QAction, QLineEdit
)
from PyQt5.QtCore import pyqtSignal, Qt

class TGISMenu(QWidget):
    # 定义所有需要的信号
    import_shapefile_clicked = pyqtSignal()
    import_nodes_clicked = pyqtSignal()
    projection_changed = pyqtSignal(str)
    delete_map_clicked = pyqtSignal()
    delete_selected_nodes_clicked = pyqtSignal()
    node_size_changed = pyqtSignal(int)  # 用于节点图片尺寸调整
    export_to_png_clicked = pyqtSignal()  # 新增信号-导出为png
    export_to_pdf_clicked = pyqtSignal()  # 新增信号-导出为pdf
    export_format_changed = pyqtSignal(str)  # 用于选择文件格式
    attribute_query_clicked = pyqtSignal(str, str)  # 新增信号，用于属性查询

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayout(QVBoxLayout())

        # 当前坐标系显示
        self.current_projection_label = QLabel("Current Coordinate System: ")
        self.layout().addWidget(self.current_projection_label)

        # 对象管理部分
        self.object_management = QGroupBox("Object Management")
        self.object_management.setLayout(QGridLayout())
        self.layout().addWidget(self.object_management)

        self.import_shapefile_button = QPushButton("Import Shapefile")
        self.import_shapefile_button.clicked.connect(self.import_shapefile_clicked.emit)
        self.object_management.layout().addWidget(self.import_shapefile_button, 0, 0)

        self.import_nodes_button = QPushButton("Import Nodes")
        self.import_nodes_button.clicked.connect(self.import_nodes_clicked.emit)
        self.import_nodes_button.setEnabled(False)  # 默认禁用
        self.object_management.layout().addWidget(self.import_nodes_button, 1, 0)

        # 投影管理部分
        self.projection_management = QGroupBox("Projection Management")
        self.projection_management.setLayout(QGridLayout())
        self.layout().addWidget(self.projection_management)

        self.projection_list = QComboBox()
        self.projection_list.addItems([
            "EPSG:4326 - WGS84",
            "EPSG:4490 - CGCS2000 (China)",
            "EPSG:3571 - North Pole LAEA Alaska",
            "EPSG:3035 - ETRS89 / LAEA Europe",
            "EPSG:3395 - WGS 84 / World Mercator",
            "EPSG:32649 - WGS 84 / UTM zone 49N",
            "EPSG:4214 - Beijing 1954",
        ])
        self.projection_management.layout().addWidget(self.projection_list, 0, 0)

        change_projection_button = QPushButton("Change Projection")
        change_projection_button.clicked.connect(self.on_change_projection)
        self.projection_management.layout().addWidget(change_projection_button, 1, 0)

        # 地图管理部分
        self.map_management = QGroupBox("Map Management")
        self.map_management.setLayout(QGridLayout())
        self.layout().addWidget(self.map_management)

        delete_map_button = QPushButton("Delete Map")
        delete_map_button.clicked.connect(self.delete_map_clicked.emit)
        self.map_management.layout().addWidget(delete_map_button, 0, 0)

        delete_selection_button = QPushButton("Delete Selected Nodes")
        delete_selection_button.clicked.connect(self.delete_selected_nodes_clicked.emit)
        self.map_management.layout().addWidget(delete_selection_button, 1, 0)

        # 导出部分
        self.export_group_box = QGroupBox("Output View")
        self.export_group_box.setLayout(QGridLayout())
        self.layout().addWidget(self.export_group_box)

        # 添加新的 QComboBox 用以选择文件格式
        self.export_format_combo = QComboBox()
        self.export_format_combo.addItems(["PDF", "PNG", "JPG", "JPEG"])
        self.export_format_combo.currentIndexChanged.connect(self.on_export_format_changed)

        # 将 QComboBox 添加到 Export 框的布局中
        self.export_group_box.layout().addWidget(self.export_format_combo, 0, 0)

        # 节点图片尺寸调整部分
        self.node_size_management = QGroupBox("Node Size Adjustment")
        self.node_size_management.setLayout(QVBoxLayout())
        self.layout().addWidget(self.node_size_management)

        self.node_size_label = QLabel("Node Size: 50%")
        self.node_size_management.layout().addWidget(self.node_size_label)

        self.node_size_slider = QSlider(Qt.Horizontal)
        self.node_size_slider.setMinimum(10)
        self.node_size_slider.setMaximum(200)
        self.node_size_slider.setValue(50)
        self.node_size_slider.setTickInterval(10)
        self.node_size_slider.setTickPosition(QSlider.TicksBelow)
        self.node_size_slider.valueChanged.connect(self.on_node_size_changed)
        self.node_size_management.layout().addWidget(self.node_size_slider)

        # 添加属性查询部分
        self.query_group_box = QGroupBox("Attribute Query")
        self.query_group_box.setLayout(QGridLayout())
        self.layout().addWidget(self.query_group_box)

        self.field_label = QLabel("Field:")
        self.query_group_box.layout().addWidget(self.field_label, 0, 0)
        self.field_input = QLineEdit()
        self.query_group_box.layout().addWidget(self.field_input, 0, 1)

        self.value_label = QLabel("Value:")
        self.query_group_box.layout().addWidget(self.value_label, 1, 0)
        self.value_input = QLineEdit()
        self.query_group_box.layout().addWidget(self.value_input, 1, 1)

        self.query_button = QPushButton("Query")
        self.query_button.clicked.connect(self.on_attribute_query)
        self.query_group_box.layout().addWidget(self.query_button, 2, 0, 1, 2)

    def on_change_projection(self):
        projection = self.projection_list.currentText()
        self.projection_changed.emit(projection)
        self.current_projection_label.setText(f"Current Coordinate System: {projection}")

    def disable_buttons(self):
        """禁用所有按钮"""
        self.import_shapefile_button.setEnabled(False)
        self.import_nodes_button.setEnabled(False)
        # 禁用其他按钮（如有）

    def enable_buttons(self):
        """启用所有按钮"""
        self.import_shapefile_button.setEnabled(True)
        self.import_nodes_button.setEnabled(True)
        # 启用其他按钮（如有）

    def on_node_size_changed(self, value):
        """当滑动条的值变化时，更新标签并发射信号"""
        self.node_size_label.setText(f"Node Size: {value}%")
        self.node_size_changed.emit(value)

    def on_export_format_changed(self, index):
        """当导出格式发生变化时，发射信号"""
        format = self.export_format_combo.itemText(index)
        self.export_format_changed.emit(format)

    def on_attribute_query(self):
        field = self.field_input.text()
        value = self.value_input.text()
        if field and value:
            self.attribute_query_clicked.emit(field, value)
        else:
            QMessageBox.warning(self, "Input Error", "Please enter both field and value.")
