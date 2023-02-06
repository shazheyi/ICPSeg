
import numpy as np
from bi_preprocess import ProcessPcap
import matplotlib.pyplot as plt
import os
def picture(data):
    from matplotlib import pyplot as plt
    # 设置图片大小
    fig = plt.figure(figsize=(8, 8), dpi=80)  # plt.figure用来设置图像大小，dpi参数调节图片清晰度
    x = range(1, len(data)+1)
    y = data  # x,y一起组成了要绘制图形的图标
    # 绘图
    plt.plot(x, y,marker='o', color='r')  # 传入x，y绘制出折线图
    # 设置x轴刻度
    plt.xticks(x)  # 设置x轴刻度 可以以plt.xticks(range(2,26))的样式来调节x刻度参数
    # 展示图形
    plt.show()  # 在执行程序的同时显示出图形

def reverse_data(x):
    y=[]
    for i in x:
        i.reverse()
        y.append(i)
    return y
def data_alignment(data,max_len):
    # 首位对齐
    front_data = list(map(lambda x: x + [0] * (max_len - len(x)), data))  # 将data中不同长度的list统一为max_len长度的，不足的后面补0
    # 末位对齐
    back_data = list(map(lambda x:   [0] * (max_len - len(x))+x , data))
    return front_data,back_data
def transposition(x):
    """
            x的转置矩阵
    """
    y=list(zip(*x))
    y=np.array(y)
    # print(dataset.shape)
    return y


def calc_ent(x):
    """
        calculate shanno ent of x
    """
    x_value_list = set([x[i] for i in range(x.shape[0])])
    ent = 0.0
    for x_value in x_value_list:
        p = float(x[x == x_value].shape[0]) / x.shape[0]
        logp = np.log2(p)
        ent -= p * logp

    return ent

def calc_condition_ent(x, y):
    """
        calculate ent H(y|x)
    """

    # calc ent(y|x)
    x_value_list = set([x[i] for i in range(x.shape[0])])
    ent = 0.0
    for x_value in x_value_list:
        sub_y = y[x == x_value]
        temp_ent = calc_ent(sub_y)
        ent += (float(sub_y.shape[0]) / y.shape[0]) * temp_ent

    return ent

def calc_ent_grap(x,y):
    """
        calculate ent grap
    """
    x_ent=calc_ent(x)
    y_ent = calc_ent(y)
    condition_ent = calc_condition_ent(x, y)
    ent_grap = y_ent - condition_ent #信息增益 g(y,x)=H(y)-H(y|x)
    #计算信息增益比 G(y,x)=g(y,x)/H(x)
    G=0.0 #x_ent==0.0时G=1.0
    if x_ent!=0.0:
        G=ent_grap/x_ent
    return G


def get_ent_point(data,h):
    """
            根据信息熵获得字符分割点
            data:某类协议数据中的一条消息序列，主要是用于判断固定字段的值
            h:信息熵列表
            type:首位对齐还是末位对齐
    """
    point=[]
    fixed_field_list = []
    fix_len = 0
    zero_len = 0
    # picture(h[14:34])
    for i in range(0,len(h)-1):
        # 如果是首位对齐，进行操作一
        if i != 0 and h[i] >= h[i - 1] and h[i] > h[i + 1]:
            point.append(i + 1)
        # 首位对齐和末位对齐均进行操作二
        if h[i] == 0.0 and h[i + 1] > 0:
            # 计算固定字段的长度
            idx = i
            while h[idx] == 0.0 and idx >= 0:
                fix_len += 1
                idx -= 1
            # 计算连续O字段的长度
            idx = i
            while h[idx] == 0.0 and idx >= 0:
                if data[idx] != 0:
                    break
                zero_len += 1
                idx -= 1

            if zero_len % 4 == 1: #zero_len == 1
                if fix_len >1:
                    point.append(i)
                    fixed_field_list.append([i - fix_len + 1, i])
            elif zero_len % 4 == 2:#zero_len == 2
                if fix_len >2:
                    point.append(i - 1)
                    fixed_field_list.append([i - fix_len + 1, i - 1])
            elif zero_len % 4 == 3:#zero_len >= 3
                if fix_len >3:
                    point.append(i - 2)
                    fixed_field_list.append([i - fix_len + 1, i - 2])
            else:
                point.append(i + 1)
                fixed_field_list.append([i - fix_len + 1, i + 1])
            fix_len = 0
            zero_len = 0

    print("信息熵分割点：{}".format(point))
    return point,fixed_field_list


