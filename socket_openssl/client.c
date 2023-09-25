#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <stddef.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <openssl/ssl.h>
#include <openssl/err.h>

#define SERVER_IP "127.0.0.1"  // 请根据需要更改服务器IP
#define SERVER_PORT 9990  
#define MAXLINE 4096  
  typedef enum {
    SSL_MODE_SERVER,
    SSL_MODE_CLIENT
} SSL_MODE;

#include <stdio.h>  
#include <stdlib.h>  
#include <stddef.h>
#include <string.h>  
#include <unistd.h>  
#include <sys/socket.h>  
#include <arpa/inet.h>
#include <netinet/in.h>  
#include <openssl/ssl.h>  
#include <openssl/err.h>  
  
#define SERVER_PORT 9990  
#define MAXLINE 4096  
  typedef enum {
    SSL_MODE_SERVER,
    SSL_MODE_CLIENT
} SSL_MODE;

int main(int argc, char **argv) {  
    int listenfd, connfd;  
    struct sockaddr_in servaddr, cliaddr;  
    char buf[MAXLINE];  

    // 创建监听套接字  
    listenfd = socket(AF_INET, SOCK_STREAM, 0);  
  
    // 绑定地址和端口  
    memset(&servaddr, 0, sizeof(servaddr));  
    servaddr.sin_family = AF_INET;  
    servaddr.sin_addr.s_addr = htonl(INADDR_ANY);  
    servaddr.sin_port = htons(SERVER_PORT);  
    bind(listenfd, (struct sockaddr *) &servaddr, sizeof(servaddr));  
  
    // 监听连接  
    listen(listenfd, 10);  
    printf("Listening on port %d...\n", SERVER_PORT);  
  
    while (1) {  
        // 接受连接请求  
        socklen_t len = sizeof(cliaddr);  
        connfd = accept(listenfd, (struct sockaddr *) &cliaddr, &len);  
        printf("Accepted connection from %s:%d\n", inet_ntoa(cliaddr.sin_addr), ntohs(cliaddr.sin_port));  
  
        // 创建 SSL 对象并进行握手  
        SSL *ssl = sync_initialize_ssl("cert.pem", "key.pem", SSL_MODE_SERVER, connfd); 
  
        // 读取客户端发送的数据并回复  
        memset(buf, 0, MAXLINE);  
        SSL_read(ssl, buf, MAXLINE);  
        printf("Received: %s\n", buf);  
        SSL_write(ssl, "Hello, client!", strlen("Hello, client!"));  
  
        // 关闭连接和清理资源  
        close(connfd);  
        SSL_shutdown(ssl);  
        SSL_free(ssl);  
    }  
  

    return 0;  
}


int main(int argc, char **argv) {
    int sockfd;
    struct sockaddr_in servaddr;
    char buf[MAXLINE];
    // 创建 socket
    sockfd = socket(AF_INET, SOCK_STREAM, 0);

    // 设置服务器地址和端口
    memset(&servaddr, 0, sizeof(servaddr));
    servaddr.sin_family = AF_INET;
    servaddr.sin_addr.s_addr = inet_addr(SERVER_IP);
    servaddr.sin_port = htons(SERVER_PORT);

    // 连接到服务器
    connect(sockfd, (struct sockaddr *) &servaddr, sizeof(servaddr));

    // 创建 SSL 对象并进行握手
    SSL *ssl = sync_initialize_ssl("cert.pem", "key.pem", SSL_MODE_CLIENT, sockfd); 
    // 发送数据给服务器
    SSL_write(ssl, "Hello, server!", strlen("Hello, server!"));

    // 读取服务器的回复
    memset(buf, 0, MAXLINE);
    SSL_read(ssl, buf, MAXLINE);
    printf("Received: %s\n", buf);

    // 关闭连接和清理资源
    close(sockfd);
    SSL_shutdown(ssl);
    SSL_free(ssl);

    return 0;
}


