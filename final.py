import socket
import sys
import threading
import operate

drawing = False
tmp_data = bytes()


class MyThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        global drawing
        # 这个线程不能销毁，销毁了GUI也跟着没了
        while True:
            if drawing:
                operate.final_run(tmp_data)
                drawing = False


class Minicap(object):
    BUFFER_SIZE = 4096

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.__socket.connect((self.host, self.port))

    def consume(self):
        global drawing
        global tmp_data
        readFrameBytes = 0
        frameBodyLength = 0
        data = bytes()
        inited = False
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

                        if not drawing:
                            drawing = True
                            tmp_data = data[:]
                        if not inited:
                            inited = True
                            # 启动一个无限循环线程
                            MyThread().start()

                        cursor += frameBodyLength
                        frameBodyLength = readFrameBytes = 0
                        data = bytes()
                    else:
                        # print('body(len=%d)' % (buf_len - cursor))
                        data += chunk[cursor:buf_len]
                        frameBodyLength -= buf_len - cursor
                        readFrameBytes += buf_len - cursor
                        cursor = buf_len


if __name__ == '__main__':
    mc = Minicap('localhost', 1717)
    mc.connect()
    mc.consume()
