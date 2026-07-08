# 图像美化系统

这是一个用 Python、OpenCV 和 PySide6 写的桌面图像处理软件。项目最初来自《计算机视觉系统开发实践》课程设计，后来按个人作品集项目继续整理：补了图形界面、参数预览、打包脚本、基础测试和 GitHub Release。

软件面向的是常见图片处理练习，不追求 Photoshop 那种完整图层系统。它更适合展示 OpenCV 基础算法如何组合成一个可以运行、可以交付的小型桌面应用。

## 下载体验

Windows 用户可以直接下载 Release 里的可执行文件：

[下载 VisionBeautifier.exe](https://github.com/Ren7707/vision-beautifier/releases/download/v0.1.0/VisionBeautifier.exe)

如果 Windows 弹出安全提示，选择“更多信息”后继续运行即可。这个程序没有安装器，双击 exe 就能启动。

## 主要功能

- 读取、显示和保存 BMP、JPG、PNG 图片
- 支持彩色图和灰度图
- 添加高斯噪声、椒盐噪声、均匀随机噪声
- 使用均值滤波、中值滤波、高斯滤波去噪
- 旋转、镜像、平移、裁剪
- 调整亮度、对比度、色相、饱和度，并实时预览
- 锐化和描边
- 阈值分割、GrabCut 框选分割
- 对分割遮罩做矩形区域添加和删除
- 加边框、雾化、浮雕、艺术文字
- 显示原图和当前结果的对比图
- 显示灰度直方图
- 测量区域面积、重心、周长、矩形度和圆形度
- 撤销和重做最近的编辑操作

## 界面设计

界面采用深色工具台风格。左侧是工具和参数区，右侧是图片预览区。涉及数值的操作尽量使用滑动条，例如亮度、对比度、旋转角度、噪声强度、滤波核大小、边框宽度和雾化强度。

这一版没有做复杂菜单，常用功能都放在主界面上，方便课堂演示和录屏讲解。

## 本地运行

```powershell
python -m pip install -r requirements.txt
python main.py
```

如果本机没有配置 `python` 命令，可以先安装 Python 3.10 或更高版本。

## 打包 EXE

项目提供了 PowerShell 打包脚本：

```powershell
powershell -ExecutionPolicy Bypass -File .\build.ps1
```

生成文件位于：

```text
dist\VisionBeautifier.exe
```

打包使用 PyInstaller 的 onefile 模式。最终 exe 会把 Python 运行时、PySide6、OpenCV 和 NumPy 一起带上，所以体积在 60 MB 左右。

## 项目结构

```text
.
├── main.py                    # 程序入口
├── src/beautify/main.py       # PySide6 图形界面
├── src/beautify/ops.py        # 图像处理算法
├── tests/test_ops.py          # 核心算法测试
├── requirements.txt           # Python 依赖
├── build.ps1                  # Windows 打包脚本
└── VisionBeautifier.spec      # PyInstaller 配置
```

## 测试

```powershell
python -m unittest tests.test_ops -v
```

当前测试覆盖了亮度和对比度调整、裁剪、区域测量、对比图、遮罩编辑、直方图和旋转等核心逻辑。

## 后续计划

- 给艺术文字增加文字输入框
- 把遮罩编辑从矩形选择扩展成画笔
- 增加一组示例图片和功能演示截图
- 整理课程报告和演示视频素材

## 说明

这个项目主要用于课程实践和个人展示。源码里没有接入云服务，也不会上传本地图片。
