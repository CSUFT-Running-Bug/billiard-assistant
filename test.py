import socket
import sys
import cv2
import io
from PIL import Image
import numpy as np


class Minicap(object):
    BUFFER_SIZE = 4096

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.__socket.connect((self.host, self.port))

    def consume(self):
        readFrameBytes = 0
        frameBodyLength = 0
        data = bytes()
        while 1:
            try:
                chunk = self.__socket.recv(self.BUFFER_SIZE)
            except socket.error as e:
                print("Error receiving data: %s" % e)
                sys.exit(1)
            cursor = 0
            buf_len = len(chunk)
            if buf_len == 24:
                # 暂不需要头部信息
                continue
            while cursor < buf_len:
                if readFrameBytes < 4:
                    frameBodyLength += (chunk[cursor]) << (readFrameBytes * 8) >> 0
                    cursor += 1
                    readFrameBytes += 1
                else:
                    if buf_len - cursor >= frameBodyLength:
                        # print("body_fin(len=%d,cursor=%d)" % (frameBodyLength, cursor))
                        data += chunk[cursor:cursor + frameBodyLength]

                        if data[0] != 0xFF or data[1] != 0xD8:
                            print('Frame body does not start with JPG header')
                            sys.exit(1)

                        im = io.BytesIO(data)
                        im = Image.open(im)
                        im = cv2.cvtColor(np.asarray(im), cv2.COLOR_RGB2BGR)
                        cv2.imwrite('template.jpg', im)
                        sys.exit(0)
                    else:
                        # print('body(len=%d)' % (buf_len - cursor))
                        data += chunk[cursor:buf_len]
                        frameBodyLength -= buf_len - cursor
                        readFrameBytes += buf_len - cursor
                        cursor = buf_len


if __name__ == '__main__':
    # 第二步取消注释这两行，注释后三行，图片保存在当前路径下
    # im = cv2.imread('template.jpg', cv2.IMREAD_GRAYSCALE)
    # cv2.imwrite('template.png', im)

    # 第一步
    mc = Minicap('localhost', 1717)
    mc.connect()
    mc.consume()
