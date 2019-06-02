# -*- coding: UTF-8 -*-

from GPTree import GPTree, getTaxiPos, getNodePos
import json

road_node = "data/road.cnode"
road_edge = "data/road.cedge"
cars = "data/car.txt"
template= "frontend/template.html"
result = "result/map.html"

taxies, passages = getTaxiPos()
nodes = getNodePos()

delta_lgt = 0.0066
delta_lat = 0.0057
gpTree = GPTree()
nodes = []

# colors = [
#     "#9FDFC7",
#     "#9A37A4",
#     "#492418",
#     "#173545",
#     "#9B9D34",
# ]
# taxiJS = \
# """
# var taxi_{id} = new BMap.Marker(new BMap.Point({lgt},{lat}), {{
#   icon: new BMap.Symbol(BMap_Symbol_SHAPE_STAR, {{
#     scale: 2,
#     fillColor: "pink",
#     fillOpacity: 0.8
#   }})
# }});
# map.addOverlay(taxi_{id});
# """

# routeJS = \
# """
# var sy_{id} = new BMap.Symbol(BMap_Symbol_SHAPE_BACKWARD_OPEN_ARROW, {{
#   scale: 0.6,//图标缩放大小
#   strokeColor:'#fff',//设置矢量图标的线填充颜色
#   strokeWeight: '2',//设置线宽
# }});
# var icons_{id} = new BMap.IconSequence(sy_{id}, '10', '30');
# // 创建polyline对象
# var pois_{id} = [
# {points}
# ];
# var polyline_{id} =new BMap.Polyline(pois_{id}, {{
#   enableEditing: false,//是否启用线编辑，默认为false
#   enableClicking: true,//是否响应点击事件，默认为true
#   icons:[icons_{id}],
#   strokeWeight:'8',//折线的宽度，以像素为单位
#   strokeOpacity: 0.8,//折线的透明度，取值范围0 - 1
#   strokeColor:"{color}" //折线颜色
# }});

# map.addOverlay(polyline_{id});          //增加折线
# """


import logging
from websocket_server import WebsocketServer
import sys
import thread

# 因为考虑到传入的字符串有非英文字符，
# 所以手动设置编码，否则可能会报编码错误
reload(sys)
sys.setdefaultencoding('utf-8')


def new_client(client, server):
    print("Client(%d) has joined." % client['id'])


def client_left(client, server):
    print("Client(%d) disconnected" % client['id'])


def message_back(client, server, message):
    # 这里的message参数就是客户端传进来的内容
    print("Client(%d) said: %s" % (client['id'], message))
    # 这里可以对message进行各种处理

    tmp = message.split(" ")
    src = int(tmp[0])
    dst = int(tmp[1])
    ans = gpTree.getAns(src, dst)
    # with open("./tmp.txt", "w") as f:
    #     f.write(json.dumps(ans))
    #     f.close()
    if ans["status"] == "successful":
        print(ans["result"])
        mes = ""

        # src dst
        mes = mes + str(nodes[src][0]) + "," + str(nodes[src][1]) + " "
        mes = mes + str(nodes[dst][0]) + "," + str(nodes[dst][1]) + " "

        # size

        mes = mes + str(len(ans["result"])) + " "

        # length
        for i in range(0, len(ans["result"])):
            mes = mes + str(ans["result"][i]["id"])+ ":" + str(ans["result"][i]["d1"])+ ":" + str(ans["result"][i]["d2"])+ ":" + str(ans["result"][i]["d3"])+ ":" + str(ans["result"][i]["d4"]) + ":"
            mes = mes + str(taxies[ans["result"][i]["id"]][0])+ "," + str(taxies[ans["result"][i]["id"]][1]) + " "


        # route
        for i in range(0, len(ans["result"])):
            # print ans["result"][i]["order"]
            for j in range(0, len(ans["result"][i]["order"])-1):
                # print(ans["result"][i]["order"][j])
                mes = mes + str(nodes[ans["result"][i]["order"][j]][0]) + "," + str(nodes[ans["result"][i]["order"][j]][1]) + ":"
            mes = mes + " "

        # passage

        for i in range(0, len(ans["result"])):
            print("taxi id:");
            print(ans["result"][i]["id"])
            if(len(passages[ans["result"][i]["id"]]) == 0):
                mes = mes + "- "
            else:
                for pa in passages[ans["result"][i]["id"]]:
                    print( str(pa[0]) + "," + str(pa[1]))
                    mes = mes + str(pa[0]) + "," + str(pa[1]) + ":"
                mes = mes + " "

        # print(len(passages))
        # print(mes)
        # exportHTML(nodes[src], nodes[dst], ans)
    else:
        print("No taxies!\n")


    # 将处理后的数据再返回给客户端
    server.send_message(client, mes)


def taxiPos(n):
    return taxies[n]

def nodePos(n):
    return nodes[n]

def addTaxi(id, pos):
    return taxiJS.format(id=id, lgt=pos[0] + delta_lgt, lat=pos[1] + delta_lat)

def addRoute(id, color, points):
    s = ""
    for point in points:
        s += "  new BMap.Point({},{}),\n".format(point[0] + delta_lgt, point[1] + delta_lat)
    return routeJS.format(id=id, color=color, points=s)

# def exportHTML(src, dst, ans):
#     print("in exportHTML" )
#     print(src, dst)
#     with open(template, "r") as f:
#         html = f.read()
#         html = html.replace("SRC0", str(src[0] + delta_lgt)).replace("SRC1", str(src[1] + delta_lat))
#         html = html.replace("DST0", str(dst[0] + delta_lgt)).replace("DST1", str(dst[1] + delta_lat))

#         taxi = ""
#         for i, t in enumerate(ans["result"]):
#             id = t["id"]
#             print(id, t["d1"], t["d2"], t["d3"], t["d4"], taxiPos(id))
#             taxi += addTaxi(i, taxiPos(id))
#         html = html.replace("TAXIES", taxi)

#         route = ""
#         for i, t in enumerate(ans["result"]):
#             points = []
#             for rank in t["order"]:
#                 points.append(nodePos(rank))
#             route += addRoute(i, colors[i], points)
#             if i >= 2:
#                 break
#         html = html.replace("ROUTES", route)

#         with open(result, "w") as o:
#             o.write(html)
#             o.close()
#         f.close()

def main():
    # gpTree = GPTree()
    # nodes = []
    with open(road_node, "r") as f:
        tmp = f.read().split('\n')[: -1]
        for j in tmp:
            i = j.split(" ")
            nodes.append([float(i[1]), float(i[2])])
    # while True:
    #     src = input("The src number : ")
    #     dst = input("The dst number : ")
    #     src = int(src)
    #     dst = int(dst)
    #     ans = gpTree.getAns(src, dst)
    #     # with open("./tmp.txt", "w") as f:
    #     #         #     f.write(json.dumps(ans))
    #     #         #     f.close()
    #     if ans["status"] == "successful":
    #         exportHTML(nodes[src], nodes[dst], ans)
    #     else:
    #         print("No taxies!\n")

    # 新建一个WebsocketServer对象，第一个参数是端口号，第二个参数是host
    # 如果host为空，则默认为本机IP
    server = WebsocketServer(4200, host='', loglevel=logging.INFO)
    # 设置当有新客户端接入时的动作
    server.set_fn_new_client(new_client)
    # 设置当有客户端断开时的动作
    server.set_fn_client_left(client_left)
    # 设置当接收到某个客户端发送的消息后的操作
    server.set_fn_message_received(message_back)
    # 设置服务一直运行
    server.run_forever()



main()
