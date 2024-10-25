# core/mapData.py

import shapefile
from shapely.geometry import shape
from shapely.ops import transform
from pyproj import Transformer, CRS
import logging

class MapData:
    def __init__(self):
        self.shapes = []
        self.records = []  # 用于存储属性数据
        self.crs = 'EPSG:4326'  # 默认坐标参考系
        self.transformer = None
        self.proj_string = 'EPSG:4326'  # 当前投影字符串

    def load_shapefile(self, filepath, encoding='utf-8'):
        """加载 Shapefile 并存储几何和属性数据"""
        try:
            sf = shapefile.Reader(filepath, encoding=encoding)
            self.shapes = []
            self.records = []  # 清空属性数据
            for shaperec in sf.iterShapeRecords():
                geom = shape(shaperec.shape.__geo_interface__)
                self.shapes.append(geom)
                self.records.append(shaperec.record.as_dict())  # 获取属性数据
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

    def get_crs_from_prj(self, shapefile_path):
        """从 .prj 文件获取 CRS"""
        prj_path = shapefile_path.replace('.shp', '.prj')
        try:
            with open(prj_path, 'r', encoding='utf-8') as prj_file:
                prj_text = prj_file.read()
                crs = CRS.from_wkt(prj_text)
                epsg = crs.to_epsg()
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

    def change_projection(self, epsg_code):
        """更改地图投影"""
        try:
            self.proj_string = epsg_code
            self.transformer = Transformer.from_crs(self.crs, self.proj_string, always_xy=True)
            logging.info(f"Projection changed to: {self.proj_string}")
        except Exception as e:
            logging.error(f"Error changing projection: {e}")
            raise e

    def get_transformed_polygons(self):
        """获取转换后的多边形坐标列表"""
        transformed_polygons = []
        for geom in self.shapes:
            if geom.geom_type in ['Polygon', 'MultiPolygon']:
                transformed_geom = self.transform_geometry(geom)
                if transformed_geom:
                    if transformed_geom.geom_type == 'Polygon':
                        transformed_polygons.append(list(transformed_geom.exterior.coords))
                    elif transformed_geom.geom_type == 'MultiPolygon':
                        for poly in transformed_geom.geoms:
                            transformed_polygons.append(list(poly.exterior.coords))
        return transformed_polygons

    def get_transformed_lines(self):
        """获取转换后的线坐标列表"""
        transformed_lines = []
        for geom in self.shapes:
            if geom.geom_type in ['LineString', 'MultiLineString']:
                transformed_geom = self.transform_geometry(geom)
                if transformed_geom:
                    if transformed_geom.geom_type == 'LineString':
                        transformed_lines.append(list(transformed_geom.coords))
                    elif transformed_geom.geom_type == 'MultiLineString':
                        for line in transformed_geom.geoms:
                            transformed_lines.append(list(line.coords))
        return transformed_lines
###
dd

#

