# core/PSF_Object.py

class PSF_Object:
    def __init__(self, id, x, y):
        self.id = id
        self.x, self.y = x, y
        self.longitude, self.latitude = 0, 0

    def set_coordinates(self, longitude, latitude):
        """设置经纬度坐标"""
        self.longitude = longitude
        self.latitude = latitude

    def get_coordinates(self):
        """获取经纬度坐标"""
        return self.longitude, self.latitude
