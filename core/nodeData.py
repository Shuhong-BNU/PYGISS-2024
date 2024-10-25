# core/nodeData.py

import pandas as pd
from shapely.geometry import Point
from pyproj import Transformer
import logging

class NodeData:
    def __init__(self):
        self.nodes = []
        self.transformer = None
        self.proj_string = 'EPSG:4326'  # 默认投影

    def import_nodes(self, filepath):
        """导入节点数据（Excel 文件）"""
        try:
            df = pd.read_excel(filepath)
            self.nodes = []
            for _, row in df.iterrows():
                x, y = row['Longitude'], row['Latitude']  # 假设 Excel 有 Longitude 和 Latitude 列
                self.nodes.append((x, y))
            logging.info(f"Imported {len(self.nodes)} nodes from {filepath}.")
        except Exception as e:
            logging.error(f"Error importing nodes: {e}")
            raise e

    def set_projection(self, input_crs, target_crs):
        """设置节点数据的投影转换器"""
        try:
            self.proj_string = target_crs
            self.transformer = Transformer.from_crs(input_crs, self.proj_string, always_xy=True)
            logging.info(f"Node projection set to: {self.proj_string}")
        except Exception as e:
            logging.error(f"Error setting node projection: {e}")
            raise e

    def get_transformed_nodes(self):
        """获取转换后的节点坐标列表"""
        transformed_nodes = []
        for x, y in self.nodes:
            try:
                transformed_x, transformed_y = self.transformer.transform(x, y)
                transformed_nodes.append((transformed_x, transformed_y))
            except Exception as e:
                logging.error(f"Error transforming node ({x}, {y}): {e}")
        return transformed_nodes

    def clear_nodes(self):
        """清除节点数据"""
        self.nodes = []
        logging.info("Node data cleared.")
