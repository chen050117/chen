# 导入相应包
import os
import requests
import math

# 坐标转换函数
class LngLatTransfer():

    def __init__(self):
        self.x_pi = 3.14159265358979324 * 3000.0 / 180.0
        self.pi = math.pi  # π
        self.a = 6378245.0  # 长半轴
        self.es = 0.00669342162296594323  # 偏心率平方
        pass

    def GCJ02_to_BD09(self, gcj_lng, gcj_lat):
        z = math.sqrt(gcj_lng * gcj_lng + gcj_lat * gcj_lat) + 0.00002 * math.sin(gcj_lat * self.x_pi)
        theta = math.atan2(gcj_lat, gcj_lng) + 0.000003 * math.cos(gcj_lng * self.x_pi)
        bd_lng = z * math.cos(theta) + 0.0065
        bd_lat = z * math.sin(theta) + 0.006
        return bd_lng, bd_lat

    def BD09_to_GCJ02(self, bd_lng, bd_lat):
        x = bd_lng - 0.0065
        y = bd_lat - 0.006
        z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * self.x_pi)
        theta = math.atan2(y, x) - 0.000003 * math.cos(x * self.x_pi)
        gcj_lng = z * math.cos(theta)
        gcj_lat = z * math.sin(theta)
        return gcj_lng, gcj_lat

    def WGS84_to_GCJ02(self, lng, lat):
        dlat = self._transformlat(lng - 105.0, lat - 35.0)
        dlng = self._transformlng(lng - 105.0, lat - 35.0)
        radlat = lat / 180.0 * self.pi
        magic = math.sin(radlat)
        magic = 1 - self.es * magic * magic
        sqrtmagic = math.sqrt(magic)
        dlat = (dlat * 180.0) / ((self.a * (1 - self.es)) / (magic * sqrtmagic) * self.pi)
        dlng = (dlng * 180.0) / (self.a / sqrtmagic * math.cos(radlat) * self.pi)
        gcj_lng = lat + dlat
        gcj_lat = lng + dlng
        return gcj_lng, gcj_lat

    def GCJ02_to_WGS84(self, gcj_lng, gcj_lat):
        dlat = self._transformlat(gcj_lng - 105.0, gcj_lat - 35.0)
        dlng = self._transformlng(gcj_lng - 105.0, gcj_lat - 35.0)
        radlat = gcj_lat / 180.0 * self.pi
        magic = math.sin(radlat)
        magic = 1 - self.es * magic * magic
        sqrtmagic = math.sqrt(magic)
        dlat = (dlat * 180.0) / ((self.a * (1 - self.es)) / (magic * sqrtmagic) * self.pi)
        dlng = (dlng * 180.0) / (self.a / sqrtmagic * math.cos(radlat) * self.pi)
        mglat = gcj_lat + dlat
        mglng = gcj_lng + dlng
        lng = gcj_lng * 2 - mglng
        lat = gcj_lat * 2 - mglat
        return lng, lat

    def BD09_to_WGS84(self, bd_lng, bd_lat):
        lng, lat = self.BD09_to_GCJ02(bd_lng, bd_lat)
        return self.GCJ02_to_WGS84(lng, lat)

    def WGS84_to_BD09(self, lng, lat):
        lng, lat = self.WGS84_to_GCJ02(lng, lat)
        return self.GCJ02_to_BD09(lng, lat)

    def _transformlat(self, lng, lat):
        ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
              0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
        ret += (20.0 * math.sin(6.0 * lng * self.pi) + 20.0 *
                math.sin(2.0 * lng * self.pi)) * 2.0 / 3.0
        ret += (20.0 * math.sin(lat * self.pi) + 40.0 *
                math.sin(lat / 3.0 * self.pi)) * 2.0 / 3.0
        ret += (160.0 * math.sin(lat / 12.0 * self.pi) + 320 *
                math.sin(lat * self.pi / 30.0)) * 2.0 / 3.0
        return ret

    def _transformlng(self, lng, lat):
        ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
              0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
        ret += (20.0 * math.sin(6.0 * lng * self.pi) + 20.0 *
                math.sin(2.0 * lng * self.pi)) * 2.0 / 3.0
        ret += (20.0 * math.sin(lng * self.pi) + 40.0 *
                math.sin(lng / 3.0 * self.pi)) * 2.0 / 3.0
        ret += (150.0 * math.sin(lng / 12.0 * self.pi) + 300.0 *
                math.sin(lng / 30.0 * self.pi)) * 2.0 / 3.0
        return ret

    def WGS84_to_WebMercator(self, lng, lat):
        x = lng * 20037508.342789 / 180
        y = math.log(math.tan((90 + lat) * self.pi / 360)) / (self.pi / 180)
        y = y * 20037508.34789 / 180
        return x, y

    def WebMercator_to_WGS84(self, x, y):
        lng = x / 20037508.34 * 180
        lat = y / 20037508.34 * 180
        lat = 180 / self.pi * (2 * math.atan(math.exp(lat * self.pi / 180)) - self.pi / 2)
        return lng, lat

