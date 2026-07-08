# 图像美化系统

Python + OpenCV + PySide6 实现的课程实践项目，可打包为轻量桌面 exe。

## 运行

```powershell
python -m pip install -r requirements.txt
python main.py
```

## 打包

```powershell
powershell -ExecutionPolicy Bypass -File .\build.ps1
```

生成文件：`dist\VisionBeautifier.exe`

## 功能

- BMP / JPG / PNG 读取、显示、保存
- 高斯噪声、椒盐噪声、均匀随机噪声
- 均值滤波、中值滤波、高斯滤波
- 旋转、镜像、平移、裁剪
- 亮度、对比度、色相、饱和度调整
- 锐化、描边
- 阈值分割、框选 GrabCut 分割
- 加边框、雾化、浮雕、艺术文字
- 面积、重心、周长、矩形度、圆形度测量
