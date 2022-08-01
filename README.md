# partner
伙伴系统
配置说明
1.添加相应的python库，创建相应的数据库数据库，修改setting文件
DATABASES = {
     'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME':  'appdata',
        'USER': 'postgres',
        'PASSWORD': '250716',
        'HOST': 'localhost',
        'PORT': 5432,
     }
}

2.数据库迁移
python manage.py makemigrations
python manage.py migrate
