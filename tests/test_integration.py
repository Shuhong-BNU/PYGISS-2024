# test_integration.py

import os
import pytest
from core.mapData import MapData
from core.nodeData import NodeData
from ui.mapWidget import MapWidget
from PyQt5.QtWidgets import QApplication

app = QApplication([])  # 创建应用程序实例


def test_full_workflow():
    # 获取当前脚本文件的绝对路径，然后上移两级，获取项目的根目录
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'pyGISS-1029 -8 - final'))

    # 使用项目根路径构建 shapefile 和节点文件的路径
    shapefile_path = os.path.join(project_root, "tests", "data", "ne_50m_admin_0_countries.shp")
    node_file_path = os.path.join(project_root, "tests", "data", "french cities.xls")

    # 输出路径检查
    print("Shapefile path:", shapefile_path)
    print("Node file path:", node_file_path)

    # 检查所有关联文件是否存在
    assert os.path.exists(shapefile_path), f"Shapefile (.shp) not found: {shapefile_path}"
    assert os.path.exists(node_file_path), f"Node file (.xls) not found: {node_file_path}"
    assert os.path.exists(shapefile_path.replace('.shp', '.dbf')), "Associated .dbf file not found"
    assert os.path.exists(shapefile_path.replace('.shp', '.shx')), "Associated .shx file not found"

    # 测试地图加载和投影转换的完整流程
    map_data = MapData()
    map_data.load_shapefile(shapefile_path)
    map_data.change_projection("EPSG:3035")
    assert len(map_data.shapes) > 0
    assert map_data.proj_string == "EPSG:3035"

    # 测试节点加载和投影
    node_data = NodeData()
    node_data.import_nodes(node_file_path)
    node_data.set_projection("EPSG:4326", "EPSG:3035")
    transformed_nodes = node_data.get_transformed_nodes()
    assert len(transformed_nodes) > 0

    # 测试 UI 集成
    widget = MapWidget(None)
    widget.map_data = map_data
    widget.node_data = node_data
    widget.draw_map()  # 绘制地图
    assert widget.scene is not None
