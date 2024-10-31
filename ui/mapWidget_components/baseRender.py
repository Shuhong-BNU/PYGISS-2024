# ui/mapWidget_components/baseRender.py
# 功能：提供地图形状、多边形和线的绘制功能，包括背景和边界绘制

from PyQt5.QtGui import QPen, QBrush, QColor, QPolygonF, QPainterPath, QPixmap
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsPolygonItem, QGraphicsPixmapItem
from PyQt5.QtCore import QPointF, QRectF, Qt
import logging
from utils.utils import is_valid_coordinate, show_error_message

class CustomPolygonItem(QGraphicsPolygonItem):
    """
    自定义多边形项，确保每个项都有 attributes 属性
    """
    def __init__(self, polygon: QPolygonF, attributes: dict, *args, **kwargs):
        super().__init__(polygon, *args, **kwargs)
        self.attributes = attributes  # 存储多边形属性
        self.setPen(QPen(Qt.black, 0.01))  # 设置边框笔刷
        self.setBrush(QBrush(QColor(0, 100, 0)))  # 设置填充颜色
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)  # 设置多边形可选中

class NodeItem(QGraphicsPixmapItem):
    """
    自定义节点项类，继承自 QGraphicsPixmapItem
    """
    def __init__(self, pixmap: QPixmap, *args, **kwargs):
        super().__init__(pixmap, *args, **kwargs)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)  # 设置节点可选中
        self.setFlag(QGraphicsItem.ItemIsMovable, False)  # 禁止节点移动
        self.setCursor(Qt.PointingHandCursor)  # 设置鼠标指针样式

