class Resolve:
    def __init__(self, normal, maximum, edge):
        # 球的圆心能到达的范围
        self.normal = normal
        # 球的边界能到达的范围
        self.maximum = maximum
        # 台球桌子边界
        self.edge = edge


# 适配的分辨率请在这里添加

_1080x2160 = Resolve(
    ((371, 261), (1785, 947)),
    ((348, 238), (1807, 970)),
    ((260, 150), (1895, 1060))
)
_1080x1920 = Resolve(
    ((254, 264), (1663, 946)),
    ((230, 240), (1687, 970)),
    ((140, 150), (1776, 1060))
)
