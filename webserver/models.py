from app import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = "user"
    
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    pwd = db.Column(db.String(300), nullable=False, unique=True)

    def __repr__(self):
        return '<User %r>' % self.username

class Users(UserMixin, db.Model):
    __tablename__ = "users"
    
    id  = db.Column(db.Integer(), primary_key=True)
    name     = db.Column(db.String(80), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email    = db.Column(db.String(120), unique=True, nullable=False)
    pwd = db.Column(db.String(300), nullable=False, unique=False)
    pict_file= db.Column(db.String(300), nullable=False, unique=False)

    def __repr__(self):
        return '<User %r>' % self.username

class Settings(UserMixin, db.Model):
    __tablename__ = "settings"

    Key     = db.Column(db.Integer(), primary_key=True)
    Value   = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return '<Setting() %r>' % self.Value

class Programs(UserMixin, db.Model):
    __tablename__ = "programs"

    Prog_ID     = db.Column(db.Integer(), primary_key=True)
    Name        = db.Column(db.String(80), unique=True, nullable=False)
    Description = db.Column(db.String(80), unique=True, nullable=True)
    File        = db.Column(db.String(80), unique=True, nullable=False)
    Date_upload = db.Column(db.Integer(), unique=False, nullable=False)

    def __repr__(self):
        return '<Programs() %r>' % self.Name

class Slave_dev(UserMixin, db.Model):
    __tablename__ = "slave_dev"

    dev_id      = db.Column(db.Integer(), primary_key=True)
    dev_name    = db.Column(db.String(80), unique=True, nullable=False)
    dev_type    = db.Column(db.String(80), unique=True, nullable=False)
    slave_id    = db.Column(db.Integer(), unique=False, nullable=False)
    com_port    = db.Column(db.String(80), unique=False, nullable=True)
    baud_rate   = db.Column(db.Integer(), unique=False, nullable=True)
    parity      = db.Column(db.String(8), unique=False, nullable=True)
    data_bits   = db.Column(db.Integer(), unique=False, nullable=True)
    stop_bits   = db.Column(db.Integer(), unique=False, nullable=True)
    ip_address  = db.Column(db.String(80), unique=False, nullable=True)
    ip_port     = db.Column(db.Integer(), unique=False, nullable=True)
    di_start    = db.Column(db.Integer(), unique=False, nullable=True)    
    di_size     = db.Column(db.Integer(), unique=False, nullable=True)
    coil_start  = db.Column(db.Integer(), unique=False, nullable=True)
    coil_size   = db.Column(db.Integer(), unique=False, nullable=True)      
    ir_start    = db.Column(db.Integer(), unique=False, nullable=True)
    ir_size     = db.Column(db.Integer(), unique=False, nullable=True)
    hr_read_start = db.Column(db.Integer(), unique=False, nullable=True)
    hr_read_size   = db.Column(db.Integer(), unique=False, nullable=True)
    hr_write_start = db.Column(db.Integer(), unique=False, nullable=True)
    hr_write_size  = db.Column(db.Integer(), unique=False, nullable=True)
    pause  = db.Column(db.Integer(), unique=False, nullable=True)

    def __repr__(self):
        return '<Slave_dev() %r>' % self.dev_name    
 
''' 
from alembic import op   
import sqlalchemy as sa                                                                                                                                                                                                                                                                    

    op.create_table('Settings',
    sa.Column('Key', sa.TEXT(), nullable=False),
    sa.Column('Value', sa.TEXT(), nullable=False),
    sa.PrimaryKeyConstraint('Key')
    )
    op.create_table('Programs',
    sa.Column('Prog_ID', sa.INTEGER(), nullable=False),
    sa.Column('Name', sa.TEXT(), nullable=False),
    sa.Column('Description', sa.TEXT(), nullable=True),
    sa.Column('File', sa.TEXT(), nullable=False),
    sa.Column('Date_upload', sa.INTEGER(), nullable=False),
    sa.PrimaryKeyConstraint('Prog_ID')
    )
    op.create_table('sqlite_sequence',
    sa.Column('name', sa.NullType(), nullable=True),
    sa.Column('seq', sa.NullType(), nullable=True)
    )
    op.create_table('Users',
    sa.Column('user_id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.TEXT(), nullable=False),
    sa.Column('username', sa.TEXT(), nullable=False),
    sa.Column('email', sa.TEXT(), nullable=True),
    sa.Column('password', sa.TEXT(), nullable=False),
    sa.Column('pict_file', sa.TEXT(), nullable=True),
    sa.PrimaryKeyConstraint('user_id')
    )
    op.create_table('Slave_dev',
    sa.Column('dev_id', sa.INTEGER(), nullable=False),
    sa.Column('dev_name', sa.TEXT(), nullable=False),
    sa.Column('dev_type', sa.TEXT(), nullable=False),
    sa.Column('slave_id', sa.INTEGER(), nullable=False),
    sa.Column('com_port', sa.TEXT(), nullable=True),
    sa.Column('baud_rate', sa.INTEGER(), nullable=True),
    sa.Column('parity', sa.TEXT(), nullable=True),
    sa.Column('data_bits', sa.INTEGER(), nullable=True),
    sa.Column('stop_bits', sa.INTEGER(), nullable=True),
    sa.Column('ip_address', sa.TEXT(), nullable=True),
    sa.Column('ip_port', sa.INTEGER(), nullable=True),
    sa.Column('di_start', sa.INTEGER(), nullable=False),
    sa.Column('di_size', sa.INTEGER(), nullable=False),
    sa.Column('coil_start', sa.INTEGER(), nullable=False),
    sa.Column('coil_size', sa.INTEGER(), nullable=False),
    sa.Column('ir_start', sa.INTEGER(), nullable=False),
    sa.Column('ir_size', sa.INTEGER(), nullable=False),
    sa.Column('hr_read_start', sa.INTEGER(), nullable=False),
    sa.Column('hr_read_size', sa.INTEGER(), nullable=False),
    sa.Column('hr_write_start', sa.INTEGER(), nullable=False),
    sa.Column('hr_write_size', sa.INTEGER(), nullable=False),
    sa.Column('pause', sa.INTEGER(), nullable=True),
    sa.PrimaryKeyConstraint('dev_id')
    ) '''


''' 
openplc.db fullschema

        sqlite3 openplc.db
SQLite version 3.31.1 2020-01-27 19:55:54
Enter ".help" for usage hints.
sqlite> .fullschema
CREATE TABLE IF NOT EXISTS "Users" (
        `user_id`       INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        `name`  TEXT NOT NULL,
        `username`      TEXT NOT NULL UNIQUE,
        `email` TEXT,
        `password`      TEXT NOT NULL,
        `pict_file`     TEXT
);
CREATE TABLE `Programs` (
        `Prog_ID`       INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        `Name`  TEXT NOT NULL,
        `Description`   TEXT,
        `File`  TEXT NOT NULL,
        `Date_upload`   INTEGER NOT NULL
);
CREATE TABLE `Settings` (
        `Key`   TEXT NOT NULL UNIQUE,
        `Value` TEXT NOT NULL,
        PRIMARY KEY(`Key`)
);
CREATE TABLE IF NOT EXISTS "Slave_dev" (
        "dev_id"        INTEGER NOT NULL UNIQUE,
        "dev_name"      TEXT NOT NULL UNIQUE,
        "dev_type"      TEXT NOT NULL,
        "slave_id"      INTEGER NOT NULL,
        "com_port"      TEXT,
        "baud_rate"     INTEGER,
        "parity"        TEXT,
        "data_bits"     INTEGER,
        "stop_bits"     INTEGER,
        "ip_address"    TEXT,
        "ip_port"       INTEGER,
        "di_start"      INTEGER NOT NULL,
        "di_size"       INTEGER NOT NULL,
        "coil_start"    INTEGER NOT NULL,
        "coil_size"     INTEGER NOT NULL,
        "ir_start"      INTEGER NOT NULL,
        "ir_size"       INTEGER NOT NULL,
        "hr_read_start" INTEGER NOT NULL,
        "hr_read_size"  INTEGER NOT NULL,
        "hr_write_start"        INTEGER NOT NULL,
        "hr_write_size" INTEGER NOT NULL,
        "pause" INTEGER,
        PRIMARY KEY("dev_id" AUTOINCREMENT)
);
/* No STAT tables available */ '''
