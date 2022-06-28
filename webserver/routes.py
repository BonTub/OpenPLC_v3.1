
from ast import Pass
from datetime import timedelta
from this import d
from sqlalchemy.exc import (
    IntegrityError,
    DataError,
    DatabaseError,
    InterfaceError,
    InvalidRequestError,
)
from flask import (Flask, render_template, redirect, flash, url_for, session)

from werkzeug.routing import BuildError

from flask_bcrypt import Bcrypt, generate_password_hash, check_password_hash

from flask_login import (
    UserMixin,
    login_user,
    LoginManager,
    current_user,
    logout_user,
    login_required,
)

from app import create_app, login_manager, bcrypt
# import models
from models import db
from models import User
from models import Setting
from forms import login_form, register_form, setting_form

from openplc import openplc_runtime, configure_runtime


app = create_app()
# init_app(app) see manage.py
# app.app_context().push()


# configure_openplc(app)
# openplc_runtime = openplc.runtime()
configure_runtime(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Unauthorized'


@app.before_request
def session_handler():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=10)

@app.route("/home", methods=("GET", "POST"), strict_slashes=False)
@app.route("/", methods=("GET", "POST"), strict_slashes=False)
def index():
    if current_user.is_authenticated:
        return render_template("dashboard.html", title="OpenPLC_V3.1 Home", user=current_user)
    else:
        return redirect(url_for('login'))
    
@app.route("/programs", methods=("GET", "POST"), strict_slashes=False)
def program():
    if current_user.is_authenticated:
        return render_template("programs.html", title="OpenPLC_V3.1 Programs", user=current_user)
    else:
        return redirect(url_for('login'))

from flask import stream_with_context, request, Response

@app.route('/runtime_logs', strict_slashes=False)
def streamed_response():
    @stream_with_context
    def generate():
        yield 'Hello RUNTIME_LOGS '
        yield request.args['name']
        yield '!'
    return Response(generate())

@app.route("/login/", methods=("GET", "POST"), strict_slashes=False)
def login():
    form = login_form()

    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=form.email.data).first()
            if check_password_hash(user.pwd, form.pwd.data):
                login_user(user)
                return redirect(url_for('index'))
            else:
                flash("Invalid Username or password!", "danger")
        except Exception as e:
            flash(e, "danger")

    return render_template("auth.html",
                           form=form,
                           text="Login",
                           title="Login",
                           btn_action="Login"
                           )


# Register route
@app.route("/register/", methods=("GET", "POST"), strict_slashes=False)
def register():
    form = register_form()
    if form.validate_on_submit():
        try:
            email = form.email.data
            pwd = form.pwd.data
            username = form.username.data

            newuser = User(
                username=username,
                email=email,
                pwd=bcrypt.generate_password_hash(pwd),
            )

            db.session.add(newuser)
            db.session.commit()
            flash("Account Succesfully created ", "success")
            return redirect(url_for("login"))

        except InvalidRequestError:
            db.session.rollback()
            flash("Something went wrong! ", "danger")
        except IntegrityError:
            db.session.rollback()
            flash("User already exists! ", "warning")
        except DataError:
            db.session.rollback()
            flash("Invalid Entry", "warning")
        except InterfaceError:
            db.session.rollback()
            flash("Error connecting to the database", "danger")
        except DatabaseError:
            db.session.rollback()
            flash("Error connecting to the database", "danger")
        except BuildError:
            db.session.rollback()
            flash("An error occured !", "danger")
    return render_template("auth.html",
                           form=form,
                           text="Create account",
                           title="Register",
                           btn_action="Register account",
                           )

