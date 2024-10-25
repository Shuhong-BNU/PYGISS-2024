# ui/mapWidget.py

from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtWidgets import (
    QGraphicsView, QGraphicsScene, QFileDialog, QVBoxLayout, QWidget, QLabel,
    QGraphicsPixmapItem, QGraphicsItem, QGraphicsPolygonItem, QLineEdit, QGraphicsSimpleTextItem,
    QHBoxLayout, QToolButton, QMessageBox
)
from PyQt5.QtGui import (
    QPainter, QPen, QPolygonF, QBrush, QPixmap, QIcon, QCursor, QColor,
    QPainterPath, QTransform, QImage, QImageWriter
)
from PyQt5.QtCore import Qt, QPointF, pyqtSignal, QRectF
import os
import logging
from core.mapData import MapData
from core.nodeData import NodeData
from utils.utils import is_valid_coordinate, show_error_message

class NodeItem(QGraphicsPixmapItem):
    """自定义节点项类，继承自 QGraphicsPixmapItem"""
    def __init__(self, pixmap, *args, **kwargs):
        super().__init__(pixmap, *args, **kwargs)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.setCursor(QCursor(Qt.PointingHandCursor))

class MapWidget(QGraphicsView):
    shapefile_imported = pyqtSignal()  # 当 Shapefile 导入成功时发出信号
    feature_selected = pyqtSignal(dict)  # 新增信号，当要素被选中时发射属性信息

    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window  # 保存主窗口对象
        self.scene = QGraphicsScene(self)  # 创建场景来展示地图和节点
        # 设置背景色为透明
        self.scene.setBackgroundBrush(Qt.transparent)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)  # 开启抗锯齿

        self.map_data = MapData()  # 地图数据类
        self.node_data = NodeData()  # 节点数据类

        self.default_pen_width = 0.01  # 默认线宽
        self.map_pen = QPen(Qt.black, self.default_pen_width)  # 地图边界的笔
        self.map_brush = QBrush(QColor(0, 100, 0))  # 深绿色填充色

        self.line_pen = QPen(Qt.blue, 1.5)  # 线的笔刷，用于 LineString
        self.line_brush = QBrush(Qt.NoBrush)  # 线的填充色

        self.node_scale_factor = 0.5  # 节点图片缩放比例，初始为 50%

        self.init_ui()  # 初始化界面

        # 拖拽相关变量
        self.is_panning = False  # 是否处于拖拽状态
        self.last_pan_point = QPointF()  # 上一次鼠标位置

        # 加载节点图片
        self.load_node_image()
        self.node_items = []  # 用于存储节点图片项
        self.polygon_items = []  # 用于存储多边形项

        # 更新笔的线宽
        self.update_pen_width()

        # 默认模式为平移模式
        self.set_drag_mode('pan')

        # 翻转 Y 轴，解决地图显示颠倒问题
        self.setTransform(QTransform().scale(1, -1))

        # 优化性能
        self.setCacheMode(QGraphicsView.CacheBackground)
        self.setViewportUpdateMode(QGraphicsView.BoundingRectViewportUpdate)
        self.setRenderHint(QPainter.Antialiasing)

        self.highlighted_items = []  # 用于存储高亮的要素

    def init_ui(self):
        """初始化界面和控件"""
        # 创建容器部件
        container = QWidget(self)
        container.setFixedWidth(100)
        container.setStyleSheet("background-color: rgba(255, 255, 255, 150);")

        layout = QVBoxLayout(container)
        layout.setContentsMargins(5, 5, 5, 5)

        # 添加按钮用于切换鼠标模式
        self.pan_button = QToolButton()
        self.pan_button.setIcon(QIcon(os.path.join(os.path.dirname(__file__), '..', 'images', 'hand_icon.png')))
        self.pan_button.setCheckable(True)
        self.pan_button.setChecked(True)  # 默认选中
        self.pan_button.clicked.connect(lambda: self.set_drag_mode('pan'))
        self.pan_button.setToolTip("Pan Mode")

        self.select_button = QToolButton()
        self.select_button.setIcon(QIcon(os.path.join(os.path.dirname(__file__), '..', 'images', 'arrow_icon.png')))
        self.select_button.setCheckable(True)
        self.select_button.clicked.connect(lambda: self.set_drag_mode('select'))
        self.select_button.setToolTip("Select Mode")

        # 将按钮添加到布局
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.pan_button)
        button_layout.addWidget(self.select_button)
        layout.addLayout(button_layout)

        # 添加提示标签
        self.hint_label = QLabel("使用按钮切换模式")
        layout.addWidget(self.hint_label)

        # 将容器放置在左上角
        container.move(10, 10)

    def set_drag_mode(self, mode):
        """设置鼠标拖拽模式"""
        if mode == 'pan':
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self.pan_button.setChecked(True)
            self.select_button.setChecked(False)
            self.setCursor(Qt.OpenHandCursor)
        elif mode == 'select':
            self.setDragMode(QGraphicsView.RubberBandDrag)
            self.pan_button.setChecked(False)
            self.select_button.setChecked(True)
            self.setCursor(Qt.ArrowCursor)

    def load_node_image(self):
        """加载节点图片"""
        # 获取当前文件所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 构建相对路径
        image_path = os.path.join(current_dir, '..', 'images', 'OIP-C.jpg')
        # 加载图片
        self.node_pixmap_original = QPixmap(image_path)
        if self.node_pixmap_original.isNull():
            logging.warning(f"Failed to load node image from {image_path}. Using default red dot.")
            # 使用默认的节点符号，例如一个小圆点
            self.node_pixmap_original = QPixmap(10, 10)
            self.node_pixmap_original.fill(Qt.red)
        else:
            logging.info(f"Node image loaded from {image_path}")

        # 初始节点图片
        self.node_pixmap = self.node_pixmap_original.scaled(
            self.node_pixmap_original.size() * self.node_scale_factor,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

    def resizeEvent(self, event):
        """窗口大小改变时调整控件位置"""
        super().resizeEvent(event)
        container = self.findChild(QWidget)  # 查找容器
        if container:
            container.move(10, 10)  # 重新定位到左上角

    def wheelEvent(self, event):
        """鼠标滚轮缩放视图"""
        zoom_in_factor = 1.25  # 放大因子
        zoom_out_factor = 1 / zoom_in_factor  # 缩小因子

        old_pos = self.mapToScene(event.pos())  # 记录鼠标位置

        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor  # 放大
        else:
            zoom_factor = zoom_out_factor  # 缩小

        self.scale(zoom_factor, zoom_factor)  # 缩放

        new_pos = self.mapToScene(event.pos())  # 新的场景位置

        delta = new_pos - old_pos  # 计算位置差

        self.translate(delta.x(), delta.y())  # 平移视图

    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            if self.dragMode() == QGraphicsView.RubberBandDrag:
                super().mousePressEvent(event)
            else:
                # 获取点击位置的场景坐标
                scene_pos = self.mapToScene(event.pos())
                # 获取点击位置的项
                item = self.scene.itemAt(scene_pos, self.transform())
                if isinstance(item, QGraphicsPolygonItem):
                    # 高亮显示选中的要素
                    self.highlight_feature(item)
                    # 发射信号，传递属性信息
                    self.feature_selected.emit(item.attributes)
                else:
                    # 如果未点击到要素，取消高亮
                    self.clear_highlights()
                self.is_panning = True
                self.last_pan_point = event.pos()
                self.setCursor(Qt.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if self.is_panning:
            delta = event.pos() - self.last_pan_point
            self.last_pan_point = event.pos()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.LeftButton:
            self.is_panning = False
            self.setCursor(Qt.ArrowCursor)
        super().mouseReleaseEvent(event)

    def import_shapefile(self):
        """导入 Shapefile 并绘制地图"""
        options = QFileDialog.Options()
        filepath, _ = QFileDialog.getOpenFileName(self, "Open Shapefile", "", "Shapefiles (*.shp)", options=options)
        if filepath:
            logging.info(f"Importing shapefile: {filepath}")
            try:
                # 使用正确的方法加载 Shapefile
                self.map_data.load_shapefile(filepath, encoding='utf-8')  # 修改部分：将 import_map 替换为 load_shapefile
            except UnicodeDecodeError:
                logging.warning("Failed to decode with utf-8, trying gbk encoding.")
                try:
                    self.map_data.load_shapefile(filepath, encoding='gbk')  # 修改部分
                except Exception as e:
                    logging.exception("Failed to import shapefile with gbk encoding.")
                    show_error_message(self, "导入错误", f"无法导入 Shapefile:\n{e}")
                    return
            except Exception as e:
                logging.exception("Failed to import shapefile.")
                show_error_message(self, "导入错误", f"无法导入 Shapefile:\n{e}")
                return

            try:
                self.draw_map()
                self.shapefile_imported.emit()
                logging.info("Shapefile imported, enabling Import Nodes button.")
            except Exception as e:
                logging.exception("Failed to draw map after importing shapefile.")
                show_error_message(self, "绘制错误", f"导入 Shapefile 后绘制地图时出错:\n{e}")
        else:
            logging.info("No shapefile selected.")

    def import_nodes(self):
        """导入节点文件并绘制节点"""
        options = QFileDialog.Options()
        filepath, _ = QFileDialog.getOpenFileName(self, "Open Nodes File", "", "Excel Files (*.xls *.xlsx)", options=options)
        if filepath:
            logging.info(f"Importing nodes from: {filepath}")
            try:
                self.node_data.import_nodes(filepath)
                self.node_data.set_projection(self.map_data.crs, self.map_data.proj_string)
                self.draw_nodes()
            except Exception as e:
                logging.exception("导入节点时发生错误")
                show_error_message(self, "导入错误", f"无法导入节点:\n{e}")
        else:
            logging.info("No nodes file selected.")

    def draw_map(self):
        """绘制地图形状"""
        self.scene.clear()
        self.node_items.clear()
        self.polygon_items.clear()  # 清空多边形项列表
        self.highlighted_items.clear()  # 清空高亮的要素列表

        # 绘制投影范围内的海洋背景
        self.draw_ocean_background()

        # 绘制多边形
        transformed_polygons = self.map_data.get_transformed_polygons()
        logging.info(f"Drawing {len(transformed_polygons)} polygons.")
        for index, coords in enumerate(transformed_polygons):
            valid_coords = []
            for point in coords:
                if is_valid_coordinate(point[0], point[1]):
                    valid_coords.append(QPointF(point[0], point[1]))
            if len(valid_coords) >= 3:
                polygon = QPolygonF(valid_coords)
                # 创建多边形项，设置填充色和边框色
                polygon_item = QGraphicsPolygonItem(polygon)
                polygon_item.setPen(QPen(Qt.black, self.map_pen.widthF(), Qt.SolidLine))
                polygon_item.setBrush(QBrush(QColor(0, 100, 0)))  # 深绿色
                polygon_item.setZValue(1)  # 确保陆地显示在海洋背景之上
                # 保存属性信息
                if index < len(self.map_data.records):
                    polygon_item.attributes = self.map_data.records[index]
                else:
                    polygon_item.attributes = {}
                # 使多边形项可选择
                polygon_item.setFlag(QGraphicsItem.ItemIsSelectable, True)
                # 添加到场景和列表
                self.scene.addItem(polygon_item)
                self.polygon_items.append(polygon_item)
            else:
                logging.warning("Not enough valid points to form a polygon.")

        # 绘制线
        transformed_lines = self.map_data.get_transformed_lines()
        logging.info(f"Drawing {len(transformed_lines)} lines.")
        for coords in transformed_lines:
            valid_coords = []
            for point in coords:
                if is_valid_coordinate(point[0], point[1]):
                    valid_coords.append(QPointF(point[0], point[1]))
            if len(valid_coords) >= 2:
                path = QPainterPath()
                path.moveTo(valid_coords[0])
                for point in valid_coords[1:]:
                    path.lineTo(point)
                # 使用 addPath 方法绘制线
                line_item = self.scene.addPath(path, QPen(Qt.blue, self.line_pen.widthF(), Qt.SolidLine))
                line_item.setZValue(1)  # 确保线显示在海洋背景之上
            else:
                logging.warning("Not enough valid points to form a line.")

        # 绘制行政边界线
        self.draw_administrative_boundaries()

        # 绘制节点
        self.draw_nodes()

        # 调整场景边界
        self.scene.setSceneRect(self.scene.itemsBoundingRect())

        # 绘制投影范围的边框
        self.draw_projection_boundary()

        # 适应视图到场景
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def draw_ocean_background(self):
        """绘制投影范围内的海洋背景"""
        # 设置海洋颜色为深蓝色
        ocean_brush = QBrush(QColor(0, 105, 148))  # 深蓝色
        projection_extent = self.get_projection_extent()

        if projection_extent:
            if self.is_circular_projection():
                # 绘制圆形海洋背景
                center = projection_extent.center()
                radius = min(projection_extent.width(), projection_extent.height()) / 2
                ellipse_rect = QRectF(center.x() - radius, center.y() - radius, 2 * radius, 2 * radius)
                ocean_item = self.scene.addEllipse(ellipse_rect, QPen(Qt.NoPen), ocean_brush)
            else:
                # 绘制矩形海洋背景
                ocean_item = self.scene.addRect(projection_extent, QPen(Qt.NoPen), ocean_brush)
            ocean_item.setZValue(0)  # 确保海洋背景在最底层

    def get_projection_extent(self):
        """获取投影后的地图范围，并添加缓冲区以确保海洋区域可见"""
        transformed_polygons = self.map_data.get_transformed_polygons()
        transformed_lines = self.map_data.get_transformed_lines()
        all_coords = [coord for shape in transformed_polygons for coord in shape] + \
                    [coord for shape in transformed_lines for coord in shape]
        if not all_coords:
            return None
        try:
            min_x = min([point[0] for point in all_coords])
            max_x = max([point[0] for point in all_coords])
            min_y = min([point[1] for point in all_coords])
            max_y = max([point[1] for point in all_coords])

            # 添加缓冲区（0.1%）
            buffer_x = (max_x - min_x) * 0.001
            buffer_y = (max_y - min_y) * 0.001
            min_x -= buffer_x
            max_x += buffer_x
            min_y -= buffer_y
            max_y += buffer_y

            return QRectF(min_x, min_y, max_x - min_x, max_y - min_y)
        except Exception as e:
            logging.error(f"Error calculating projection extent: {e}")
            return None

    def is_circular_projection(self):
        """判断当前投影是否为圆形范围"""
        circular_epsg_codes = ['EPSG:3571']  # 仅包含 EPSG:3571
        is_circular = self.map_data.proj_string in circular_epsg_codes
        logging.info(f"Is circular projection: {is_circular}")
        return is_circular

    def draw_projection_boundary(self):
        """绘制投影范围的边框"""
        boundary_pen = QPen(Qt.black)
        boundary_pen.setWidthF(2.0)
        projection_extent = self.get_projection_extent()

        if projection_extent:
            if self.is_circular_projection():
                # 绘制圆形边框
                center = projection_extent.center()
                radius = min(projection_extent.width(), projection_extent.height()) / 2
                ellipse_rect = QRectF(center.x() - radius, center.y() - radius, 2 * radius, 2 * radius)
                boundary_item = self.scene.addEllipse(ellipse_rect, boundary_pen)
            else:
                # 绘制矩形边框
                boundary_item = self.scene.addRect(projection_extent, boundary_pen)
            boundary_item.setZValue(3)  # 确保边框在行政边界线之上

    def draw_administrative_boundaries(self):
        """绘制行政边界线"""
        transformed_polygons = self.map_data.get_transformed_polygons()
        logging.info(f"Drawing administrative boundaries.")

        for coords in transformed_polygons:
            valid_coords = []
            for point in coords:
                if is_valid_coordinate(point[0], point[1]):
                    valid_coords.append(QPointF(point[0], point[1]))
            if len(valid_coords) >= 3:
                path = QPainterPath()
                path.moveTo(valid_coords[0])
                for point in valid_coords[1:]:
                    path.lineTo(point)
                path.closeSubpath()
                try:
                    boundary_item = self.scene.addPath(path, QPen(Qt.black, 0.2, Qt.SolidLine))  # 边界线为黑色实线
                    boundary_item.setZValue(3)  # 设置更高的 Z 值，确保在多边形之上
                except Exception as e:
                    logging.error(f"Failed to draw administrative boundary: {e}")
            else:
                logging.warning("Not enough valid points to form a boundary.")

    def draw_nodes(self):
        """绘制节点"""
        if not self.node_data.nodes:
            return

        # 在绘制新的节点之前，先清除之前的节点图片项
        for item in self.node_items:
            self.scene.removeItem(item)
        self.node_items.clear()

        transformed_nodes = self.node_data.get_transformed_nodes()
        logging.info(f"Drawing {len(transformed_nodes)} nodes.")
        for x, y in transformed_nodes:
            if is_valid_coordinate(x, y):
                # 创建自定义的节点项
                node_item = NodeItem(self.node_pixmap)
                # 设置图片中心在节点位置
                node_item.setOffset(-self.node_pixmap.width() / 2, -self.node_pixmap.height() / 2)
                node_item.setPos(x, y)
                # 设置图片不随视图缩放而改变大小
                node_item.setFlag(QGraphicsItem.ItemIgnoresTransformations, True)
                # 设置节点的 Z 值，使其显示在地图之上
                node_item.setZValue(4)  # 设置更高的 Z 值
                # 添加到场景
                self.scene.addItem(node_item)
                # 将节点项添加到列表中
                self.node_items.append(node_item)
            else:
                logging.warning(f"Invalid node coordinates: ({x}, {y})")

    def change_projection(self, new_proj):
        """更改投影并重新绘制地图和节点"""
        try:
            logging.info(f"Changing projection to: {new_proj}")
            # 提取 EPSG 代码
            epsg_code = new_proj.split(' - ')[0]
            self.map_data.change_projection(epsg_code)
            # 更新节点数据的投影转换器
            self.node_data.set_projection(self.map_data.crs, self.map_data.proj_string)
            # 更新笔的线宽
            self.update_pen_width()
            # 重新绘制地图
            self.draw_map()
        except Exception as e:
            logging.error(f"Failed to change projection: {e}")
            show_error_message(self, "投影错误", f"无法更改地图投影:\n{e}")

    def update_pen_width(self):
        """根据当前的投影更新地图笔的线宽"""
        if self.map_data.proj_string and self.map_data.proj_string.lower() == 'epsg:4326':
            # 将线宽缩小为原来的四分之一
            self.map_pen.setWidthF(self.default_pen_width * 0.25)
            self.line_pen.setWidthF(0.75)  # 调整线宽
        elif self.map_data.proj_string in ['EPSG:3035', 'EPSG:3395', 'EPSG:3571']:
            # 指定投影下，保持较宽的线宽
            self.map_pen.setWidthF(2.0)
            self.line_pen.setWidthF(2.0)
        else:
            # 对于其他投影，将线宽缩小为原来的三分之一
            self.map_pen.setWidthF(self.default_pen_width / 3)
            self.line_pen.setWidthF(1.5 / 3)  # 目前为 0.5

    def delete_map(self):
        """删除地图和节点"""
        logging.info("Deleting map and nodes.")
        self.scene.clear()
        self.map_data.clear_map()
        self.node_data.clear_nodes()
        self.node_items.clear()  # 清除节点图片项列表
        self.polygon_items.clear()  # 清除多边形项列表
        self.highlighted_items.clear()  # 清除高亮的要素列表

    def update_node_size(self, value):
        """更新节点图片尺寸并重新绘制节点"""
        self.node_scale_factor = value / 100.0  # 将百分比转换为比例
        logging.info(f"Node scale factor updated to: {self.node_scale_factor}")
        # 重新生成缩放后的节点图片
        self.node_pixmap = self.node_pixmap_original.scaled(
            self.node_pixmap_original.size() * self.node_scale_factor,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        # 重新绘制节点
        self.draw_nodes()

    def delete_selected_nodes(self):
        """删除选中的节点"""
        logging.info("Deleting selected nodes.")
        selected_items = self.scene.selectedItems()
        for item in selected_items:
            if item in self.node_items:
                self.scene.removeItem(item)
                self.node_items.remove(item)

    def export_to_png(self, file_path):
        """导出地图为 PNG 文件"""
        try:
            # 获取当前场景的矩形区域
            rect = self.scene.itemsBoundingRect()
            width, height = int(rect.width()), int(rect.height())

            # 检查场景内容
            if rect.isEmpty():
                raise ValueError("场景内容为空，无法导出图像")

            # 检查矩形区域的尺寸
            if width <= 0 or height <= 0:
                raise ValueError(f"场景矩形区域的尺寸无效: 宽度={width}, 高度={height}")

            # 限制图像尺寸，避免超出QImage的处理范围
            max_size = 32767  # QImage的最大尺寸限制
            width = min(width, max_size)
            height = min(height, max_size)

            # 创建一个 QImage 对象来保存渲染结果
            image = QImage(width, height, QImage.Format_ARGB32)
            image.fill(Qt.transparent)
            # 检查图像大小
            if image.isNull():
                raise ValueError("创建的 QImage 对象为空")
            # 使用 QPainter 将场景内容渲染到 QImage 上
            painter = QPainter(image)
            # 反转Y轴：否则导出的图像是倒的
            painter.scale(1, -1)
            painter.translate(0, -height)
            #开始渲染场景
            self.scene.render(painter, QRectF(0, 0, width, height), rect)
            painter.end()
            # 检查渲染结果
            if image.isNull():
                raise ValueError("渲染后的 QImage 对象为空")
            # 使用 QImageWriter 保存图像
            image_writer = QImageWriter(file_path, b"PNG")
            if not image_writer.write(image):
                error_string = image_writer.errorString()
                raise IOError(f"无法保存图像到文件: {file_path}\n错误详情: {error_string}")

        except Exception as e:
            logging.error(f"导出地图失败: {e}")
            raise e  # 重新抛出异常，以便上层捕获

    def export_to_pdf(self, file_path):
        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(file_path)
        painter = QPainter(printer)
        self.render(painter)
        painter.end()

    def export_to_jpeg(self, file_path):
        """导出地图为 JPEG 文件"""
        try:
            # 获取当前场景的矩形区域
            rect = self.scene.itemsBoundingRect()
            width, height = int(rect.width()), int(rect.height())

            # 检查场景内容
            if rect.isEmpty():
                raise ValueError("场景内容为空，无法导出图像")

            # 检查矩形区域的尺寸
            if width <= 0 or height <= 0:
                raise ValueError(f"场景矩形区域的尺寸无效: 宽度={width}, 高度={height}")

            # 限制图像尺寸，避免超出QImage的处理范围
            max_size = 32767  # QImage的最大尺寸限制
            width = min(width, max_size)
            height = min(height, max_size)

            # 创建一个 QImage 对象来保存渲染结果
            image = QImage(width, height, QImage.Format_ARGB32)
            image.fill(Qt.transparent)

            # 检查图像大小
            if image.isNull():
                raise ValueError("创建的 QImage 对象为空")

            # 使用 QPainter 将场景内容渲染到 QImage 上
            painter = QPainter(image)
            # 反转Y轴：否则导出的图像是倒的
            painter.scale(1, -1)
            painter.translate(0, -height)
            # 开始渲染场景
            self.scene.render(painter, QRectF(0, 0, width, height), rect)
            painter.end()

            # 检查渲染结果
            if image.isNull():
                raise ValueError("渲染后的 QImage 对象为空")

            # 使用 QImageWriter 保存图像
            image_writer = QImageWriter(file_path, b"JPEG")
            if not image_writer.write(image):
                error_string = image_writer.errorString()
                raise IOError(f"无法保存图像到文件: {file_path}\n错误详情: {error_string}")

        except Exception as e:
            logging.error(f"导出地图失败: {e}")
            raise e  # 重新抛出异常，以便上层捕获

    def export_to_jpg(self, file_path):
        """导出地图为 JPG 文件"""
        try:
            # 获取当前场景的矩形区域
            rect = self.scene.itemsBoundingRect()
            width, height = int(rect.width()), int(rect.height())

            # 检查场景内容
            if rect.isEmpty():
                raise ValueError("场景内容为空，无法导出图像")

            # 检查矩形区域的尺寸
            if width <= 0 or height <= 0:
                raise ValueError(f"场景矩形区域的尺寸无效: 宽度={width}, 高度={height}")

            # 限制图像尺寸，避免超出QImage的处理范围
            max_size = 32767  # QImage的最大尺寸限制
            width = min(width, max_size)
            height = min(height, max_size)

            # 创建一个 QImage 对象来保存渲染结果
            image = QImage(width, height, QImage.Format_ARGB32)
            image.fill(Qt.transparent)

            # 检查图像大小
            if image.isNull():
                raise ValueError("创建的 QImage 对象为空")

            # 使用 QPainter 将场景内容渲染到 QImage 上
            painter = QPainter(image)
            # 反转Y轴：否则导出的图像是倒的
            painter.scale(1, -1)
            painter.translate(0, -height)
            # 开始渲染场景
            self.scene.render(painter, QRectF(0, 0, width, height), rect)
            painter.end()

            # 检查渲染结果
            if image.isNull():
                raise ValueError("渲染后的 QImage 对象为空")

            # 使用 QImageWriter 保存图像
            image_writer = QImageWriter(file_path, b"JPG")
            if not image_writer.write(image):
                error_string = image_writer.errorString()
                raise IOError(f"无法保存图像到文件: {file_path}\n错误详情: {error_string}")

        except Exception as e:
            logging.error(f"导出地图失败: {e}")
            raise e  # 重新抛出异常，以便上层捕获

    def highlight_feature(self, item):
        """高亮显示选中的要素"""
        # 清除之前的高亮
        self.clear_highlights()
        # 设置高亮样式
        item.setBrush(QBrush(QColor(255, 0, 0, 100)))  # 半透明红色
        self.highlighted_items.append(item)

    def clear_highlights(self):
        """清除高亮显示"""
        for item in self.highlighted_items:
            item.setBrush(QBrush(QColor(0, 100, 0)))  # 恢复原始颜色
        self.highlighted_items.clear()

    def perform_attribute_query(self, field, value):
        """执行属性查询并高亮符合条件的要素"""
        matching_items = []
        for item in self.polygon_items:
            if field in item.attributes and str(item.attributes[field]) == value:
                matching_items.append(item)
        if matching_items:
            # 清除之前的高亮
            self.clear_highlights()
            # 高亮所有符合条件的要素
            for item in matching_items:
                item.setBrush(QBrush(QColor(255, 255, 0, 100)))  # 半透明黄色
                self.highlighted_items.append(item)
            return matching_items
        else:
            self.clear_highlights()
            return []