def get_G_point(G,ent):
    """
            根据信息增益比获得字符分割点
            G：该点处的信息增益比值
            ent: 该点处的信息熵值，用于判断是否不为0
    """
    # picture(G[14:34])
    point = []
    threshold=0.01 #阈值
    for i in range(0, len(G) - 1):
        # 如果是第一位，仅判断是否小于设定阈值
        if i==0:
            if ent[i] > 0.0:
                if G[i] < threshold:
                    point.append(i + 1)
        else:
            if ent[i] > 0.0:
                # 小于设定阈值点
                if G[i] < threshold:
                    point.append(i + 1)
                # 极小值点
                elif G[i] < G[i - 1] and G[i] < G[i + 1] :
                    point.append(i + 1)
    print("信息增益比分割点:{}".format(point))
    return point

def get_ent_list(data):
    ent_list = []
    idx_list = []
    for idx in range(len(data)):
        ent = calc_ent(data[idx])
        ent_list.append(ent)
        idx_list.append(idx + 1)
    print("信息熵:{}，长度为{}".format(ent_list, len(ent_list)))
    return ent_list

def get_G_list(data):
    """
        获得数据的信息熵和信息增益比值列表
    """
    G_list = []
    for idx in range(len(data)):
        G = 0.0
        if idx != len(data) - 1:
            G = calc_ent_grap(data[idx], data[idx + 1])
        G_list.append(G)

    print("信息增益比:{}，长度为{}".format(G_list, len(G_list)))
    # #展示出来
    # import matplotlib.pyplot as plt
    # plt.plot(G_list[3:8])
    # plt.show()
    return G_list

def picture(ent_list,G_list):
    fig = plt.figure(figsize=(8, 5))
    offset=list(range(1,19))
    label = ['IE', 'GR']
    line_color = ["#91CC75","#FAC858"]
    # plt.grid(axis="y")
    plt.plot(offset, ent_list, color=line_color[0], marker='o', label=label[0],markersize=6)
    plt.plot(offset, G_list, color=line_color[1], marker='^', label=label[1],markersize=6,linestyle='--')

    plt.xticks(size=9.5)
    my_x_ticks = np.arange(1, 19, 1)
    plt.xticks(my_x_ticks)
    plt.ylabel('Segmentation value', fontproperties='Times New Roman', fontsize=12)
    plt.xlabel('half-byte offset',fontproperties='Times New Roman',fontsize=12)
    plt.legend(fontsize=12)

    plt.grid(axis='y', linestyle=":")
    plt.grid(axis='x', linestyle=":")

    plt.tight_layout()

    plt.savefig('modbus.pdf', dpi=100, bbox_inches='tight')
    plt.show()

def front_segmentation(data,min_len):
    data_T=transposition(data)
    ent_list=get_ent_list(data_T)
    # print(data[0][4])
    # print(data[0][5])
    # print(data[0][6])
    # print(data[0][7])
    # # 测试是否对齐
    # for i in range(len(data_T[1])):
    #     if data_T[3][i] != 10:
    #         print(i)

    ent_point, fixed_field_list = get_ent_point(data[0], ent_list)
    G_list=get_G_list(data_T)
    G_point = get_G_point(G_list, ent_list)
    # picture(ent_list[:18],G_list[:18])
    #获得结果点集合
    res_point = set()
    res_fixed_field_list=[]
    for i in ent_point:
        if i > min_len:
            break
        else:
            res_point.add(i)
    for i in G_point:
        if i > min_len:
            break
        else:
            res_point.add(i)
    for i in fixed_field_list:
        if i[0] > min_len:
            break
        elif i[1]>min_len:
            i[1]=min_len
            res_fixed_field_list.append(i)
        else:
            res_fixed_field_list.append(i)
    res_point = list(res_point)
    res_point.sort()
    print("首位对齐最终结果分割点{}".format(res_point))
    print("固定字段为{}".format(res_fixed_field_list))
    print("-------------------------------------------------------------")

    # last_point=res_point[len(res_point)-2]
    # print("最后一个分割点{}".format(last_point))

    return res_point

def back_segmentation(data,min_len):
    data_T = transposition(data)
    ent_list = get_ent_list(data_T)

    # 获得结果点集合
    res_point = []
    res_fixed_field_list = []
    end_idx=len(ent_list)-1
    idx=end_idx
    while idx>end_idx-min_len:
        if ent_list[idx]!=0:
            break
        if data[0][idx]==0 and data[0][idx-1]==0:
            break
        idx-=1
    point=idx-end_idx
    if point!=0:
        res_point.append(point)
        res_fixed_field=[point,-1]
        res_fixed_field_list.append(res_fixed_field)

    print("末位对齐最终结果分割点{}".format(res_point))
    print("固定字段为{}".format(res_fixed_field_list))
    print("-------------------------------------------------------------")

