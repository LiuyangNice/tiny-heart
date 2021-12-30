"""返回指定页面数据"""

from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
import re


def main():
    # 创建tcp服务端套接字
    tcp_server = socket(AF_INET, SOCK_STREAM)
    # 设置socket选项，立即释放端口，正常情况下，服务器断开连接后，需要1-2分钟才会释放端口
    tcp_server.setsockopt(SOL_SOCKET, SO_REUSEADDR, True)
    # 局域网下其他电脑可以通过 本机ip:9090访问，本机可以使用127.0.0.1:9090访问（默认是80,所以后面要加端口号）
    tcp_server.bind(("", 8000))
    # 设置监听：单任务，同一时刻只有一个客户端能建立连接，其他的都等着建立连接
    tcp_server.listen(128)
    # 循环接受可客户端的连接请求
    while True:
        # 生成一个新的套接字，专门处理这一个客户端，tcp_server就可以省下来等待其他的客户端请求
        service_client_sock, ip_port = tcp_server.accept()
        # 正常请求报文1024就足够接收了，为了防止特殊情况使用了4096
        client_request_data = service_client_sock.recv(4096)
        client_request_content = client_request_data.decode("utf-8")
        # 查找请求资源路径
        print(client_request_content)
        match_obj = re.search("r/\S*", client_request_content)
        print(match_obj)
        if not match_obj:
            print("访问路径有误")
            service_client_sock.close()
            return

        request_path = match_obj.group()
        print(request_path)
        if request_path == "/":
            request_path = "/index.html"
        # 判断访问的资源存在可以使用异常处理或者os模块的os.path.exists()
        # import os
        # os.chdir("static")
        # res = os.path.exists('index.html')
        # print(res)
        try:
            with open("static" + request_path, 'rb') as file:
                file_data = file.read()
        except Exception as e:
            # 准备响应报文数据
            # 响应行
            response_line = "HTTP/1.1 404 Not Found\r\n"
            # 响应头
            response_header = "Server: PWS1.0\r\nContent-Type: text/html;charset=utf-8\r\n"
            # 响应体 -> 打开一个404html数据把数据给浏览器
            response_body = "<h1>非常抱歉，您当前访问的网页已经不存在了</h1>".encode("utf-8")

            # 匹配响应报文数据
            response_data = (response_line + response_header + "\r\n").encode("utf-8") + response_body
            # 发送响应报文数据
            service_client_sock.send(response_data)
        else:
            # 准备响应数据
            # 响应行
            response_line = "HTTP/1.1 200 OK\r\n"
            # 响应头
            response_header = "Server: PWS1.0\r\nContent_Type: text/html; charset=utr-8\r\n"
            # 响应体
            response_body = file_data
            response_data = (response_line + response_header + "\r\n").encode("utf-8") + response_body

            service_client_sock.send(response_data)
        finally:
            service_client_sock.close()


if __name__ == "__main__":
    main()


