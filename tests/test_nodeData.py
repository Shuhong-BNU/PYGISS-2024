# test_nodeData.py

import pytest
import os
from core.nodeData import NodeData


# 更新路径构造函数
def get_test_file_path(*path_segments):
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'pyGISS-1029 -8 - final'))
    return os.path.join(project_root, *path_segments)


def test_import_nodes():
    node_data = NodeData()
    node_file_path = get_test_file_path("tests", "data", "french cities.xls")

    # 检查文件路径
    print("Constructed node file path:", node_file_path)
    assert os.path.exists(node_file_path), f"Node file not found: {node_file_path}"

    node_data.import_nodes(node_file_path)
    assert len(node_data.nodes) > 0


def test_set_projection():
    node_data = NodeData()
    node_file_path = get_test_file_path("tests", "data", "french cities.xls")

    # 检查文件路径
    print("Constructed node file path:", node_file_path)
    assert os.path.exists(node_file_path), f"Node file not found: {node_file_path}"

    node_data.import_nodes(node_file_path)
    node_data.set_projection("EPSG:4326", "EPSG:3395")  # 从 WGS84 转换到墨卡托
    assert node_data.proj_string == "EPSG:3395"


def test_clear_nodes():
    node_data = NodeData()
    node_file_path = get_test_file_path("tests", "data", "french cities.xls")

    # 检查文件路径
    print("Constructed node file path:", node_file_path)
    assert os.path.exists(node_file_path), f"Node file not found: {node_file_path}"

    node_data.import_nodes(node_file_path)
    node_data.clear_nodes()
    assert len(node_data.nodes) == 0
