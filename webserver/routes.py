
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

from nav import nav
from frontend import frontend

from flask import (
    Flask,
    Blueprint,
    render_template,
    redirect,
    flash,
    url_for,
    session,
    send_from_directory,
    stream_with_context,
    request,
    Response,
)

#from werkzeug.routing import BuildError
import os
import time
from werkzeug.utils import secure_filename
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
from models import Program

from forms import (
    LoginForm,
    RegisterForm,
    SettingForm,
    ProgramForm,
    SignupForm
    )


app = create_app()
# init_app(app) see manage.py
# app.app_context().push()

from openplc import openplc_runtime, configure_runtime
import openplc
import monitoring as monitor
#configure_openplc(app)
openplc_runtime = openplc.runtime()
compilation_status_str=0
compilation_object=0
configure_runtime(app)

monitor.parse_st(openplc_runtime.project_file)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Unauthorized'


@login_manager.request_loader
def request_loader(request):
    pass


@app.before_request
def session_handler():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=10)
    session.modified =True
   

@app.route("/home", methods=("GET", "POST"), strict_slashes=False)
@app.route("/", methods=("GET", "POST"), strict_slashes=False)
def index():
    if current_user.is_authenticated:
        return render_template("dashboard.html", title="OpenPLC_V3.1 Home", user=current_user)
    else:
        return redirect(url_for('login'))
    
    
@login_required
@app.route('/start_plc')
def start_plc():
    global openplc_runtime
#    if not current_user.is_authenticated:
#        return redirect(url_for('login'))
    
    monitor.stop_monitor()
    openplc_runtime.start_runtime()
    time.sleep(1)
    # configure_runtime()
    configure_runtime(app)

    monitor.cleanup()
    monitor.parse_st(openplc_runtime.project_file)
    return redirect(url_for('index'))
    # return render_template("dashboard.html", title="OpenPLC_V3.1 Home", user=current_user)

@login_required
@app.route('/stop_plc')
def stop_plc():
    global openplc_runtime
#    if (current_user.is_authenticated == False):
#        return flask.redirect(flask.url_for('login'))
#    else:
    openplc_runtime.stop_runtime()
    time.sleep(1)
    monitor.stop_monitor()
    #return redirect(url_for('dashboard'))
    return redirect(url_for('index'))

@login_required
@app.route('/runtime_logs')
def runtime_logs():
    global openplc_runtime
    return openplc_runtime.logs()
  
    
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)

@login_required
@app.route('/program/edit/<item_id>', methods=['GET', 'POST'])
def edit_program(request=request, item_id=None):
    # program = Program.get(...)
    # obj = Setting.query.filter_by(id=item_id).one()
    prog = Program.get(item_id)
    form = ProgramForm(request.POST, obj=prog)

    if request.POST and form.validate():
        form.populate_obj(prog)
        prog.save()
        return redirect(url_for('/programs'))

    # return render('edit.html', form=form, program=program)

    return render_template("programs.html", title="OpenPLC_V3.1 Programs", form=form, program=prog, data=result, user=current_user)

@login_required
@app.route('/upload-program-action', methods=['GET', 'POST'])
@app.route('/program/edit', methods=['GET', 'POST'])
@app.route('/upload-program', methods=['GET', 'POST'])
@app.route('/programs/<crud_method>/<item_id>', methods=['GET','POST'])
@app.route("/programs", methods=("GET", "POST"), strict_slashes=False)
def program( item_id = None, crud_method = None):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    
    form = ProgramForm()
    if form.validate_on_submit():
        flash('Start Date is : {} End Date is : {}'.format(form.date.data, form.date.data))
       
        return redirect('/programs')
    
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('program', name=filename))
        
        return redirect(request.url)
    # return '''
    # <!doctype html>
    # <title>Upload new File</title>
    # <h1>Upload new File</h1>
    # <form method=post enctype=multipart/form-data>
    #   <input type=file name=file>
    #   <input type=submit value=Upload>
    # </form>
    # '''
    

    
    try:
        result = db.session.query(Program).all()
        print(result)
        # Program.query.get(int(user_id))
    except:
        print("db session programs trouble")

    return render_template("programs.html", title="OpenPLC_V3.1 Programs", form=form, data=result, user=current_user)


@app.route('/runtime_logs', strict_slashes=False)
def streamed_response():
    @stream_with_context
    def generate():
        yield 'Hello RUNTIME_LOGS '
        # yield request.args['name']
        yield '!'
    return Response(generate())

@app.route("/login/", methods=("GET", "POST"), strict_slashes=False)
def login():
    form = LoginForm()

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
    form = RegisterForm()
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
    form = SettingForm()

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

    return redirect(url_for('settings'))  

@login_required
@app.route('/settings/', methods=['GET', 'POST'])
@app.route('/settings/<crud_method>/<item_id>', methods=['GET'])
def settings( item_id = None, crud_method = None):
    item_id = item_id or ''
    crud_method = crud_method or ''
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    
    # monitor.stop_monitor()
    # if (openplc_runtime.status() == "Compiling"):
        # return draw_compiling_page()
        # return flask.redirect(flask.url_for('draw_compiling_page'))


    try:
        # a list
        result = db.session.query(Setting).all()
    except:
        print("db session settings trouble")

    form = SettingForm()

    if (item_id != ''):
        if (crud_method == 'edit'):
            # obj = Setting.query.filter_by(id=item_id).one()
            obj = Setting.query.get(item_id)
            #print(obj)
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


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == "__main__":
    #Load information about current program on the openplc_runtime object
    file = open("active_program", "r")
    st_file = file.read()
    st_file = st_file.replace('\r','').replace('\n','')
    
    reload(sys)
    sys.setdefaultencoding('UTF8')
    
    
    app.run(debug=True)
