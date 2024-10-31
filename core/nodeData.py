# core/nodeData.py
# 功能：提供加载节点数据、处理投影和获取转换后的节点坐标的功能

import pandas as pd
from shapely.geometry import Point
from pyproj import Transformer
import logging

class NodeData:
    def __init__(self):
        # 初始化 NodeData 类，存储节点数据和投影信息
        self.nodes = []  # 存储节点坐标
        self.transformer = None  # 转换器，初始为 None
        self.proj_string = 'EPSG:4326'  # 默认投影字符串，默认值为 WGS84

    def import_nodes(self, filepath: str) -> None:
        """
        导入节点数据（Excel 文件）
        参数:
            filepath (str): Excel 文件路径，假设文件中有 Longitude 和 Latitude 列
        """
        try:
            df = pd.read_excel(filepath)  # 读取 Excel 文件
            self.nodes = []  # 清空节点列表
            for _, row in df.iterrows():
                x, y = row['Longitude'], row['Latitude']  # 获取经纬度坐标
                self.nodes.append((x, y))  # 添加到节点列表
            logging.info(f"Imported {len(self.nodes)} nodes from {filepath}.")
        except Exception as e:
            logging.error(f"Error importing nodes: {e}")
            raise e

    def set_projection(self, input_crs: str, target_crs: str) -> None:
        """
        设置节点数据的投影转换器
        参数:
            input_crs (str): 输入坐标参考系
            target_crs (str): 目标坐标参考系
        """
        try:
            self.proj_string = target_crs  # 更新投影字符串
            self.transformer = Transformer.from_crs(input_crs, self.proj_string, always_xy=True)  # 初始化转换器
            logging.info(f"Node projection set to: {self.proj_string}")
        except Exception as e:
            logging.error(f"Error setting node projection: {e}")
            raise e

    def get_transformed_nodes(self) -> list:
        """
        获取转换后的节点坐标列表
        返回:
            list: 包含所有转换后的节点坐标列表
        """
        transformed_nodes = []
        for x, y in self.nodes:
            try:
                transformed_x, transformed_y = self.transformer.transform(x, y)  # 转换节点坐标
                transformed_nodes.append((transformed_x, transformed_y))  # 添加转换后的坐标
            except Exception as e:
                logging.error(f"Error transforming node ({x}, {y}): {e}")
        return transformed_nodes

    def clear_nodes(self) -> None:
        """
        清除节点数据
        """
        self.nodes = []  # 清空节点列表
        logging.info("Node data cleared.")