def get_min_and_max_len(data):
    min_len=len(data[0])
    max_len=len(data[0])
    for i in range(1,len(data)):
        if len(data[i])>max_len:
            max_len=len(data[i])
        if len(data[i]) < min_len:
            min_len = len(data[i])
    print("最短长度为{}，最长长度为{}".format(min_len,max_len))
    return min_len,max_len



def segmentation(path):
    data=ProcessPcap(path, 0)
    min_len,max_len=get_min_and_max_len(data)
    front_data, back_data=data_alignment(data,max_len)
    front_segmentation(front_data,min_len)

def read_datasets(url):
    file  = os.listdir(url)
    for f in file:
        pcap_url=os.path.join(url,f)
        segmentation(pcap_url)

def main():
    read_datasets(r"E:\沙哲一\Python Projects\迁移数据\半字节字段提取算法\final_datasets\original")
    # read_datasets(r"E:\沙哲一\Python Projects\迁移数据\半字节字段提取算法\final_datasets\100")
    # read_datasets(r"E:\沙哲一\Python Projects\迁移数据\半字节字段提取算法\final_datasets\1000")
if __name__=="__main__":
    main()
#最大长度
# segmentation(r"E:\沙哲一\Python Projects\迁移数据\半字节字段提取算法\final_datasets\Modbus-TCP.pcap")
# segmentation(r"E:\沙哲一\Python Projects\迁移数据\半字节字段提取算法\final_datasets\S7Comm.pcap")
# segmentation(r"E:\沙哲一\Python Projects\迁移数据\半字节字段提取算法\final_datasets\ESIO.pcap")
# segmentation(r"E:\沙哲一\Python Projects\迁移数据\半字节字段提取算法\final_datasets\BACnet-IP.pcap")
# segmentation(r"E:\沙哲一\Python Projects\迁移数据\半字节字段提取算法\final_datasets\BACnet Ethernet.pcap")
# segmentation(r"E:\沙哲一\Python Projects\迁移数据\半字节字段提取算法\final_datasets\EtherCAT.pcap")
# segmentation(r"E:\沙哲一\Python Projects\迁移数据\半字节字段提取算法\final_datasets\Powerlink-V2.pcap")
# segmentation(r"E:\沙哲一\Python Projects\迁移数据\半字节字段提取算法\final_datasets\Powerlink-V1.pcap")
# segmentation(r"E:\沙哲一\Python Projects\迁移数据\半字节字段提取算法\final_datasets\hartip.pcap")
# segmentation(r"E:\沙哲一\Python Projects\迁移数据\半字节字段提取算法\final_datasets\ecpri.pcap")

#100长度
# segmentation(r"E:\沙哲一\Python Projects\迁移数据\半字节字段提取算法\final_datasets\100\Modbus-TCP.pcap")
# segmentation(r"E:\沙哲一\Python Projects\迁移数据\半字节字段提取算法\final_datasets\100\S7Comm.pcap")
# segmentation(r"E:\沙哲一\Python Projects\迁移数据\半字节字段提取算法\final_datasets\100\ESIO.pcap")
# segmentation(r"E:\沙哲一\Python Projects\迁移数据\半字节字段提取算法\final_datasets\100\BACnet-IP.pcap")#1010-1050
# segmentation(r"E:\沙哲一\Python Projects\迁移数据\半字节字段提取算法\final_datasets\100\BACnet Ethernet.pcap")
# segmentation(r"E:\沙哲一\Python Projects\迁移数据\半字节字段提取算法\final_datasets\100\Powerlink-V2.pcap")

#1000长度
# segmentation(r"E:\沙哲一\Python Projects\迁移数据\半字节字段提取算法\final_datasets\1000\Modbus-TCP.pcap")
# segmentation(r"E:\沙哲一\Python Projects\迁移数据\半字节字段提取算法\final_datasets\1000\S7Comm.pcap")
# segmentation(r"E:\沙哲一\Python Projects\迁移数据\半字节字段提取算法\final_datasets\1000\ESIO.pcap")
# segmentation(r"E:\沙哲一\Python Projects\迁移数据\半字节字段提取算法\final_datasets\1000\BACnet-IP.pcap")#1010-1050
# segmentation(r"E:\沙哲一\Python Projects\迁移数据\半字节字段提取算法\final_datasets\1000\BACnet Ethernet.pcap")
# segmentation(r"E:\沙哲一\Python Projects\迁移数据\半字节字段提取算法\final_datasets\1000\Powerlink-V2.pcap")