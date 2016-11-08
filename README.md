## 依赖
*   nginx
*   uwsgi
*   mysql
*   redis
*   mongodb


```
mongodb 配置文件

systemLog:
    destination: file
    path: "/tmp/mongo.log"
    logAppend: true

storage:
    dbPath: /opt/db
    journal:
        enabled: true
    engine: mmapv1

processManagement:
    fork: true

net:
    bindIp: 127.0.0.1
    port: 27017

```

## 开发环境部署
1.  `git clone https://muzhishidai@bitbucket.org/muzhi/dianjing-server.git server`
2.   `cd server && git submodule update --init --recrusive`
3.  创建虚拟环境并安装依赖
    ```
    virtualenv env
    source env/bin/activate
    pip install -r requirements.txt
    ```
    
    **注意** `protobuf` 库要用 cpp implementation.
    
    所以要编译 安装 protobuf,并设置 `LD_LIBRARY_PATH`
    
4.  编辑配置文件
    ```
    cp settings.xml.example settings.xml
    ```

5.  编辑 `uwsgi.ini`
6.  配置并运行 `nginx`, `mysql`, `redis`, `mongodb`. 

7.  初始化. (首次运行的时候需要读取本地的 config.zip)
    ```
    创建数据库 create database XXX default charset=utf8;
    DIANJIG_CONFIG=local = python manage.py migrate
    DIANJIG_CONFIG=local = python manage.py collectstatic
    DIANJIG_CONFIG=local = python manage.py createsuperuser
    ```

8.  进入admin 配置 version, config, servers 信息

    config 需要一下配置:
    
    *   qq: 客服QQ号
    *   qq_group: 玩家QQ群
    *   email:  客服邮箱
    *   1sdk_callback: 1sdk 支付回调地址  HOST:PORT/callback/1sdk/


## 生产环境部署
去掉上面第二步


## 管理命令

*   `python manage.py game reset` 重置
*   `python manage.py game empty_cache` 清空缓存
    
    主要是 staff, unit 的计算结果都缓存起来的.
    
    如果调整了公式,或者配置参数,为了及时生效,需要清空缓存
*   `python manage.py mongodb createindex` 建立mongodb索引

    其实在admin添加server的时候,这个server对应的mongodb是自动创建索引的.
    
    但如果部署完毕后,更改了mongodb 结构,那么这条命令可以对所有的servers再次创建index

*   `python manage.py nginx` 输出 nginx 配置


## settings.xml

##### duty-server
本组服务器cronjob要处理的 servers

考虑这种情况, 开了1 到 100 这100个 游戏逻辑服(区), 
并且 代码是通过负载均衡跑在两台计算上的.

当跑cronjob的时候, 要是这台计算机都对同一个server跑了一遍,
那么就相当于跑了两边,这肯定是不对的.
所以需要这个duty-server. 上面的情况可以这么配置:

第一个机器上 是 1-50 , 第二个是 50-999 

第二个的结束范围是999,而不是100的原因是, 要是后面开了101区, 
那么101的cronjob自然就在第二台 计算机上跑了.

只要开服数块到 999 的时候, 修改一下配置文件 即可

##### sockets
sockets 服务器地址, 可以配置多个, 以负载均衡

##### mongodb
可以配置多个, sid-min 和 sid-max 的设置是指 这一个 mongodb 要承载的 游戏区
