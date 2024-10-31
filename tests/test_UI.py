# test_UI.py

import pytest
import os
from PyQt5.QtWidgets import QApplication
from ui.mapWidget import MapWidget
from core.mapData import MapData
from core.nodeData import NodeData

app = QApplication([])  # 创建应用程序实例


# Helper function to construct paths based on the test directory
def get_test_file_path(*path_parts):
    # Get the directory of the current test file
    test_dir = os.path.dirname(__file__)
    # Join the directory with the provided path parts
    return os.path.abspath(os.path.join(test_dir, *path_parts))


def test_import_shapefile():
    widget = MapWidget(None)
    widget.map_data = MapData()
    shapefile_path = get_test_file_path("data", "ne_50m_admin_0_countries.shp")

    # Check if the shapefile exists
    print("Constructed shapefile path:", shapefile_path)
    assert os.path.exists(shapefile_path), f"Shapefile not found: {shapefile_path}"

    widget.map_data.load_shapefile(shapefile_path)
    assert len(widget.map_data.shapes) > 0


def test_import_nodes():
    widget = MapWidget(None)
    widget.node_data = NodeData()
    node_file_path = get_test_file_path("data", "french cities.xls")

    # Check if the node file exists
    print("Constructed node file path:", node_file_path)
    assert os.path.exists(node_file_path), f"Node file not found: {node_file_path}"

    widget.node_data.import_nodes(node_file_path)
    assert len(widget.node_data.nodes) > 0


def test_projection_change():
    widget = MapWidget(None)
    widget.map_data = MapData()
    shapefile_path = get_test_file_path("data", "ne_50m_admin_0_countries.shp")

    # Check if the shapefile exists
    print("Constructed shapefile path:", shapefile_path)
    assert os.path.exists(shapefile_path), f"Shapefile not found: {shapefile_path}"

    widget.map_data.load_shapefile(shapefile_path)
    widget.change_projection("EPSG:3395")
    assert widget.map_data.proj_string == "EPSG:3395"
