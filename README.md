# 腾讯桌球助手

此项目可以延长腾讯桌球小程序的辅助线，准确率可达90%。原理是通过[minicap](https://github.com/openstf/minicap)实时传输手机屏幕截图，然后通过opencv匹配模板图像和画线来实现延长辅助线。minicap具体详情可查看[项目网址](https://github.com/openstf/minicap)。

## 注意

* 支持的手机分辨率：`2160x1080`、`1920x1080`。其他分辨率暂时请自行适配（请查看[适配](#适配)）。
* minicap传输实时屏幕速度太快，而我的操作图片代码的速度赶不上。所以使用了另一个线程来处理图片，一定几率导致线程崩溃。
* 帧率只有`5fps`，延迟`200ms`。

## 环境要求

* [minicap](https://github.com/openstf/minicap)
* [python3](https://www.python.org/)
* Android版本>5

## 用法

### 安装运行minicap

先进入minicap目录。
```bash
cd minicap
```

获取设备支持的ABI。
```bash
ABI=$(adb shell getprop ro.product.cpu.abi | tr -d '\r')
```

然后将对应的minicap导入设备。
```bash
adb push libs/$ABI/minicap /data/local/tmp/
```

还需要将对应的共享库导入设备。
```bash
SDK=$(adb shell getprop ro.build.version.sdk | tr -d '\r')
adb push jni/libs/android-$SDK/$ABI/minicap.so /data/local/tmp/
```

授予执行权限。
```bash
adb shell chmod 777 /data/local/tmp/minicap
```

测试一下，如果打印了OK说明没有问题。
```bash
adb shell LD_LIBRARY_PATH=/data/local/tmp /data/local/tmp/minicap -P 2160x1080@2160x1080/0 -t
```

运行minicap。
```bash
adb shell LD_LIBRARY_PATH=/data/local/tmp /data/local/tmp/minicap -P 2160x1080@2160x1080/0
```

打开另一个终端映射本地端口。这里的端口要和python代码里面的端口一致。
```bash
adb forward tcp:1717 localabstract:minicap
```

到这里minicap就开始运行了，接下来安装python模块。

### 运行代码
```bash
cd ../
pip install -r requirements.txt
python final.py
```

## 适配
* 运行`test.py`。（按步骤运行）
* 用画图软件打开图片，然后取6个坐标。`left_top_m`蓝色框左上角，`left_top`是绿色框左上角，`left_top_e`是球桌边界左上角。
* 在`resolves.py`文件中添加对象，名称格式为`'_' + width + 'x' + height`，例如`'_1080x2160'`。
* 在`device.py`中添加判断。
* 在`templates`文件夹下添加模板图像，需为`png`格式，命名和上面一致。