transfer = LngLatTransfer()
error_groups = []

# 创建目录文件夹，用来存放相应的坐标文件，添加exist_ok参数,允许重复写入
folder_path_1 = "web"
folder_path_2 = "wgs_84"
os.makedirs(folder_path_1, exist_ok=True)
os.makedirs(folder_path_2, exist_ok=True)

with open('school_name.txt', 'r', encoding='utf-8') as file:
    for school_name in file:
        school_name = school_name.strip()
        file_path_1 = os.path.join(folder_path_1, f"{school_name}_web.txt")
        file_path_2 = os.path.join(folder_path_2, f"{school_name}_wgs84.txt")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"}
        url = f"https://map.baidu.com/?newmap=1&reqflag=pcmap&biz=1&from=webmap&da_par=direct&pcevaname=pc4.1&qt=s&da_src=searchBox.button&wd={school_name}&c=257&src=0&wd2=&pn=0&sug=0&l=13&b=(12598354.37355666,2611750.4914465114;12624957.186603652,2643414.6285534888)&from=webmap&biz_forward=" + "{%22scaler%22:2,%22styles%22:%22pl%22}&sug_forward=&auth=DzyX7JOUxOJJBzYSdKMQzBEOHbEIT1LZuxNBxHHHzHRt2FW21WFF84B3AzBU%40yYxvkGcuVtvvhguVtvyheuHEtH4WQ2eGvCQMuVtvIPcuxtw8wkvyFuHjtW2eGv%40vcuVtvc3CuVtvcPPuxtdw8E62qvyFuHrQH2MKSJGFosSEZ1Dp5IC%40BvhgMuzVVtvrMhuHBzNtLiidiB1Af0wd0vyOCyIIFUMO&seckey=cjjM%2FN7GHna%2FncS9%2Fets6r%2FVDzc7IKx9%2F7dyFz7aEK8%3D%2CgF3X1eAERq32B01g4TqanLzf_LdXQH2eJtaeTlve47eyiiNOsd6fDsnA61TCtM8-PnSFyMlIk3YCJgKT_6tziRcZPwk6tcUb0zrv9waBA13ixEfGf8ybfSQC4WjUgsxgdA-lYQtUTJn8r4UrwebTxv8D7FrkbVzWkU-wvKwGM_JnUzHW6SuiFfwXBWXkD3unhVB0QUpTj2XJ5p_jYOAyBg&device_ratio=2&tn=B_NORMAL_MAP&nn=0&u_loc=12609506,2633762&ie=utf-8&t=1731555488482&newfrom=zhuzhan_webmap"

        try:
            response = requests.get(url, headers=headers)
            response.encoding = "utf-8"
            data = response.json()
            geo_info = data['content'][0]['ext']['detail_info']['guoke_geo']['geo']
            geo_info = geo_info.split("-")[1]
            geo_data = geo_info.split(",")

            with open(file_path_1, "w", encoding="utf-8") as file1:
                for j in range(0, len(geo_data), 2):
                    x, y = geo_data[j], geo_data[j+1].replace(";", "")
                    file1.write(f"{x},{y}\n")
                print(f"{school_name}保存成功，相对路径为{file_path_1}")

            with open(file_path_2, "w", encoding="utf-8") as file2:
                for j in range(0, len(geo_data), 2):
                    x, y = float(geo_data[j]), float(geo_data[j+1].replace(";", ""))
                    x, y = transfer.WebMercator_to_WGS84(x, y)
                    x, y = transfer.BD09_to_WGS84(x, y)
                    file2.write(f"{x},{y}\n")
                print(f"{school_name}保存成功，相对路径为{file_path_2}")

        except Exception as e:
            error_groups.append(school_name)

if error_groups:
    print()
    print("以下名单中的学校处理时出现错误：")
    for error in error_groups:
        print(error)
