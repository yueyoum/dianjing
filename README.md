    git 安装 

    nginx 安装 
        从官网 http://nginx.org/  下载stable version(稳定版本)
        解压     tar -xzf nginx-1.8.0.tar.gz
                    cd nginx- 1.8.0
                    ./configure
                    make
                    sudo make install

        启动nginx
            sudo /usr/local/nginx/sbin/nginx 
            关闭nginx
            /usr/local/nginx/sbin/nginx -s stop

        添加配置
            cd /usr/local/nginx/conf/
            mkdir sites
            cd sites
            vim dianjing.conf
            cd ../
            vim nginx.conf
            
    下载文件
        git clone https://said696@bitbucket.org/muzhi/dianjing-server.git  需要bitbucket账号

    下载子模块文件
        cd dianjing-server
        git submodule update --init --recursive
        cd c_src
        git checkout master
        cd ../protobuf
        git checkout master
        cd ../

    建立虚拟环境
        virtualenv env
    进入虚拟环境
        source env/bin/active
    安装第三方依赖
        pip install -r requirements.txt
        make ext
    
    修改配置
        cp setting.xml.example setting.xml
        vim settting.xml

    创建数据库 
        mysql -u username -p 
     
    构建数据库表 
        python manage.py migrate
    
    进入数据库
        python manage.py dbshell

   收集静态文件 
        python manage.py collectstatic

    创建后台用户
        python manage.py createsuperuser
    
    启动服务器
        uwsgi dianjing-uwsgi.ini

    登陆admin 
        服务器地址:8000/admin/

    添加配置文件
        version    为版本号
        config    为配置

    添加servers
        mongo port     27017
        mongodb    一个服务器对应一个
       
       --------------------------------> end!! <----------------------------------
