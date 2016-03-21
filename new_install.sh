#!/bin/bash

Error_Trap()
{
    ret=$?
    echo -e "\033[01;33m [LINE:$1] Error: Command or function exited with status ${ret}. \033[0m"
    exit $ret
}

Error_Ignore()
{
    echo -e "\033[01;35m [LINE:$1] Warnning: Error happens but being ignored. \033[0m"
}

installation_dir="deploy_web_application"
cur_python_version="python2.7"
new_python_version="python3.5"

Show_Usage()
{
    echo "Syntax: $0 [base|extra|service|django]"
    echo "base: compile and install ${new_python_version}, Django"
    echo "extra: install nginx, uwsgi and 3rd python lib"
    echo "service: firewalld, selinux and enable mariadb"
    echo "django: setup django project"
}

if [ "$(whoami)" != "root" ]
then
    echo "Please Run as root."
    exit 1
else
    #cd ${HOME}
    if [ ! -d ${installation_dir} ]
    then
        echo "CAN NOT find installation directory ${installation_dir} under ${HOME}"
        exit 1
    fi
fi

case "$1" in
    base)
        echo "============== Configure Global LANG ==============="
        global_profile="/etc/profile"
        if [ "LANG=en_US.UTF-8" != "`env | grep LANG`" ]
        then
            echo 'export LANG="en_US.UTF-8"' >> ${global_profile}
            echo 'export LC_ALL="en_US.UTF-8"' >> ${global_profile}
        else
            echo "Skipped"
        fi
        echo 'HISTSIZE=100000' >> ${global_profile}
        echo 'HISTTIMEFORMAT="%Y-%m-%d %H:%M:%S `whoami`: "'  >> ${global_profile}
        source ${global_profile}
    
        cd ${installation_dir}
        python3_source="Python-3.5.1.tar.xz"
        python3_source_dir=$(echo ${python3_source%\.tar*})
        python3_setup="setuptools-18.3.2.tar.gz"
        python3_setup_dir=$(echo ${python3_setup%\.tar*})
        python3_pip="pip-7.1.2.tar.gz"
        python3_pip_dir=$(echo ${python3_pip%\.tar*})
    
        echo "=============== install dependence for Python 3 ============="
        yum install -y readline-devel sqlite xz-lzma gdbm-devel openssl-devel.i686 openssl.x86_64 \
            openssl-libs.x86_64 openssl-devel.x86_64 openssl.x86_64 openssl-static.i686 openssl-static.x86_64 \
            zlib-devel.i686 zlib-devel.x86_64 zlib-static.i686 zlib-static.x86_64 zlib.i686 zlib.x86_64
    
        # enable trap error
        trap 'Error_Trap ${LINENO}' ERR
    
        echo "=============== Compile Python 3 ============="
        tar Jxf ${python3_source}
        cd ${python3_source_dir}
        ./configure --prefix=/usr/local/ && make && make install
        sed -i "1c #!/usr/bin/${cur_python_version}" /usr/bin/yum
        sed -i "1c #!/usr/bin/${cur_python_version}" /usr/libexec/urlgrabber-ext-down
        cd -
    
        tar zxf ${python3_setup}
        cd ${python3_setup_dir}
        ${new_python_version} setup.py build && ${new_python_version} setup.py install
        cd -
    
        tar zxf ${python3_pip}
        cd ${python3_pip_dir}
        ${new_python_version} setup.py build && ${new_python_version} setup.py install
        cd -
    
        echo "=============== Compile Django ============="
        django_source="Django-1.8.5.tar.gz"
        django_source_dir=$(echo ${django_source%\.tar*})
        tar zxf ${django_source}
        cd ${django_source_dir}
        ${new_python_version} setup.py build && ${new_python_version} setup.py install
        cd -
    
        # disable trap error
        trap 'Error_Ignore ${LINENO}' ERR
        echo -e "\n\nDone......!!!!!!"
        #break
        ;;
        # end for base
    
    
    extra)
        trap 'Error_Trap ${LINENO}' ERR
        nginx_dir="nginx_install_in_centos7"
        cd ${installation_dir}
        cd ${nginx_dir}
        pwd
        echo "installing..."
        echo "=============== Install nginx ============="
        for i in $(ls nginx*el7*.rpm)
        do
            rpm -ivh $i
        done
        cd -
        echo "=============== Install mysql(mariadb) ============="
        yum install -y mariadb.x86_64 mariadb-devel.i686 mariadb-devel.x86_64 mariadb-libs.i686 mariadb-libs.x86_64 mariadb-server.x86_64 mariadb-test.x86_64
        yum install -y epel-release.noarch
        #break
        ;;
        # end for extra
    
    
    service)
        trap 'Error_Ignore ${LINENO}' ERR
        echo "=============== Disable firewall and selinux ============="
        #disable firewalld
        systemctl stop firewalld.service
        systemctl disable firewalld.service
    
        #disable selinux
        #selinux_file="/etc/sysconfig/selinux"
        #selinux_value="$(cat ${selinux_file} | grep "^SELINUX=" | awk -F'=' '{print $NF}')"
        #if [ "x${selinux_value}" == "xenforcing" ]
        #then
        #    sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' ${selinux_file}
        #elif [ "x${selinux_value}" == "xdisabled" ]
        #then
        #    echo "selinux is disabled"
        #else
        #    echo "SELINUX=disabled" >> ${selinux_file}
        #fi
        echo -e "\033[01;33mPlease disable selinux manually\033[0m"
        setenforce 0
        echo "You should reboot your system to make selinux-disabled enable"
    
        echo "============== enable mysql server ==================="
        #systemctl enable mysqld.service
        systemctl enable mariadb.service
        systemctl start mariadb.service
        echo -e '\033[01;32m
        ===================== Please Configure mariadb as follow ======================
        # then copy /usr/share/mysql/my-huge.cnf -> /etc/my.cnf
        # add "default-character-set=utf8" for [client];
        # add "character_set_server=utf8" for [mysqld];
        # add "prompt="\u@\h \d>" for [mysql];
        # then execute command "mysql_secure_installation" to setup root password
        # then restart mariadb.service and login by command
        # "mysql -uroot -pXXXXXX -P3306"(XXXXXX is the root password of mariadb)
        ===============================================================================
        \033[0m
        '
        #break
        ;;
        # end for service
    

    django)
        echo "add mysql(mariadb) information into settings.py after creating django project"
        echo "==================== mysql(mariadb) information as follow ====================
            DATABASES = {
            'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'architecture',
            'USER': 'root',
            'PASSWORD': '123456',
            #'HOST': 'localhost',
            'PORT': '3306',
            } }
            ===============================================================================
        "
        echo 'Because MySQL-python is not supported in python3, so use pymysql to replace it:
        1) pip3.5 install pymysql
        2) add "import pymysql; pymysql.install_as_MySQLdb()" into project_name/__init__.py
        3) python manage.py migrate
        '
        echo "
        [root@localhost performance-analysis]# pip3.5 install pymysql
        Collecting pymysql
          Downloading PyMySQL-0.6.7-py2.py3-none-any.whl (69kB)
              100% |████████████████████████████████| 73kB 442kB/s
              Installing collected packages: pymysql
              Successfully installed pymysql-0.6.7
        [root@localhost performance-analysis]# cat ArchApps/__init__.py
        import pymysql
        pymysql.install_as_MySQLdb()
        [root@localhost performance-analysis]# python manage.py migrate
        Operations to perform:
            Synchronize unmigrated apps: staticfiles, messages
            Apply all migrations: admin, auth, sessions, contenttypes
        Synchronizing apps without migrations:
            Creating tables...
                Running deferred SQL...
            Installing custom SQL...
        Running migrations:
            Rendering model states... DONE
            Applying contenttypes.0001_initial... OK
            Applying auth.0001_initial... OK
            Applying admin.0001_initial... OK
            Applying contenttypes.0002_remove_content_type_name... OK
            Applying auth.0002_alter_permission_name_max_length... OK
            Applying auth.0003_alter_user_email_max_length... OK
            Applying auth.0004_alter_user_username_opts... OK
            Applying auth.0005_alter_user_last_login_null... OK
            Applying auth.0006_require_contenttypes_0002... OK
            Applying sessions.0001_initial... OK
        "
        #break
        ;;
        # end for django

    *)
        Show_Usage
        exit 1
        ;;
esac
