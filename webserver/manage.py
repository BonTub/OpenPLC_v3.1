import os
from os.path import exists
from app import create_app, db, bcrypt
from flask_migrate import upgrade, migrate, init, stamp
from models import User
from sqlalchemy import exists 
app = create_app()
app.app_context().push()
db.create_all()
# migrate database to latest revision
if not os.path.exists("migrations"):
    init(
    )  # init the migration version database directory in migrations directory
stamp()
migrate()
upgrade()
# add a adminuser
adminuser = User(\
  username='openplc1',\
  email='openplc1@example.com',\
  pwd=bcrypt.generate_password_hash('openplc1')\
  )
try:
    #upserting adminuser
    #existing = db.session.query(User).filter_by(value=adminuser['username']).one()
    db.session.merge(adminuser)
    db.session.commit()
        
    #return existing
except Exception as e:
    print(e)
    db.session.rollback() # user exist if a integrity error
    #obj = User()

#end adminuser
