# ui/mapWidget_components/layerManager.py
# 功能：提供图层管理功能，包括导入 Shapefile、节点和更改地图投影的功能

from PyQt5.QtWidgets import QFileDialog
import logging
from utils.utils import show_error_message

class LayerManagerMixin:
    def import_shapefile(self) -> None:
        """
        导入 Shapefile 并绘制地图
        """
        options = QFileDialog.Options()
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Open Shapefile", "", "Shapefiles (*.shp)", options=options)
        if filepath:
            logging.info(f"Importing shapefile: {filepath}")
            try:
                self.map_data.load_shapefile(filepath, encoding='utf-8')  # 尝试以 utf-8 编码加载
            except UnicodeDecodeError:
                logging.warning("Failed to decode with utf-8, trying gbk encoding.")
                try:
                    self.map_data.load_shapefile(filepath, encoding='gbk')  # 尝试以 gbk 编码加载
                except Exception as e:
                    logging.exception("Failed to import shapefile with gbk encoding.")
                    show_error_message(self, "导入错误", f"无法导入 Shapefile:\n{e}")
                    return
            except Exception as e:
                logging.exception("Failed to import shapefile.")
                show_error_message(self, "导入错误", f"无法导入 Shapefile:\n{e}")
                return

            try:
                self.update_pen_width()  # 更新线宽
                self.draw_map()  # 绘制地图
                self.shapefile_imported.emit()  # 发射导入完成信号
                logging.info("Shapefile imported, enabling Import Nodes button.")
            except Exception as e:
                logging.exception("Failed to draw map after importing shapefile.")
                show_error_message(self, "绘制错误", f"导入 Shapefile 后绘制地图时出错:\n{e}")
        else:
            logging.info("No shapefile selected.")

    def import_nodes(self) -> None:
        """
        导入节点文件并绘制节点
        """
        options = QFileDialog.Options()
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Open Nodes File", "", "Excel Files (*.xls *.xlsx)",
            options=options)
        if filepath:
            logging.info(f"Importing nodes from: {filepath}")
            try:
                self.node_data.import_nodes(filepath)  # 导入节点数据
                self.node_data.set_projection(self.map_data.crs, self.map_data.proj_string)  # 设置节点投影
                self.draw_nodes()  # 绘制节点
            except Exception as e:
                logging.exception("导入节点时发生错误")
                show_error_message(self, "导入错误", f"无法导入节点:\n{e}")
        else:
            logging.info("No nodes file selected.")

    def change_projection(self, new_proj: str) -> None:
        """
        更改投影并重新绘制地图和节点
        参数:
            new_proj (str): 新的投影字符串，例如 'EPSG:4326'
        """
        try:
            logging.info(f"Changing projection to: {new_proj}")
            epsg_code = new_proj.split(' - ')[0]  # 获取 EPSG 代码
            self.map_data.change_projection(epsg_code)  # 更改地图投影
            self.node_data.set_projection(self.map_data.crs, self.map_data.proj_string)  # 更新节点投影
            self.update_pen_width()  # 更新线宽
            self.draw_map()  # 重新绘制地图
            self.draw_nodes()  # 重新绘制节点
        except Exception as e:
            logging.error(f"Failed to change projection: {e}")
            show_error_message(self, "投影错误", f"无法更改地图投影:\n{e}")

    def delete_map(self) -> None:
        """
        删除地图和节点
        """
        logging.info("Deleting map and nodes.")
        # 清除地图项
        for item in self.polygon_items:
            self.scene.removeItem(item)
        self.polygon_items.clear()
        # 清除节点项
        for item in self.node_items:
            self.scene.removeItem(item)
        self.node_items.clear()
        # 清除其他项
        if hasattr(self, 'ocean_item') and self.ocean_item:
            self.scene.removeItem(self.ocean_item)
            self.ocean_item = None
        if hasattr(self, 'boundary_item') and self.boundary_item:
            self.scene.removeItem(self.boundary_item)
            self.boundary_item = None
        if hasattr(self, 'boundary_items') and self.boundary_items:
            for item in self.boundary_items:
                self.scene.removeItem(item)
            self.boundary_items.clear()
        self.highlighted_items.clear()  # 清空高亮项
        self.map_data.clear_map()  # 清空地图数据
        self.node_data.clear_nodes()  # 清空节点数据
