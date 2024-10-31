# core/PSF_Object.py
# 功能：提供 PSF 对象的定义和操作方法，包含设置和获取坐标的功能

class PSF_Object:
    def __init__(self, id: int, x: float, y: float):
        """
        初始化 PSF_Object 对象
        参数:
            id (int): 对象的唯一标识符
            x (float): x 坐标
            y (float): y 坐标
        """
        self.id = id  # 对象 ID
        self.x, self.y = x, y  # 初始 x 和 y 坐标
        self.longitude, self.latitude = 0.0, 0.0  # 初始经纬度坐标，默认为 0.0

    def set_coordinates(self, longitude: float, latitude: float) -> None:
        """
        设置经纬度坐标
        参数:
            longitude (float): 经度
            latitude (float): 纬度
        """
        self.longitude = longitude  # 更新经度
        self.latitude = latitude  # 更新纬度

    def get_coordinates(self) -> tuple:
        """
        获取经纬度坐标
        返回:
            tuple: (longitude, latitude) 经纬度坐标元组
        """
        return self.longitude, self.latitude  # 返回当前经纬度坐标
