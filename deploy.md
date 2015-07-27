# 部署

### 在新机器上进行新的部署

1. 使用root在 /opt 目录下建立一个 文件夹 dianjing
2. 修改权限 `sudo chown developer:developer dianjing`
3. 进入 dianjing 目录， `https://muzhishidai@bitbucket.org/muzhi/dianjing-server.git`
4. 创建虚拟环境 `virtualenv env`, 并激活, `source env/bin/activate`
5. 安装依赖 `pip install -r requirements.txt`
6. 编辑settings.xml
7. 检查 `python manage.py check`
8. 迁移数据库 `python manage.py migrate`
9. 静态文件 `python manage.py collectstatic`
10. 编辑 dianjing-uwsgi.ini 并运行 `uwsgi --ini dianjing-uwsgi.ini`

