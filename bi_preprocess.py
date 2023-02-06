#半字节单位的预处理

import os
import time

def head_detect(data):
    """
            TCP/UDP头部检测与去除
            :param data: 首位对齐后的报文数据
            :return: 如果检测出TCP/UDP头部，则输出去掉头部之后的报文数据；如果未检测出头部，则输出原报文数据
    """
    output=[]
    label=[]
    for i in range(len(data)):
        if (data[i][0]==0 and data[i][1]== 8 and data[i][2]==0 and data[i][3]==0) or (data[i][0]==8 and data[i][1]== 6 and data[i][2]==13 and data[i][3]==13):
            message=data[i][4:] #去掉0800/86DD
            if i==0:
                if data[i][0]==0 and data[i][1]== 8 and data[i][2]==0 and data[i][3]==0:
                    label.append("IPV4头部")
                elif data[i][0]==8 and data[i][1]== 6 and data[i][2]==13 and data[i][3]==13:
                    label.append("IPV6头部")
            ip_header_len = data[i][5] * 8
            message = message[ip_header_len:]  # 去掉IP头部
            if data[i][22]==1 and data[i][23]==1:
                if i==0:
                    label.append("UDP头部")
                udp_header_len=16
                message=message[udp_header_len:]
            elif data[i][22]==0 and data[i][23]==6:
                if i==0:
                    label.append("TCP头部")
                tcp_header_len=message[24]*8
                message=message[tcp_header_len:]
            output.append(message)
        else:
            return data
    print(label)
    return output

def bi_byte(byte_list):
    '''
    将每个字节的int值转为两个4bit值，及两个半个字节int值
    :param byte_list: 字节列表
    :return: bi_list: 半字节列表
    '''
    bi_list = []
    for i in byte_list:
        a = i // 16
        b = i % 16
        bi_list.append(a)
        bi_list.append(b)
    return bi_list

def ProcessPcap(file_path, num_label):
    '''
    传入pcap文件， 每个packet截取max_len个字节
    :param file_path: pcap文件地址
    :param max_len: 每个packet选取的最大长度（最好大于34，保证ignore能运行）
    :param num_label: 每个packet的标签
    :param ignore_ip: True时将每个packet的源和目的ip置
    :param ignore_mac: True时将每个packet的源和目的mac置零
    :param save_dir: 有值时，将数据保存的文件夹地址，保存为h5文件
    :return:
    NewPackets: n行 max_len 列的 np.float
    NP_Time: (n,.) 的 np.float
    '''
    print('开始处理文件 {}'.format(os.path.basename(file_path)))

    start_time = time.perf_counter()  # 记录开始处理的时间
    file = open(file_path, mode='rb')
    # seek(offsetm, whence) 前一个参数是要移动的距离，后一个参数 0 是从开头，1 是从当前位置， 2是从最后(offset 一般设置为负数）
    file_length = int(file.seek(0, 2))
    file.seek(24, 0)  # 跳过文件头 24个字节
    # print(file_length)
    Packets = []
    Packets_Time = []
    Label = []
    while file.tell() < file_length:
        #  Packet Header Length = 16
        # file.seek(8, 1)  #  读取该packet数据包的长度
        high_time = int.from_bytes(file.read(4), 'little')
        low_time = int.from_bytes(file.read(4), 'little')
        packet_time = high_time + (low_time * 1e-6)
        packet_len = int.from_bytes(file.read(4), 'little')  # 读取数据包的长度 byteorder='little' 表示 低位在前， 'big'表示高位在前
        packet_pointer = file.seek(4, 1)  # 移动到 Packet Data（Wireshark里面显示的每个数据包） 前
        packet = list(file.read(packet_len)) #返回一个元素为int的list
        packet = packet[12:]  # 这里去掉了源地址（6）和目的地址（6）

        file.seek(packet_pointer + packet_len, 0)  # 移动到下一个数据包头前

        bi_packet = bi_byte(packet)
        Packets.append(bi_packet)
        Packets_Time.append(packet_time)
        Label.append(num_label)

    NewPackets = head_detect(Packets)
    # NP_Time = np.array(Packets_Time).astype(float)
    num_p = len(NewPackets)  # 该文件的packet的数目
    print('{} 文件处理完成，共{}个packets，用时 {} s'.format(os.path.basename(file_path), num_p, time.perf_counter() - start_time))
    print("-------------------------------------------------------------")
    return NewPackets


# pcap= ProcessPcap(r'E:\沙哲一\论文文献\ICP\test_pcap\Bacnet-MS.pcap', 4)
#
# print(pcap)