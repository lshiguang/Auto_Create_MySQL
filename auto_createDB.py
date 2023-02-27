# -*- coding=utf-8 -*-
#create by liduanfeng 202302
#call me 15019458909
#用途：自动化主从数据库部署

import  os
import subprocess
import  logging
import traceback
import  re
import sys
import  time

logfile = '/tmp/auto_createDB.log'
logging.basicConfig(level=logging.INFO,
                    filename=logfile,
                    filemode='a',
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')

def os_process(cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result = p.stdout.read()
    code = p.wait()
    return code,result




def modify_hostname(hostname):
    try:

        chmod_sq = ('sudo chmod 777 /etc/sysconfig/network')
        err=os.system(chmod_sq)
        if err == 0:
            logging.info('setup1.1: 修改/etc/sysconfig/network授权成功！')
            with open("/etc/sysconfig/network", "a") as f:
                f.write("NETWORKING=yes\n"
                        f"HOSTNAME= {hostname} ")
                logging.info('setup1.2: 修改/etc/sysconfig/network成功！')
                revoke_sq = ('sudo chmod 644 /etc/sysconfig/network')
                err=os.system(revoke_sq)
                if err ==0:
                    logging.info('setup1.3: 修改/etc/sysconfig/network回收成功！')
                else:
                    logging.error('setup1.3: 修改/etc/sysconfig/network回收失败！')
        else:
            logging.error('setup1.1: 修改/etc/sysconfig/network授权失败！')





    except:
        error_log = str(traceback.format_exc())
        logging.error('setup1.2: 修改/etc/sysconfig/network失败，原因为%s!' %error_log)
        sys.exit()

def modify_system(cmd):
    try:
        err = os.system(cmd)
        if err == 0:
            logging.info('setup1.4: set-hostname成功!')

        else:
            logging.error('setup1.4: set-hostname未成功')
    except:
        error_log = str(traceback.format_exc())
        logging.error('setup1.4: set-hostname失败，原因为%s!' %error_log)

def modify_hosts():
    j = 1
    total_machine = input("请输入需要安装主从机器个数：")
    total_machine = int(total_machine)
    print('主机顺序为master-slave1-slave2,注意ip和主机名之间需要空格隔开')
    while j <= total_machine:
        hostnamej = input("请第%s台主机的ip和主机名（如：127.0.0.1  localhost）:" %j)

        try:
            chmod_sq = ('sudo chmod 777 /etc/hosts')
            err = os.system(chmod_sq)
            if err == 0:
                with open("/etc/hosts", "a") as f:
                    f.write(hostnamej + '\n')
                    logging.info('setup1.5 加入/etc/hosts第%s台主机成功 ！' % j)
                    revoke_sq = ('sudo chmod 644 /etc/hosts')
                    err = os.system(revoke_sq)
                    if err == 0:
                        logging.info('setup1.6: 修改/etc/hosts回收成功！')
                    else:
                        logging.error('setup1.6: 修改/etc/hosts回收失败！')

        except:
            error_log = str(traceback.format_exc())
            logging.error('setup1.5 加入/etc/hosts第%s台主机失败！'%j)
        j += 1







def check_selinux_isdisable_and_disable_firewalld(cmd):
     with open("/etc/selinux/config","r") as f:
          contents = f.readlines()[6]
          content = contents[8:]
          if content.strip() == "disabled":
              logging.info('setup2.1 :SELINUX检查成功!')
          else:
              err = os.system(cmd)
              if err == 0:
                  logging.info('setup2.1: SELINUX设置为disabled')
              else:
                  logging.error('setup2.1: SELINUX未设置成功！')
     cmd = ["sudo systemctl stop firewalld","sudo systemctl disable firewalld"]
     for i in cmd:
         err = os.system(i)
         if err == 0:
             logging.info("setup2.2 %s 成功！" %i)
         else:
             logging.error("setup2.2 %s 失败，请检查！" %i)



def check_os_zonetime(cmd):
    code,result = os_process(cmd)
    if code == 0:
        res = result[26:31]
        if res == b'+0800':
            logging.info("setup3.1: 检查当前时区正确 %s" %result)
        else:
            print(res)
            logging.error("setup3.1: 当前时区不正确%s，请重新设置！" %result)
    else:
        logging.error("setup3.1: 当前时区不正确%s，请重新设置！" %result)


def install_os_pakeage():
    pakeage_list = ['cmake', 'make', 'gcc', 'gcc-c++',
                    'bison', 'ncurses', 'ncurses-devel',
                    'libaio*', 'net-tools', 'iotop', 'telnet',
                    'sysstat']
    for i in pakeage_list:
        code,result = os_process(f'rpm -qa |grep {i}')
        if code == 0:
            logging.info('setup4.1: %s 安装包检查成功！'%i)
        else:
            code,result= os_process(f'yum install {i} -y')
            if code == 0:
                logging.info('setup4.1: %s 安装包成功！' %i)

def create_db_dir():
    dir = ['/zxdata','/zxlog','/backup']
    for i in dir:
        if  os.path.exists(i) == True:
            logging.info('setup7.1 %s 目录已创建' %i)
        else:
            logging.error('setup7.1 %s 目录不存在' %i)
            break
    dir_list = ['sudo mkdir -p /zxdata/my3311/{data,etc,pid,socket,tmp,login}','sudo mkdir -p /zxlog/my3311/log','sudo mkdir -p /backup/my3311']
    for i in dir_list:
        if os.system(i) == 0:
            logging.info('setup7.2 %s 目录创建成功！' %i)
        else:
            logging.error('setup7.2 %s 目录创建失败！' %i)
            break
    authztion='sudo chown -R mysql:mysql /zxdata /zxlog /backup'
    if os.system(authztion) == 0 :
        logging.info('setup7.3 %s 目前授权成功！' %authztion)
    else:
        logging.error('setup7.3 %s 目前授权失败！' %authztion)
        sys.exit()


def check_mysql_pakeage_exists():
    if os.path.exists('/usr/local/mysql') == True:
        logging.info('setup8.1 MySQL源码包已存在！')
    else:
        logging.error('setup8.1 MySQL源码包不存在，请手动上传及解压！')

def create_mycnf():
    if os.path.exists('my.cnf') == True:
        logging.info('setup9.1 检查模板my.cnf已上传！')
        cp_cnf = 'cp my.cnf /zxdata/my3311/etc/'
        if os.system(cp_cnf) ==0:
            logging.info('setup9.2 copy my.cnf到/zxdata/my3311/etc 成功！')
            server_id = input("请输入server_id: ")
            read_only = input("是否设置只读(8.0.28版本特殊性，先设置为0: ")
            replica_parallel_workers = input("设置复制并行度（8C = 4,32C = 8）: ")
            buffer_size = input("设置buffer_pool大小，单位为G（如输入: 2G）: ")
            buffer_instance = input("设置buffer instance个数: ")
            read_io_thread = input("设置write and read io threads(默认4，8C - 16C配置8，16C以上为16: )")
            code,result = os_process('free -g')
            if code == 0:
                ret1, ret2, ret3, ret4 = str(result).split('\\n')
                memory = ret2[18]
            else:
                logging.error('setup9.3 获取操作系统内存异常！')


            code,result = os_process('cat /proc/cpuinfo| grep "processor"| wc -l')
            if code == 0:
                cpu = str(result).strip("'b'")
                cpu = str(cpu).split('\\n')
                cpu = cpu[0]
            else:
                logging.error('setup9.3 获取操作系统cpu异常！')
            memory = int(memory)
            cpu = int(cpu)

            if memory >= 15 and memory<= 16 and cpu ==8:
                err1 = os.system(f"sed -i 's/^server_id=.*$/server_id={server_id}/g' /zxdata/my3311/etc/my.cnf")
                err2 = os.system(f"sed -i 's/^read_only=.*$/read_only={read_only}/g' /zxdata/my3311/etc/my.cnf")
                err3 = os.system(
                    f"sed -i 's/^super_read_only=.*$/super_read_only={read_only}/g' /zxdata/my3311/etc/my.cnf")
                err4 = os.system(
                    f"sed -i 's/^replica_parallel_workers=.*$/replica_parallel_workers={replica_parallel_workers}/g' /zxdata/my3311/etc/my.cnf")
                err5 = os.system(
                    f"sed -i 's/^innodb_buffer_pool_size=.*$/innodb_buffer_pool_size={buffer_size}/g' /zxdata/my3311/etc/my.cnf")
                err6 = os.system(
                    f"sed -i 's/^innodb_buffer_pool_instances=.*$/innodb_buffer_pool_instances={buffer_instance}/g' /zxdata/my3311/etc/my.cnf")
                err7 = os.system(
                    f"sed -i 's/^innodb_read_io_threads=.*$/innodb_read_io_threads={read_io_thread}/g' /zxdata/my3311/etc/my.cnf")
                err8 = os.system(
                    f"sed -i 's/^innodb_write_io_threads=.*$/innodb_write_io_threads={read_io_thread}/g' /zxdata/my3311/etc/my.cnf")
                if err1 == 0 and err2 == 0 and err3 == 0 and err4 == 0 and err5 == 0 and err6 == 0 and err7 == 0 and err8 == 0:
                    logging.info('setup9.4 当前内存16G，cpu 8C my.cnf设置完成！')
                else:
                    logging.error('setup9.4 当前内存16G，cpu 8C my.cnf设置失败！')


            elif memory >=7 and memory <=8 and cpu ==4:
                err1=os.system(f"sed -i 's/^server_id=.*$/server_id={server_id}/g' /zxdata/my3311/etc/my.cnf")
                err2 =os.system(f"sed -i 's/^read_only=.*$/read_only={read_only}/g' /zxdata/my3311/etc/my.cnf")
                err3 =os.system(f"sed -i 's/^super_read_only=.*$/super_read_only={read_only}/g' /zxdata/my3311/etc/my.cnf")
                err4 =os.system(f"sed -i 's/^replica_parallel_workers=.*$/replica_parallel_workers={replica_parallel_workers}/g' /zxdata/my3311/etc/my.cnf")
                err5 =os.system(f"sed -i 's/^innodb_buffer_pool_size=.*$/innodb_buffer_pool_size={buffer_size}/g' /zxdata/my3311/etc/my.cnf")
                err6 =os.system(f"sed -i 's/^innodb_buffer_pool_instances=.*$/innodb_buffer_pool_instances={buffer_instance}/g' /zxdata/my3311/etc/my.cnf")
                err7 =os.system(
                    f"sed -i 's/^innodb_read_io_threads=.*$/innodb_read_io_threads={read_io_thread}/g' /zxdata/my3311/etc/my.cnf")
                err8 =os.system(
                    f"sed -i 's/^innodb_write_io_threads=.*$/innodb_write_io_threads={read_io_thread}/g' /zxdata/my3311/etc/my.cnf")

                err9 =os.system("sed -i 's/^max_connections=.*$/max_connections=1024/g' /zxdata/my3311/etc/my.cnf")
                err10 =os.system("sed -i 's/^max_user_connections=.*$/max_user_connections=512/g' /zxdata/my3311/etc/my.cnf")
                err11 =os.system("sed -i 's/^table_open_cache=.*$/table_open_cache=4096/g' /zxdata/my3311/etc/my.cnf")
                err12 =os.system("sed -i 's/^table_definition_cache=.*$/table_definition_cache=4096/g' /zxdata/my3311/etc/my.cnf")
                err13 =os.system("sed -i 's/^tmp_table_size=.*$/tmp_table_size=16M/g' /zxdata/my3311/etc/my.cnf")
                err14 =os.system("sed -i 's/^max_heap_table_size=.*$/max_heap_table_size=16M/g' /zxdata/my3311/etc/my.cnf")
                err15 =os.system("sed -i 's/^join_buffer_size=.*$/join_buffer_size=1M/g' /zxdata/my3311/etc/my.cnf")
                err16 =os.system("sed -i 's/^read_rnd_buffer_size=.*$/read_rnd_buffer_size=4M/g' /zxdata/my3311/etc/my.cnf")
                err17 =os.system("sed -i 's/^table_open_cache_instances=.*$/table_open_cache_instances=8/g' /zxdata/my3311/etc/my.cnf")
                err18 =os.system("sed -i 's/^bulk_insert_buffer_size=.*$/bulk_insert_buffer_size=32M/g' /zxdata/my3311/etc/my.cnf")
                if err1 == 0 and err2 == 0 and err3 ==0 and err4 ==0 and err5==0 and err6==0 and err7==0 and err8==0 and err9==0 and err10 ==0 and err11 == 0 and err12 ==0 and err13 ==0 and err14 ==0 and err15==0 and err16==0 and err17==0 and err18==0:
                    logging.info('setup9.4 当前内存8G，cpu 4C my.cnf设置完成！')
                else:
                    logging.error('setup9.4 当前内存8G，cpu 4C my.cnf设置失败！')

            elif memory >=3 and memory <=4 and cpu ==2:
                err1=os.system(f"sed -i 's/^server_id=.*$/server_id={server_id}/g' /zxdata/my3311/etc/my.cnf")
                err2 =os.system(f"sed -i 's/^read_only=.*$/read_only={read_only}/g' /zxdata/my3311/etc/my.cnf")
                err3 =os.system(f"sed -i 's/^super_read_only=.*$/super_read_only={read_only}/g' /zxdata/my3311/etc/my.cnf")
                err4 =os.system(
                    f"sed -i 's/^replica_parallel_workers=.*$/replica_parallel_workers={replica_parallel_workers}/g' /zxdata/my3311/etc/my.cnf")
                err5 =os.system(
                    f"sed -i 's/^innodb_buffer_pool_size=.*$/innodb_buffer_pool_size={buffer_size}/g' /zxdata/my3311/etc/my.cnf")
                err6 =os.system(
                    f"sed -i 's/^innodb_buffer_pool_instances=.*$/innodb_buffer_pool_instances={buffer_instance}/g' /zxdata/my3311/etc/my.cnf")
                err7 =os.system(
                    f"sed -i 's/^innodb_read_io_threads=.*$/innodb_read_io_threads={read_io_thread}/g' /zxdata/my3311/etc/my.cnf")
                err8 =os.system(
                    f"sed -i 's/^innodb_write_io_threads=.*$/innodb_write_io_threads={read_io_thread}/g' /zxdata/my3311/etc/my.cnf")

                err9 =os.system("sed -i 's/^max_connections=.*$/max_connections=512/g' /zxdata/my3311/etc/my.cnf")
                err10 =os.system("sed -i 's/^max_user_connections=.*$/max_user_connections=256/g' /zxdata/my3311/etc/my.cnf")
                err11 =os.system("sed -i 's/^table_open_cache=.*$/table_open_cache=1024/g' /zxdata/my3311/etc/my.cnf")
                err12 =os.system("sed -i 's/^table_definition_cache=.*$/table_definition_cache=1024/g' /zxdata/my3311/etc/my.cnf")
                err13 =os.system("sed -i 's/^tmp_table_size=.*$/tmp_table_size=8M/g' /zxdata/my3311/etc/my.cnf")
                err14 =os.system("sed -i 's/^max_heap_table_size=.*$/max_heap_table_size=8M/g' /zxdata/my3311/etc/my.cnf")
                err15 =os.system("sed -i 's/^join_buffer_size=.*$/join_buffer_size=1M/g' /zxdata/my3311/etc/my.cnf")
                err16 =os.system("sed -i 's/^read_rnd_buffer_size=.*$/read_rnd_buffer_size=1M/g' /zxdata/my3311/etc/my.cnf")
                err17 =os.system("sed -i 's/^table_open_cache_instances=.*$/table_open_cache_instances=4/g' /zxdata/my3311/etc/my.cnf")
                err18 =os.system("sed -i 's/^bulk_insert_buffer_size=.*$/bulk_insert_buffer_size=32M/g' /zxdata/my3311/etc/my.cnf")
                err19 =os.system( "sed -i 's/^key_buffer_size=.*$/key_buffer_size=16M/g' /zxdata/my3311/etc/my.cnf")
                err20 =os.system("sed -i 's/^read_buffer_size=.*$/read_buffer_size=1M/g' /zxdata/my3311/etc/my.cnf")
                err21 =os.system("sed -i 's/^sort_buffer_size=.*$/sort_buffer_size=1M/g' /zxdata/my3311/etc/my.cnf")
                if err1 == 0 and err2 == 0 and err3 ==0 and err4 ==0 and err5==0 and err6==0 and err7==0 and err8==0 and err9==0 and err10 ==0 and err11 == 0 and err12 ==0 and err13 ==0 and err14 ==0 and err15==0 and err16==0 and err17==0 and err18==0 and err19==0 and err20==0 and err21==0:
                    logging.info('setup9.4 当前内存8G，cpu 4C my.cnf设置完成！')
                else:
                    logging.error('setup9.4 当前内存8G，cpu 4C my.cnf设置失败！')

            else:
                print('机器配置不在默认列表中,按照8C16G配置')
                err1 = os.system(f"sed -i 's/^server_id=.*$/server_id={server_id}/g' /zxdata/my3311/etc/my.cnf")
                err2 = os.system(f"sed -i 's/^read_only=.*$/read_only={read_only}/g' /zxdata/my3311/etc/my.cnf")
                err3 = os.system(
                    f"sed -i 's/^super_read_only=.*$/super_read_only={read_only}/g' /zxdata/my3311/etc/my.cnf")
                err4 = os.system(
                    f"sed -i 's/^replica_parallel_workers=.*$/replica_parallel_workers={replica_parallel_workers}/g' /zxdata/my3311/etc/my.cnf")
                err5 = os.system(
                    f"sed -i 's/^innodb_buffer_pool_size=.*$/innodb_buffer_pool_size={buffer_size}/g' /zxdata/my3311/etc/my.cnf")
                err6 = os.system(
                    f"sed -i 's/^innodb_buffer_pool_instances=.*$/innodb_buffer_pool_instances={buffer_instance}/g' /zxdata/my3311/etc/my.cnf")
                err7 = os.system(
                    f"sed -i 's/^innodb_read_io_threads=.*$/innodb_read_io_threads={read_io_thread}/g' /zxdata/my3311/etc/my.cnf")
                err8 = os.system(
                    f"sed -i 's/^innodb_write_io_threads=.*$/innodb_write_io_threads={read_io_thread}/g' /zxdata/my3311/etc/my.cnf")
                if err1 == 0 and err2 == 0 and err3 == 0 and err4 == 0 and err5 == 0 and err6 == 0 and err7 == 0 and err8 == 0:
                    logging.info('setup9.4 当前内存%s G，cpu %s my.cnf设置完成！' %(memory,cpu))
                else:
                    logging.error('setup9.4 当前内存%s G，cpu %s C my.cnf设置失败！' %(memory,cpu))


        else:
            logging.error('setup9.2 copy my.cnf到/zxdata/my3311/etc 失败！')
    else:
        logging.error('setup9.1 检查模板my.cnf未上传，请手动上传！')
        print('setup9.1 检查模板my.cnf未上传，请手动上传！')
def init_db():
    err,result=os_process('/usr/local/mysql/bin/mysqld --defaults-file=/zxdata/my3311/etc/my.cnf --initialize --basedir=/usr/local/mysql --datadir=/zxdata/my3311/data/ --explicit_defaults_for_timestamp --user=mysql')
    if err == 0:
        logging.info('setup10.1 数据库初始化完成！')
        err,result = os_process("grep 'A temporary password is' /zxlog/my3311/log/error.log")
        if err == 0:
            passwd = str(result).strip("'b'")
            passwd = str(passwd).split('\\n')
            passwd1 = passwd[-2]
            passwd2 = str(passwd1).split(' ')

            passwd = passwd2[-1]
            logging.info('setup10.2 获取数据库初始密码为: %s' %passwd)
        else:
            logging.error('setup10.2 获取数据库初始密码失败！')
        err=os.system("/usr/local/mysql/bin/mysqld_safe --defaults-file=/zxdata/my3311/etc/my.cnf &") #subprocess.Popen会处于等待
        if err == 0:
            code,result=os_process('ps -ef |grep mysqld|wc -l')
            result1 = str(result).strip("'b'")
            result2 = str(result1).split('\\n')
            # print(result2[0])
            if code == 0 and int(result2[0]) == 3:
                logging.info('setup10.3 启动数据库成功！')
                time.sleep(10)
                with open('/zxlog/my3311/log/error.log', 'r') as f:
                    lines = f.readlines()
                    for j in lines:
                        line = re.search('ERROR',
                                         j)
                        if line:
                            logging.error('setup10.4 检查error.log存在异常，请检查错误日志！ %s' % line)
                            sys.exit()
                logging.info('setup10.4 检查error.log正常！')
            else:
                logging.error('setup10.4 启动数据库失败，进程个数有误' )
                sys.exit()

        else:
            logging.error('setup10.3 启动数据库失败，失败原因: %s' %result)
        user = 'root'
        localhost = 'localhost'
        new_passwd = input("请输入root新密码（输入格式: 'mysql'）: ")
        modify_sql = f'/usr/local/mysql/bin/mysql -uroot -p"{passwd}" -S /zxdata/my3311/socket/mysql.sock --connect-expired-password -e "alter user {user}@{localhost} identified by {new_passwd};reset master;"'

        err,result=os_process(modify_sql)

        if err ==0:
            logging.info('setup10.5 root用户密码修改成功!')
            logging.info('setup10.6 开始创建复制和备份用户！')
            repl_passwd = input("请输入复制用户密码（输入格式: 'repl'）：")
            backup_passwd = input("请输入备份用户密码（输入格式: 'backup'）：")
            monitor_passwd = input("请输入监控用户密码（输入格式: 'monitor'）：")
            host1 = input("请输入复制及备份用户host地址，请输入 '%': ")
            host2 = input("请输入监控用户host地址，请输入 '127.0.0.1': ")
            create_user = f'/usr/local/mysql/bin/mysql -uroot -p{new_passwd} -S /zxdata/my3311/socket/mysql.sock --connect-expired-password -e "set SQL_LOG_BIN=0;create user repl@{host1} identified by {repl_passwd};create user zxbackup@{host1}  identified by {backup_passwd};grant replication slave on *.* to repl@{host1} ;GRANT RELOAD, PROCESS, LOCK TABLES, REPLICATION CLIENT ON *.* TO zxbackup@{host1} ;GRANT BACKUP_ADMIN ON *.* TO zxbackup@{host1} ;GRANT SELECT ON performance_schema.log_status TO zxbackup@{host1}  ;create user zabbix@{host2} identified by {monitor_passwd}; GRANT SELECT, PROCESS, REPLICATION CLIENT ON *.* TO zabbix@{host2};FLUSH PRIVILEGES; SET SQL_LOG_BIN=1;"'

            err,result = os_process(create_user)

            if err == 0:
                logging.info('setup10.6 复制用户、备份用户、监控用户创建成功！')
                logging.info('setup10.7 开始建立主从关系！')
                dy_zc = input("请选择当前节点是主or从，请输入M or S（M：master，S：slave）:")
                dy_zc = str(dy_zc)
                if dy_zc == "S":
                    err1 = os.system("sed -i 's/^read_only=.*$/super_read_only=1/g' /zxdata/my3311/etc/my.cnf")
                    err2 = os.system("sed -i 's/^super_read_only=.*$/super_read_only=1/g' /zxdata/my3311/etc/my.cnf")

                    if err1 ==0 and err2 ==0:
                        logging.info("setup10.8 修改my.cnf Slave read_only成功!")
                        modify_readonly = f'/usr/local/mysql/bin/mysql -uroot -p{new_passwd} -S /zxdata/my3311/socket/mysql.sock --connect-expired-password -e "set global super_read_only=1; set global read_only=1;"'
                        err,result=os_process(modify_readonly)
                        if err ==0:
                            logging.info("setup10.9 开启Slave read_only成功!")
                            master_host = input("请输入master ip（输入格式: '21.93.101.101'）: ")
                            master_repl_user = input("请输入master 复制用户（输入格式: 'repl'）: ")
                            change_master = f'/usr/local/mysql/bin/mysql -uroot -p{new_passwd} -S /zxdata/my3311/socket/mysql.sock --connect-expired-password -e "change master to master_host={master_host},master_port=3311,master_user={master_repl_user},master_password={repl_passwd},master_auto_position=1;start slave;"'

                            err, result = os_process(change_master)

                            if err == 0:
                                logging.info("setup10.9 change master成功！")
                                confirm_slave_status = f'/usr/local/mysql/bin/mysql -uroot -p{new_passwd} -S /zxdata/my3311/socket/mysql.sock   -e "show slave status\G;"'
                                err,result=os_process(confirm_slave_status)

                                if err ==0:
                                    result1=str(result).split("\\n")

                                    logging.info("setup10.10 master_host=[%s],主从状态为: %s %s" %(result1[3],result1[12],result1[13]))

                                else:
                                    logging.error("setup10.10 master_host=[%s],主从状态为: %s %s" %(result1[3],result1[12],result1[13]))

                            else:
                                logging.error("setup10.9 change master 失败！ %s" % result)
                        else:
                            logging.error("setup10.9 开启Slave read_only失败 %s!" %result)


                    else:
                        logging.error("setup10.8 修改my.cnf Slave read_only失败!")
                elif dy_zc == "M":
                    logging.info("setup 10.8 主节点不需要操作！")

                else:
                    logging.error("节点选择，输入有误！")
            else:
                logging.error('setup10.6 复制用户、备份用户、监控用户创建失败！')
        else:
            logging.error('setup10.5 root用户密码修改失败!')


    else:
        logging.error('setup10.1 数据库初始化失败 %s' %result)
if  __name__ == '__main__':
    print('----------------------------部署开始----------------------------')
    logging.info('setup1: 修改主机名')
    hostname = input("请输入hostname: ")
    modify_hostname(hostname)
    modify_system(f"sudo hostnamectl  set-hostname  {hostname}")
    modify_hosts()
    logging.info('setup2：检查防火墙和selinux')
    check_selinux_isdisable_and_disable_firewalld("sudo sed -i 's/^SELINUX=.*$/SELINUX=disabled/g' /etc/selinux/config")
    logging.info('setup3：检查操作系统时区')
    check_os_zonetime('date -R')
    logging.info('setup4: 安装系统包')
    install_os_pakeage()
    logging.info('setup5：操作系统参数调整，模板已设置，此步忽略')
    logging.info('setup6：创建MySQL用户及组，模板已设置，此步忽略')
    logging.info('setup7: 创建安装目录及授权')
    create_db_dir()
    logging.info('setup8：检查MySQL包是否存在')
    check_mysql_pakeage_exists()
    logging.info('setup9：创建参数文件')
    create_mycnf()
    logging.info('setup10: 数据库初始化开始')
    init_db()
    logging.info('setup11: 部署完成！')
    print('----------------------------部署完成----------------------------')