# crud settings table
@app.route('/settings/update', methods=['POST'])
def update_settings():
    #firstname = request.form['updatefirstname']
    #lastname = request.form['updatelastname']
    #phone_no = request.form['updatephone_no']
    #contact_id = request.form['contact_id']
    form = setting_form()

    if form.validate_on_submit():
        try:
            id  = form.key.id
            key = form.key.data
            value = form.value.data
            newsetting = Setting(
                id=id,
                key=key,
                value=value,
            )

            db.session.update(newsetting)
            db.session.commit()
            flash("Setting created ", "success")
            return redirect(url_for("settings"))

        except InvalidRequestError:
            db.session.rollback()
            flash("Something went wrong! ", "danger")
        except IntegrityError:
            db.session.rollback()
            flash("Record already exists! ", "warning")
        except DataError:
            db.session.rollback()
            flash("Invalid Entry", "warning")
        except InterfaceError:
            db.session.rollback()
            flash("Error connecting to the database", "danger")
        except DatabaseError:
            db.session.rollback()
            flash("Error connecting to the database", "danger")
        except BuildError:
            db.session.rollback()
            flash("An error occured !", "danger")
    # cur.execute("update contacts SET firstname = %s , lastname = %s , phone_no = %s  WHERE contact_id = %s" , (firstname,lastname,phone_no,contact_id));
    # conn.commit();
    return redirect(url_for('settings'))  



