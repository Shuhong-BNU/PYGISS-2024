# core/mapData.py
# 功能：提供加载 Shapefile、处理地图投影和转换几何形状的功能

import shapefile
from shapely.geometry import shape
from shapely.ops import transform
from pyproj import Transformer, CRS
import logging

class MapData:
    def __init__(self):
        # 初始化 MapData 类，存储几何数据、属性数据和坐标参考系
        self.shapes = []  # 存储几何形状
        self.records = []  # 新增：用于存储属性数据
        self.crs = 'EPSG:4326'  # 默认坐标参考系
        self.transformer = None  # 转换器，初始为 None
        self.proj_string = 'EPSG:4326'  # 当前投影字符串，默认值为 WGS84

    def load_shapefile(self, filepath: str, encoding: str = 'utf-8') -> None:
        """
        加载 Shapefile 并存储几何和属性数据
        参数:
            filepath (str): Shapefile 文件路径
            encoding (str): 文件编码方式，默认为 'utf-8'
        """
        try:
            sf = shapefile.Reader(filepath, encoding=encoding)
            self.shapes = []  # 清空几何形状列表
            self.records = []  # 清空属性数据列表
            for shaperec in sf.iterShapeRecords():
                geom = shape(shaperec.shape.__geo_interface__)  # 获取几何形状
                self.shapes.append(geom)  # 添加几何到 shapes 列表
                self.records.append(shaperec.record.as_dict())  # 新增：存储属性数据
            # 获取 CRS 信息，假设使用 .prj 文件
            self.crs = self.get_crs_from_prj(filepath)
            self.proj_string = self.crs
            # 初始化转换器，从原始 CRS 到目标 CRS (初始为自身)
            self.transformer = Transformer.from_crs(self.crs, self.crs, always_xy=True)
            logging.info(f"Detected CRS: {self.crs}")
            logging.info(f"Total shapes to process: {len(self.shapes)}")
            logging.info(f"Imported {len(self.shapes)} features from shapefile.")
        except Exception as e:
            logging.error(f"Error loading shapefile: {e}")
            raise e

    def get_crs_from_prj(self, shapefile_path: str) -> str:
        """
        从 .prj 文件获取 CRS
        参数:
            shapefile_path (str): Shapefile 文件路径
        返回:
            str: 坐标参考系字符串，例如 'EPSG:4326'
        """
        prj_path = shapefile_path.replace('.shp', '.prj')
        try:
            with open(prj_path, 'r', encoding='utf-8') as prj_file:
                prj_text = prj_file.read()  # 读取 .prj 文件内容
                crs = CRS.from_wkt(prj_text)  # 从 WKT 中获取 CRS
                epsg = crs.to_epsg()  # 尝试转换为 EPSG 代码
                if epsg:
                    return f"EPSG:{epsg}"
                else:
                    logging.warning("CRS 未能解析为 EPSG 代码，使用默认 EPSG:4326。")
                    return 'EPSG:4326'
        except FileNotFoundError:
            logging.warning(f"未找到 .prj 文件: {prj_path}，使用默认 CRS: EPSG:4326。")
            return 'EPSG:4326'
        except Exception as e:
            logging.error(f"Error reading .prj file: {e}，使用默认 CRS: EPSG:4326。")
            return 'EPSG:4326'

    def change_projection(self, epsg_code: str) -> None:
        """
        更改地图投影
        参数:
            epsg_code (str): 目标 EPSG 代码
        """
        try:
            self.proj_string = epsg_code  # 更新投影字符串
            self.transformer = Transformer.from_crs(self.crs, self.proj_string, always_xy=True)  # 初始化转换器
            logging.info(f"Projection changed to: {self.proj_string}")
        except Exception as e:
            logging.error(f"Error changing projection: {e}")
            raise e

    def get_transformed_polygons(self) -> list:
        """
        获取转换后的多边形坐标列表
        返回:
            list: 包含所有转换后的多边形的坐标列表
        """
        transformed_polygons = []
        for geom in self.shapes:
            if geom.geom_type in ['Polygon', 'MultiPolygon']:
                transformed_geom = self.transform_geometry(geom)  # 转换几何形状
                if transformed_geom:
                    if transformed_geom.geom_type == 'Polygon':
                        transformed_polygons.append(list(transformed_geom.exterior.coords))  # 添加转换后的外部边界
                    elif transformed_geom.geom_type == 'MultiPolygon':
                        for poly in transformed_geom.geoms:
                            transformed_polygons.append(list(poly.exterior.coords))  # 添加每个多边形的外部边界
        return transformed_polygons

    def get_transformed_lines(self) -> list:
        """
        获取转换后的线坐标列表
        返回:
            list: 包含所有转换后的线的坐标列表
        """
        transformed_lines = []
        for geom in self.shapes:
            if geom.geom_type in ['LineString', 'MultiLineString']:
                transformed_geom = self.transform_geometry(geom)  # 转换几何形状
                if transformed_geom:
                    if transformed_geom.geom_type == 'LineString':
                        transformed_lines.append(list(transformed_geom.coords))  # 添加转换后的线坐标
                    elif transformed_geom.geom_type == 'MultiLineString':
                        for line in transformed_geom.geoms:
                            transformed_lines.append(list(line.coords))  # 添加每个子线的坐标
        return transformed_lines

    def transform_geometry(self, geom) -> shape:
        """
        将几何对象转换到当前投影
        参数:
            geom (shape): 要转换的几何对象
        返回:
            shape: 转换后的几何对象
        """
        try:
            transformed_geom = transform(self.transformer.transform, geom)  # 使用转换器转换几何对象
            return transformed_geom
        except Exception as e:
            logging.error(f"Error transforming geometry: {e}")
            return None

    def clear_map(self) -> None:
        """
        清除地图数据
        """
        self.shapes = []  # 清空几何形状列表
        self.records = []  # 清空属性数据列表
        self.transformer = Transformer.from_crs(self.crs, self.crs, always_xy=True)  # 重置转换器
        self.proj_string = self.crs  # 重置投影字符串
        logging.info("Map data cleared.")
