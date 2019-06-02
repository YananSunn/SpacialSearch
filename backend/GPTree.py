# -*- coding: UTF-8 -*-
import subprocess
from multiprocessing import Process, Queue
from Queue import Empty
import json

road_node = "data/road.cnode"
road_edge = "data/road.cedge"
cars = "data/car.txt"
template= "frontend/template.html"
result = "result/map.html"


# 读入出租车的坐标
def getTaxiPos():
    with open(cars, "r") as f:
        taxies = f.read().split("\n")[: -1]
        l = []
        p = []
        for taxi in taxies:
            info = taxi.split(" ")
            pos = info[2].split(",")[: -1]
            longitude = float(pos[0])
            latitude = float(pos[1])
            l.append([longitude, latitude])

            mp = []
            for i in range(0, int(info[1])):
                passage = info[3+i].split(",")[: -1]
                lng = float(passage[0])
                lat = float(passage[1])
                mp.append([lng, lat])
            p.append(mp)

        return l,p

# 读路口的坐标
def getNodePos():
    with open(road_node, "r") as f:
        nodes = f.read().split("\n")[: -1]
        l = []
        for node in nodes:
            ele = node.split(" ")
            l.append([float(ele[1]), float(ele[2])])
        f.close()
        return l

def enqueue_output(out, queue):
    for line in iter(out.readline, b''):
        queue.put(line)
    out.close()

class GPTree:
    def __init__(self):
        self.run()

    def send(self, a, b):
        self.p.stdin.write("{} {}\n".format(a, b).encode("utf8"))
        self.p.stdin.flush()

    def recv(self, timeout=None):
        try:
            stdout = self.receiver.get(timeout=timeout)
            data = json.loads(stdout)
            return data
        except Empty:
            return -1
        except:
            return stdout

    def run(self):
        args = ["g++", "-std=c++11", "-O3", "-lmetis", "-o", "./build/GPTree", "./api/GPTree.cpp"]
        p = subprocess.Popen(args, cwd="./")
        p.wait()
        assert p.returncode == 0

        args = ["./build/GPTree"]
        self.p = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        self.receiver = Queue()
        self.t = Process(target=enqueue_output, args=(self.p.stdout, self.receiver))
        self.t.start()

    def getAns(self, src, dst):
        self.send(src, dst)
        return self.recv()

getTaxiPos()

# def main():
#     pass

# if __name__ == "__main__":
#     main()
