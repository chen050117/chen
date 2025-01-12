# 导入必要的包
import requests
from bs4 import BeautifulSoup

# 对含有学校名称的网页进行解析
url = "https://www.dxsbb.com/news/1683.html"
header = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36", }
response = requests.get(url, headers=header)
response.encoding = 'utf-8'
soup = BeautifulSoup(response.text, 'html.parser')
content_div = soup.find('div', class_='content')
table = content_div.find('table', class_='hasback')  # 找到相应的学校名称元素

# 创建空的列表，用来存放学校名称
school_name = []

for row in table.find_all('tr'):
    cells = row.find_all("td")
    school_info = [cell.get_text(strip=True) for cell in cells]
    if school_info:
        school_name.append(" ".join(school_info))

names = []

for name in school_name:
    names.append(name.split(" ")[1])

names = names[1:]

# 创建文件，保存到相应的文件
name_path = "school_name.txt"
with open(name_path, "w", encoding="utf-8") as file:
    for j in names:
        file.write(f"{j}\n")
print(f"学校名称成功保存，相对路径为{name_path}")
