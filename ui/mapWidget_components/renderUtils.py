# ui/mapWidget_components/renderUtils.py
# 功能：提供地图渲染的工具方法，包括场景设置、节点图片加载和地图范围计算等功能

from PyQt5.QtGui import QPixmap, QTransform, QPen, QBrush, QColor
from PyQt5.QtWidgets import QGraphicsItem
from PyQt5.QtCore import QRectF, Qt
import logging
import os
from core.mapData import MapData
from core.nodeData import NodeData
from utils.utils import is_valid_coordinate

class RenderUtilsMixin:
    def setup_scene(self) -> None:
        """
        初始化场景和基本设置
        """
        # 使用 MapWidget 中的 scene
        self.map_data = MapData()  # 创建 MapData 对象，存储地图数据
        self.node_data = NodeData()  # 创建 NodeData 对象，存储节点数据
        self.default_pen_width = 0.01  # 设置默认笔刷宽度
        self.map_pen = QPen(Qt.black, self.default_pen_width)  # 初始化地图边框笔刷
        self.map_brush = QBrush(QColor(0, 100, 0))  # 设置地图填充颜色
        self.line_pen = QPen(Qt.blue, 1.5)  # 初始化线的笔刷
        self.line_brush = QBrush(Qt.NoBrush)  # 线不填充颜色
        self.node_scale_factor = 0.5  # 设置节点缩放因子
        self.node_items = []  # 存储节点项
        self.polygon_items = []  # 存储多边形项
        self.highlighted_items = []  # 存储高亮项
        self.ocean_item = None  # 存储海洋项
        self.boundary_item = None  # 存储边界项
        self.boundary_items = []  # 存储边界项列表

    def load_node_image(self) -> None:
        """
        加载节点图片
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))  # 获取当前文件所在目录
        image_path = os.path.join(current_dir, '..', '..', 'images', 'OIP-C.jpg')  # 获取图片路径
        self.node_pixmap_original = QPixmap(image_path)  # 加载节点图片
        if self.node_pixmap_original.isNull():
            logging.warning(f"Failed to load node image from {image_path}. Using default red dot.")
            self.node_pixmap_original = QPixmap(10, 10)  # 创建默认红点图片
            self.node_pixmap_original.fill(Qt.red)  # 填充红色
        else:
            logging.info(f"Node image loaded from {image_path}")
        self.node_pixmap = self.node_pixmap_original.scaled(
            self.node_pixmap_original.size() * self.node_scale_factor,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )  # 缩放节点图片

    def get_projection_extent(self) -> QRectF:
        """
        获取投影后的地图范围
        返回:
            QRectF: 包含所有多边形和线的最小边界矩形
        """
        transformed_polygons = self.map_data.get_transformed_polygons()  # 获取转换后的多边形
        transformed_lines = self.map_data.get_transformed_lines()  # 获取转换后的线
        all_coords = [coord for shape in transformed_polygons for coord in shape] + [coord for shape in transformed_lines for coord in shape]
        if not all_coords:
            return None
        try:
            min_x = min([point[0] for point in all_coords])  # 获取最小 x 坐标
            max_x = max([point[0] for point in all_coords])  # 获取最大 x 坐标
            min_y = min([point[1] for point in all_coords])  # 获取最小 y 坐标
            max_y = max([point[1] for point in all_coords])  # 获取最大 y 坐标
            buffer_x = (max_x - min_x) * 0.001  # x 方向添加缓冲
            buffer_y = (max_y - min_y) * 0.001  # y 方向添加缓冲
            min_x -= buffer_x
            max_x += buffer_x
            min_y -= buffer_y
            max_y += buffer_y
            return QRectF(min_x, min_y, max_x - min_x, max_y - min_y)  # 返回矩形范围
        except Exception as e:
            logging.error(f"Error calculating projection extent: {e}")
            return None

    def is_circular_projection(self) -> bool:
        """
        判断当前投影是否为圆形范围
        返回:
            bool: 如果是圆形投影则返回 True，否则返回 False
        """
        circular_epsg_codes = ['EPSG:3571']  # 定义圆形投影的 EPSG 代码列表
        is_circular = self.map_data.proj_string in circular_epsg_codes  # 判断当前投影是否在列表中
        logging.info(f"Is circular projection: {is_circular}")
        return is_circular

    def update_node_size(self, value: int) -> None:
        """
        更新节点图片尺寸并重新绘制节点
        参数:
            value (int): 新的节点尺寸百分比
        """
        self.node_scale_factor = value / 100.0  # 计算新的节点缩放因子
        logging.info(f"Node scale factor updated to: {self.node_scale_factor}")
        self.node_pixmap = self.node_pixmap_original.scaled(
            self.node_pixmap_original.size() * self.node_scale_factor,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )  # 缩放节点图片
        self.draw_nodes()  # 重新绘制节点
