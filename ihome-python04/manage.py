
from flask import session
from flask_wtf import csrf

from ihome import db,create_app
from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand

# 创建flask的应用对象
app=create_app('develop')
manager=Manager(app)

Migrate(app,db)
manager.add_command('db',MigrateCommand)

# @app.route('/index')
# def index():
#     # session[]=
#     return 'index page'

if __name__ == '__main__':
    manager.run()