@app.route('/settings/', methods=['GET', 'POST'])
@app.route('/settings/<crud_method>/<item_id>', methods=['GET'])
def settings( item_id = None, crud_method = None):
    item_id = item_id or ''
    crud_method = crud_method or ''
    #if not current_user.is_authenticated:
    #    return redirect(url_for('login'))
    
    # monitor.stop_monitor()
    # if (openplc_runtime.status() == "Compiling"):
        # return draw_compiling_page()
        # return flask.redirect(flask.url_for('draw_compiling_page'))


    try:
        # a list
        result = db.session.query(Setting).all()
    except:
        print("db session settings trouble")

    form = setting_form()

    if (item_id != ''):
        if (crud_method == 'edit'):
            # obj = Setting.query.filter_by(id=item_id).one()
            obj = Setting.query.get(item_id)
            print(obj)
            return render_template("setting.html",
                                  form=form,
                                  text="Edit Setting",
                                  title="Setting",
                                  btn_action="Edit Setting",
                                  data=result,
                                  item=item_id,
                                  )
        if (crud_method == 'delete'):
            # obj = Setting.query.filter_by(id=item_id).one()
            obj = Setting.query.get(item_id)
            db.session.delete(obj)
            db.session.commit()
        return redirect(url_for('settings'))


    if form.validate_on_submit():
        try:
            key = form.key.data
            value = form.value.data
            newsetting = Setting(
                key=key,
                value=value,
            )

            db.session.add(newsetting)
            db.session.commit()
            flash("Setting created ", "success")
            return redirect(url_for("settings"))

        except InvalidRequestError:
            db.session.rollback()
            flash("Something went wrong! ", "danger")
        except IntegrityError:
            db.session.rollback()
            flash("Record already exists! ", "warning")
        except DataError:
            db.session.rollback()
            flash("Invalid Entry", "warning")
        except InterfaceError:
            db.session.rollback()
            flash("Error connecting to the database", "danger")
        except DatabaseError:
            db.session.rollback()
            flash("Error connecting to the database", "danger")
        except BuildError:
            db.session.rollback()
            flash("An error occured !", "danger")

    return render_template("setting.html",
                           form=form,
                           text="Create Setting",
                           title="Setting",
                           btn_action="add Setting",
                           data=result,
                           )
         
    if (flask.request.method == 'GET'):
        return_str = pages.w3_style + pages.settings_style + draw_top_div() + pages.settings_head
        return_str += draw_status()
        return_str += """
        </div>
        <div style="margin-left:320px; margin-right:70px">
            <div style="w3-container">
                <br>
                <h2>Settings</h2>
                <form id        = "uploadForm"
                    enctype     = "multipart/form-data"
                    action      = "settings"
                    method      = "post"
                    onsubmit    = "return validateForm()">
                    
                    <label class="container">
                        <b>Enable Modbus Server</b>"""
        
        database = "openplc.db"
        conn = create_connection(database)
        if (conn != None):
            try:
                cur = conn.cursor()
                cur.execute("SELECT * FROM Settings")
                rows = cur.fetchall()
                cur.close()
                conn.close()
                
                for row in rows:
                    if (row[0] == "Modbus_port"):
                        modbus_port = str(row[1])
                    elif (row[0] == "Dnp3_port"):
                        dnp3_port = str(row[1])
                    elif (row[0] == "Enip_port"):
                        enip_port = str(row[1])
                    elif (row[0] == "Pstorage_polling"):
                        pstorage_poll = str(row[1])
                    elif (row[0] == "Start_run_mode"):
                        start_run = str(row[1])
                    elif (row[0] == "Slave_polling"):
                        slave_polling = str(row[1])
                    elif (row[0] == "Slave_timeout"):
                        slave_timeout = str(row[1])
                
                if (modbus_port == 'disabled'):
                    return_str += """
                        <input id="modbus_server" type="checkbox">
                        <span class="checkmark"></span>
                    </label>
                    <label for='modbus_server_port'><b>Modbus Server Port</b></label>
                    <input type='text' id='modbus_server_port' name='modbus_server_port' value='502'>"""
                else:
                    return_str += """
                        <input id="modbus_server" type="checkbox" checked>
                        <span class="checkmark"></span>
                    </label>
                    <label for='modbus_server_port'><b>Modbus Server Port</b></label>
                    <input type='text' id='modbus_server_port' name='modbus_server_port' value='""" + modbus_port + "'>"
                    
                return_str += """
                    <br>
                    <br>
                    <br>
                    <label class="container">
                        <b>Enable DNP3 Server</b>"""
                
                if (dnp3_port == 'disabled'):
                    return_str += """
                        <input id="dnp3_server" type="checkbox">
                        <span class="checkmark"></span>
                    </label>
                    <label for='dnp3_server_port'><b>DNP3 Server Port</b></label>
                    <input type='text' id='dnp3_server_port' name='dnp3_server_port' value='20000'>"""
                else:
                    return_str += """
                        <input id="dnp3_server" type="checkbox" checked>
                        <span class="checkmark"></span>
                    </label>
                    <label for='dnp3_server_port'><b>DNP3 Server Port</b></label>
                    <input type='text' id='dnp3_server_port' name='dnp3_server_port' value='""" + dnp3_port + "'>"
                
                return_str += """
                    <br>
                    <br>
                    <br>
                    <label class="container">
                        <b>Enable EtherNet/IP Server</b>"""
                        
                if (enip_port == 'disabled'):
                    return_str += """
                        <input id="enip_server" type="checkbox">
                        <span class="checkmark"></span>
                    </label>
                    <label for='enip_server_port'><b>EtherNet/IP Server Port</b></label>
                    <input type='text' id='enip_server_port' name='enip_server_port' value='44818'>"""
                else:
                    return_str += """
                        <input id="enip_server" type="checkbox" checked>
                        <span class="checkmark"></span>
                    </label>
                    <label for='enip_server_port'><b>EtherNet/IP Server Port</b></label>
                    <input type='text' id='enip_server_port' name='enip_server_port' value='""" + enip_port + "'>"
                
                return_str += """
                    <br>
                    <br>
                    <br>
                    <label class="container">
                        <b>Enable Persistent Storage Thread</b>"""
                        
                if (pstorage_poll == 'disabled'):
                    return_str += """
                        <input id="pstorage_thread" type="checkbox">
                        <span class="checkmark"></span>
                    </label>
                    <label for='pstorage_thread_poll'><b>Persistent Storage polling rate</b></label>
                    <input type='text' id='pstorage_thread_poll' name='pstorage_thread_poll' value='10'>"""
                else:
                    return_str += """
                        <input id="pstorage_thread" type="checkbox" checked>
                        <span class="checkmark"></span>
                    </label>
                    <label for='pstorage_thread_poll'><b>Persistent Storage polling rate</b></label>
                    <input type='text' id='pstorage_thread_poll' name='pstorage_thread_poll' value='""" + pstorage_poll + "'>"
                
                return_str += """
                    <br>
                    <br>
                    <br>
                    <label class="container">
                        <b>Start OpenPLC in RUN mode</b>"""
                        
                if (start_run == 'false'):
                    return_str += """
                        <input id="auto_run" type="checkbox">
                        <span class="checkmark"></span>
                    </label>
                    <input type='hidden' value='false' id='auto_run_text' name='auto_run_text'/>"""
                else:
                    return_str += """
                        <input id="auto_run" type="checkbox" checked>
                        <span class="checkmark"></span>
                    </label>
                    <input type='hidden' value='true' id='auto_run_text' name='auto_run_text'/>"""
                
                return_str += """
                    <br>
                    <h2>Slave Devices</h2>
                    <label for='slave_polling_period'><b>Polling Period (ms)</b></label>
                    <input type='text' id='slave_polling_period' name='slave_polling_period' value='""" + slave_polling + "'>"
                
                return_str += """
                    <br>
                    <br>
                    <br>
                    <label for='slave_timeout'><b>Timeout (ms)</b></label>
                    <input type='text' id='slave_timeout' name='slave_timeout' value='""" + slave_timeout + "'>"
                
                return_str += pages.settings_tail
                
            except Error as e:
                return_str += "error connecting to the database" + str(e)
        else:
            return_str += "Error opening DB"
        return return_str
    elif (flask.request.method == 'POST'):
        modbus_port = flask.request.form.get('modbus_server_port')
        dnp3_port = flask.request.form.get('dnp3_server_port')
        enip_port = flask.request.form.get('enip_server_port')
        pstorage_poll = flask.request.form.get('pstorage_thread_poll')
        start_run = flask.request.form.get('auto_run_text')
        slave_polling = flask.request.form.get('slave_polling_period')
        slave_timeout = flask.request.form.get('slave_timeout')
        
        (modbus_port, dnp3_port, enip_port, pstorage_poll, start_run, slave_polling, slave_timeout) = sanitize_input(modbus_port, dnp3_port, enip_port, pstorage_poll, start_run, slave_polling, slave_timeout)
        database = "openplc.db"
        conn = create_connection(database)
        if (conn != None):
            try:
                cur = conn.cursor()
                if (modbus_port == None):
                    cur.execute("UPDATE Settings SET Value = 'disabled' WHERE Key = 'Modbus_port'")
                    conn.commit()
                else:
                    cur.execute("UPDATE Settings SET Value = ? WHERE Key = 'Modbus_port'", (str(modbus_port),))
                    conn.commit()
                    
                if (dnp3_port == None):
                    cur.execute("UPDATE Settings SET Value = 'disabled' WHERE Key = 'Dnp3_port'")
                    conn.commit()
                else:
                    cur.execute("UPDATE Settings SET Value = ? WHERE Key = 'Dnp3_port'", (str(dnp3_port),))
                    conn.commit()
                    
                if (enip_port == None):
                    cur.execute("UPDATE Settings SET Value = 'disabled' WHERE Key = 'Enip_port'")
                    conn.commit()
                else:
                    cur.execute("UPDATE Settings SET Value = ? WHERE Key = 'Enip_port'", (str(enip_port),))
                    conn.commit()
                    
                if (pstorage_poll == None):
                    cur.execute("UPDATE Settings SET Value = 'disabled' WHERE Key = 'Pstorage_polling'")
                    conn.commit()
                else:
                    cur.execute("UPDATE Settings SET Value = ? WHERE Key = 'Pstorage_polling'", (str(pstorage_poll),))
                    conn.commit()
                    
                if (start_run == 'true'):
                    cur.execute("UPDATE Settings SET Value = 'true' WHERE Key = 'Start_run_mode'")
                    conn.commit()
                else:
                    cur.execute("UPDATE Settings SET Value = 'false' WHERE Key = 'Start_run_mode'")
                    conn.commit()
                    
                cur.execute("UPDATE Settings SET Value = ? WHERE Key = 'Slave_polling'", (str(slave_polling),))
                conn.commit()
                
                cur.execute("UPDATE Settings SET Value = ? WHERE Key = 'Slave_timeout'", (str(slave_timeout),))
                conn.commit()
                
                cur.close()
                conn.close()
                configure_runtime()
                generate_mbconfig()
                return flask.redirect(flask.url_for('dashboard'))
                
            except Error as e:
                print("error connecting to the database" + str(e))
                return 'Error connecting to the database. Make sure that your openplc.db file is not corrupt.<br><br>Error: ' + str(e)
        else:
            return 'Error connecting to the database. Make sure that your openplc.db file is not corrupt.'
    


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)