class BaseRenderMixin:
    def draw_map(self) -> None:
        """
        绘制地图形状
        """
        # 不再清空整个场景，只清除地图相关的项
        for item in self.polygon_items:
            self.scene.removeItem(item)  # 从场景中移除多边形项
        self.polygon_items.clear()  # 清空多边形项列表
        self.highlighted_items.clear()  # 清空高亮项列表

        self.draw_ocean_background()  # 绘制海洋背景

        transformed_polygons = self.map_data.get_transformed_polygons()  # 获取转换后的多边形
        logging.info(f"Drawing {len(transformed_polygons)} polygons.")

        for index, coords in enumerate(transformed_polygons):
            valid_coords = []
            for point in coords:
                if is_valid_coordinate(point[0], point[1]):
                    valid_coords.append(QPointF(point[0], point[1]))  # 验证并添加有效坐标
            if len(valid_coords) >= 3:
                polygon = QPolygonF(valid_coords)  # 创建多边形
                attributes = self.map_data.records[index] if index < len(self.map_data.records) else {}
                polygon_item = CustomPolygonItem(polygon, attributes)  # 创建自定义多边形项
                polygon_item.setZValue(1)  # 设置 Z 值，控制绘制顺序
                self.scene.addItem(polygon_item)  # 添加到场景中
                self.polygon_items.append(polygon_item)  # 添加到多边形项列表
            else:
                logging.warning("Not enough valid points to form a polygon.")

        transformed_lines = self.map_data.get_transformed_lines()  # 获取转换后的线
        logging.info(f"Drawing {len(transformed_lines)} lines.")

        for coords in transformed_lines:
            valid_coords = []
            for point in coords:
                if is_valid_coordinate(point[0], point[1]):
                    valid_coords.append(QPointF(point[0], point[1]))  # 验证并添加有效坐标
            if len(valid_coords) >= 2:
                path = QPainterPath()
                path.moveTo(valid_coords[0])  # 起点
                for point in valid_coords[1:]:
                    path.lineTo(point)  # 连接线段
                line_item = self.scene.addPath(
                    path, QPen(Qt.blue, self.line_pen.widthF(), Qt.SolidLine))  # 创建并添加线项
                line_item.setZValue(1)  # 设置 Z 值
            else:
                logging.warning("Not enough valid points to form a line.")

        self.draw_administrative_boundaries()  # 绘制行政边界
        self.scene.setSceneRect(self.scene.itemsBoundingRect())  # 更新场景边界
        self.draw_projection_boundary()  # 绘制投影边界
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)  # 调整视图以适应场景

    def draw_ocean_background(self) -> None:
        """
        绘制投影范围内的海洋背景
        """
        # 清除之前的海洋背景
        if hasattr(self, 'ocean_item') and self.ocean_item:
            self.scene.removeItem(self.ocean_item)
        ocean_brush = QBrush(QColor(0, 105, 148))  # 设置海洋颜色
        projection_extent = self.get_projection_extent()  # 获取投影范围
        if projection_extent:
            if self.is_circular_projection():
                center = projection_extent.center()
                radius = min(projection_extent.width(), projection_extent.height()) / 2
                ellipse_rect = QRectF(center.x() - radius, center.y() - radius, 2 * radius, 2 * radius)
                self.ocean_item = self.scene.addEllipse(
                    ellipse_rect, QPen(Qt.NoPen), ocean_brush)  # 绘制圆形背景
            else:
                self.ocean_item = self.scene.addRect(
                    projection_extent, QPen(Qt.NoPen), ocean_brush)  # 绘制矩形背景
            self.ocean_item.setZValue(0)  # 设置 Z 值

    def draw_projection_boundary(self) -> None:
        """
        绘制投影范围的边框
        """
        # 清除之前的边框
        if hasattr(self, 'boundary_item') and self.boundary_item:
            self.scene.removeItem(self.boundary_item)
        boundary_pen = QPen(Qt.black)
        boundary_pen.setWidthF(2.0)  # 设置边框宽度
        projection_extent = self.get_projection_extent()  # 获取投影范围
        if projection_extent:
            if self.is_circular_projection():
                center = projection_extent.center()
                radius = min(projection_extent.width(), projection_extent.height()) / 2
                ellipse_rect = QRectF(center.x() - radius, center.y() - radius, 2 * radius, 2 * radius)
                self.boundary_item = self.scene.addEllipse(ellipse_rect, boundary_pen)  # 绘制圆形边框
            else:
                self.boundary_item = self.scene.addRect(projection_extent, boundary_pen)  # 绘制矩形边框
            self.boundary_item.setZValue(3)  # 设置 Z 值

    def draw_administrative_boundaries(self) -> None:
        """
        绘制行政边界线
        """
        # 清除之前的行政边界
        if hasattr(self, 'boundary_items') and self.boundary_items:
            for item in self.boundary_items:
                self.scene.removeItem(item)
            self.boundary_items.clear()
        else:
            self.boundary_items = []
        transformed_polygons = self.map_data.get_transformed_polygons()  # 获取转换后的多边形
        logging.info(f"Drawing administrative boundaries.")
        for coords in transformed_polygons:
            valid_coords = []
            for point in coords:
                if is_valid_coordinate(point[0], point[1]):
                    valid_coords.append(QPointF(point[0], point[1]))  # 验证并添加有效坐标
            if len(valid_coords) >= 3:
                path = QPainterPath()
                path.moveTo(valid_coords[0])
                for point in valid_coords[1:]:
                    path.lineTo(point)  # 连接多边形的每个点
                path.closeSubpath()  # 闭合路径
                try:
                    boundary_item = self.scene.addPath(
                        path, QPen(Qt.black, 0.2, Qt.SolidLine))  # 创建并添加边界项
                    boundary_item.setZValue(3)  # 设置 Z 值
                    self.boundary_items.append(boundary_item)  # 添加到边界项列表
                except Exception as e:
                    logging.error(f"Failed to draw administrative boundary: {e}")
            else:
                logging.warning("Not enough valid points to form a boundary.")

    def draw_nodes(self) -> None:
        """
        绘制节点
        """
        if not self.node_data.nodes:
            return
        # 清除之前的节点项
        for item in self.node_items:
            self.scene.removeItem(item)
        self.node_items.clear()
        transformed_nodes = self.node_data.get_transformed_nodes()  # 获取转换后的节点
        logging.info(f"Drawing {len(transformed_nodes)} nodes.")
        try:
            for x, y in transformed_nodes:
                if is_valid_coordinate(x, y):
                    node_item = NodeItem(self.node_pixmap)  # 创建节点项
                    node_item.setOffset(-self.node_pixmap.width() / 2, -self.node_pixmap.height() / 2)  # 设置偏移
                    node_item.setPos(x, y)  # 设置节点位置
                    node_item.setFlag(QGraphicsItem.ItemIgnoresTransformations, True)  # 设置忽略变换
                    node_item.setZValue(4)  # 设置 Z 值
                    self.scene.addItem(node_item)  # 添加到场景中
                    self.node_items.append(node_item)  # 添加到节点项列表
                else:
                    logging.warning(f"Invalid node coordinates: ({x}, {y})")
        except Exception as e:
            logging.error(f"Error while drawing nodes: {e}")
            show_error_message(self, "绘制节点错误", f"绘制节点时发生错误:\n{e}")

    def update_pen_width(self) -> None:
        """
        根据当前的投影更新地图笔的线宽
        """
        if self.map_data.proj_string and self.map_data.proj_string.lower() == 'epsg:4326':
            self.map_pen.setWidthF(self.default_pen_width * 0.25)  # 设置线宽
            self.line_pen.setWidthF(0.75)
        elif self.map_data.proj_string in ['EPSG:3035', 'EPSG:3395', 'EPSG:3571']:
            self.map_pen.setWidthF(2.0)
            self.line_pen.setWidthF(2.0)
        else:
            self.map_pen.setWidthF(self.default_pen_width / 3)
            self.line_pen.setWidthF(1.5 / 3)
