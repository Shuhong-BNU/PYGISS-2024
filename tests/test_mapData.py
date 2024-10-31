# test_mapData.py

import pytest
import os
from core.mapData import MapData
from pathlib import Path

def get_test_file_path(*paths):
    # 获取项目的根目录路径并使用 Pathlib
    project_root = Path(__file__).resolve().parent.parent
    full_path = project_root.joinpath(*paths)
    print("Constructed file path:", full_path)  # 调试信息
    return full_path

def test_load_shapefile():
    map_data = MapData()
    shapefile_path = get_test_file_path("tests", "data", "ne_50m_admin_0_countries.shp")

    # 检查文件路径和关联文件是否存在
    assert shapefile_path.exists(), f"Shapefile (.shp) not found: {shapefile_path}"
    assert shapefile_path.with_suffix('.dbf').exists(), f"DBF file not found for shapefile: {shapefile_path}"
    assert shapefile_path.with_suffix('.shx').exists(), f"SHX file not found for shapefile: {shapefile_path}"

    map_data.load_shapefile(str(shapefile_path))
    assert len(map_data.shapes) > 0
    assert len(map_data.records) > 0
    assert map_data.crs == "EPSG:4326"  # 假设默认 CRS 是 WGS84

def test_change_projection():
    map_data = MapData()
    shapefile_path = get_test_file_path("tests", "data", "ne_50m_admin_0_countries.shp")

    # 文件路径检查
    assert shapefile_path.exists(), f"Shapefile (.shp) not found: {shapefile_path}"
    assert shapefile_path.with_suffix('.dbf').exists(), f"DBF file not found for shapefile: {shapefile_path}"
    assert shapefile_path.with_suffix('.shx').exists(), f"SHX file not found for shapefile: {shapefile_path}"

    map_data.load_shapefile(str(shapefile_path))
    map_data.change_projection("EPSG:3571")  # 更改投影
    assert map_data.proj_string == "EPSG:3571"

def test_clear_map():
    map_data = MapData()
    shapefile_path = get_test_file_path("tests", "data", "ne_50m_admin_0_countries.shp")

    # 文件路径检查
    assert shapefile_path.exists(), f"Shapefile (.shp) not found: {shapefile_path}"
    assert shapefile_path.with_suffix('.dbf').exists(), f"DBF file not found for shapefile: {shapefile_path}"
    assert shapefile_path.with_suffix('.shx').exists(), f"SHX file not found for shapefile: {shapefile_path}"

    map_data.load_shapefile(str(shapefile_path))
    map_data.clear_map()
    assert len(map_data.shapes) == 0
    assert len(map_data.records) == 0
