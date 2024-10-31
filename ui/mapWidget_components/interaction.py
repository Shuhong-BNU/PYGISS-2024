# ui/mapWidget_components/interaction.py
# 功能：提供与地图交互的功能，包括拖拽、缩放和选择等操作

from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPen
from PyQt5.QtWidgets import QGraphicsView
import logging
from utils.utils import show_error_message
from ui.mapWidget_components.baseRender import CustomPolygonItem

class InteractionMixin:
    def set_drag_mode(self, mode: str) -> None:
        """
        设置鼠标拖拽模式
        参数:
            mode (str): 拖拽模式，'pan' 或 'select'
        """
        if mode == 'pan':
            self.setDragMode(QGraphicsView.NoDrag)  # 设置为无拖动模式
            self.pan_button.setChecked(True)
            self.select_button.setChecked(False)
            self.setCursor(Qt.OpenHandCursor)  # 设置鼠标光标为打开的手形
        elif mode == 'select':
            self.setDragMode(QGraphicsView.NoDrag)
            self.pan_button.setChecked(False)
            self.select_button.setChecked(True)
            self.setCursor(Qt.ArrowCursor)  # 设置鼠标光标为箭头

    def wheelEvent(self, event) -> None:
        """
        鼠标滚轮缩放视图
        """
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor
        old_pos = self.mapToScene(event.pos())  # 记录缩放前的位置
        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor  # 放大
        else:
            zoom_factor = zoom_out_factor  # 缩小
        self.scale(zoom_factor, zoom_factor)  # 进行缩放
        new_pos = self.mapToScene(event.pos())  # 记录缩放后的新位置
        delta = new_pos - old_pos  # 计算位置偏移量
        self.translate(delta.x(), delta.y())  # 将视图平移以保持原位置

    def mousePressEvent(self, event) -> None:
        """
        鼠标按下事件
        """
        if event.button() == Qt.LeftButton:
            if self.select_button.isChecked():
                scene_pos = self.mapToScene(event.pos())  # 获取场景坐标
                items = self.scene.items(QPointF(scene_pos))  # 获取点击位置的项
                try:
                    for item in items:
                        if isinstance(item, CustomPolygonItem):
                            self.clear_highlights()  # 清除之前的高亮
                            self.highlight_feature(item)  # 高亮选中的要素
                            self.display_feature_attributes(item.attributes)  # 显示选中要素的属性
                            break
                    else:
                        # 未找到匹配的要素
                        self.clear_highlights()
                        self.display_feature_attributes(None)
                except Exception as e:
                    logging.error(f"Error during feature selection: {e}")
                    show_error_message(self, "选择错误", f"选择要素时发生错误:\n{e}")
                event.accept()
            else:
                self.is_panning = True  # 开始平移
                self.last_pan_point = event.pos()  # 记录平移起点
                self.setCursor(Qt.ClosedHandCursor)  # 设置鼠标光标为闭合的手形
                event.accept()
        else:
            QGraphicsView.mousePressEvent(self, event)  # 调用父类方法

    def mouseMoveEvent(self, event) -> None:
        """
        鼠标移动事件
        """
        if self.is_panning:
            delta = event.pos() - self.last_pan_point  # 计算移动的位移
            self.last_pan_point = event.pos()  # 更新最后平移点
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - delta.x())  # 平移水平滚动条
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - delta.y())  # 平移垂直滚动条
            event.accept()
        else:
            QGraphicsView.mouseMoveEvent(self, event)  # 调用父类方法

    def mouseReleaseEvent(self, event) -> None:
        """
        鼠标释放事件
        """
        if event.button() == Qt.LeftButton:
            if self.select_button.isChecked():
                self.is_panning = False  # 停止平移
                event.accept()
            elif self.is_panning:
                self.is_panning = False
                self.setCursor(Qt.OpenHandCursor)  # 恢复鼠标光标为打开的手形
                event.accept()
            else:
                QGraphicsView.mouseReleaseEvent(self, event)  # 调用父类方法
        else:
            QGraphicsView.mouseReleaseEvent(self, event)  # 调用父类方法

    def highlight_feature(self, item: CustomPolygonItem) -> None:
        """
        高亮显示选中的要素
        参数:
            item (CustomPolygonItem): 要高亮的多边形项
        """
        try:
            # 清除之前的高亮
            self.clear_highlights()
            # 保存原始的 Pen
            if hasattr(item, 'original_pen'):
                return  # 已经高亮，不需要再次处理
            item.original_pen = item.pen()  # 保存当前的笔刷
            # 创建高亮的 Pen
            highlighted_pen = QPen(Qt.red, item.pen().widthF() * 2)  # 设置高亮颜色和线宽
            item.setPen(highlighted_pen)  # 应用高亮笔刷
            self.highlighted_items.append(item)  # 添加到高亮项列表
        except Exception as e:
            logging.error(f"Error during feature highlighting: {e}")
            show_error_message(self, "高亮错误", f"高亮要素时发生错误:\n{e}")

    def clear_highlights(self) -> None:
        """
        清除高亮显示
        """
        try:
            for item in self.highlighted_items:
                if hasattr(item, 'original_pen'):
                    item.setPen(item.original_pen)  # 恢复原始笔刷
                    del item.original_pen  # 删除保存的原始笔刷
            self.highlighted_items.clear()  # 清空高亮项列表
        except Exception as e:
            logging.error(f"Error during clearing highlights: {e}")
            show_error_message(self, "清除高亮错误", f"清除高亮时发生错误:\n{e}")

    def delete_selected_nodes(self) -> None:
        """
        删除选中的节点
        """
        logging.info("Deleting selected nodes.")
        selected_items = self.scene.selectedItems()  # 获取选中的项
        for item in selected_items:
            if item in self.node_items:
                self.scene.removeItem(item)  # 从场景中移除节点项
                self.node_items.remove(item)  # 从节点项列表中移除

    def display_feature_attributes(self, attributes: dict) -> None:
        """
        显示要素的属性信息
        参数:
            attributes (dict): 要素的属性字典
        """
        self.feature_attributes_updated.emit(attributes)  # 发射信号以更新属性信息