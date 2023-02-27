# Auto_Create_MySQL
Auto Create MySQL Databases And construct master-slave(default MySQL 8.0.28)

本自动化MySQL主从部署基于MySQL 8.0.28版本。
1.脚本中目录结构可自行修改
2.my.cnf可自行提供，与脚本同目录即可，参数与配置不要有空格，如：
 read_only=1
 super_read_only=1
 
 执行案例：
  python3 auto_createDB.py  按照提示输入即可！
