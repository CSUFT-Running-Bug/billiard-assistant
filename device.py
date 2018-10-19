import sys
import os
import re
import resolves


def resolution():
    """
    获取手机分辨率，默认分辨率1080x2160
    :return:
    """
    name = '_1080x2160'
    normal = resolves._1080x2160.normal
    maximum = resolves._1080x2160.maximum
    edge = resolves._1080x2160.edge

    rr = os.popen('adb shell wm size')
    rr = re.search('\d+x\d+', rr.read()).group()
    if rr != '1080x2160':
        name = '_' + rr
        try:
            if rr == '1080x1920':
                normal = resolves._1080x1920.normal
                maximum = resolves._1080x1920.maximum
                edge = resolves._1080x1920.edge
            else:
                # 这里添加其他分辨率判断
                pass
        except AttributeError as e:
            print(str(e) + ' 分辨率%s暂不支持，请自行适配' % rr)
            sys.exit(1)
    return normal, maximum, edge, name
