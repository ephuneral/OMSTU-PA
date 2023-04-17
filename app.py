import os
import secrets
from datetime import datetime

from PIL import Image
from flask import Flask, render_template, request, session, flash, redirect, url_for
from flask_login import login_required, LoginManager, UserMixin, current_user, login_user, logout_user
from flask_migrate import Migrate
from flask_security import RoleMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:dsdctgbljhs@localhost/application_db' #для локалки

# для серва
# app.config[
#     'SQLALCHEMY_DATABASE_URI'] = 'postgresql://ktqteenlpccxxk:fa5e165a12c9fa8a47460812e8ec39de1c66fae9c72ad4dea75b257da575fc8f@ec2-52-30-67-143.eu-west-1.compute.amazonaws.com:5432/da2mr4830grb58'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'abombusus'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

manager = LoginManager(app)

roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('users.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('roles.id'))
)


class Package(db.Model):
    __tablename__ = 'package'
    package_id = db.Column(db.Integer, unique=True, primary_key=True)
    task_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'))
    sent_on = db.Column(db.DateTime(), default=datetime.utcnow)
    file_path = db.Column(db.String(128), nullable=False)


class Role(db.Model, RoleMixin):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name


class UserModel(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, unique=True, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    surname = db.Column(db.String(20), nullable=False)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    image_file = db.Column(db.String(128), default='/static/profile_pics/default_pic.svg')

    # email = db.Column(db.String, unique=True)
    # created_on = db.Column(db.DateTime(), default=datetime.utcnow)
    # updated_on = db.Column(db.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)
    # # Нужен для security!
    # active = db.Column(db.Boolean())
    # # Для получения доступа к связанным объектам
    # roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))

    # Flask - Login
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    # Flask-Security
    def has_role(self, *args):
        return set(args).issubset({role.name for role in self.roles})

    def get_id(self):
        return self.id

    # Required for administrative interface
    def __unicode__(self):
        return self.username

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __init__(self, username, password, image_file, name, surname):
        self.username = username
        self.password = password
        self.image_file = image_file
        self.name = name
        self.surname = surname
        # self.email = email
        # self.created_on = created_on
        # self.updated_on = updated_on
        # self.active = active
        # self.roles = roles

    def __repr__(self):
        return f""


@manager.user_loader
def load_user(user_id):
    return db.session.query(UserModel).get(user_id)


manager.init_app(app)
manager.login_view = 'register'


@app.route('/register', methods=["POST", "GET"])
def register():
    if request.method == "POST":
        session.pop('_flashes', None)
        username = request.form['login']
        user = UserModel.query.filter_by(username=username).first()
        if len(request.form['name']) and len(request.form['surname']) is not None:
            if len(request.form['login']) >= 6:
                if not user:
                    if len(request.form['password']) >= 8:
                        if request.form['password'] == request.form['password2']:
                            hash_pass = generate_password_hash(request.form['password'])
                            image = url_for('static', filename=f'profile_pics/default_pic.svg')
                            new_user = UserModel(name=user, surname=username,
                                                 username=request.form['login'], password=hash_pass, image_file=image)
                            db.session.add(new_user)
                            login_user(new_user)
                            res = db.session.commit()
                            # res = db.addUser(request.form['name'], request.form['email'], hash_pass)
                            flash("Вы успешно зарегистрированы", "success")
                            return redirect('/')
                        else:
                            flash("Пароли должны совпадать", "error")
                    else:
                        flash("Длина пароля должна быть не менее 8 символов", "error")
                else:
                    flash("Пользователь с таким логином уже существует", "error")
            else:
                flash("Длина логина должна быть не менее 6 символов", "error")
        else:
            flash("Поля имя и фамилия не должны быть пустыми")

    # if len(request.form['login']) > 4 and len(request.form['password']) > 4 and request.form['password'] == \
    #         request.form['password2']:
    #     hash_pass = generate_password_hash(request.form['password'])
    #     image = url_for('static', filename=f'profile_pics/default_pic.svg')
    #     new_user = UserModel(name=request.form['name'], surname=request.form['surname'],
    #                          username=request.form['login'], password=hash_pass, image_file=image)
    #     db.session.add(new_user)
    #     res = db.session.commit()
    #     # res = db.addUser(request.form['name'], request.form['email'], hash_pass)
    #     flash("Вы успешно зарегистрированы", "success")
    #     return redirect('/')
    # else:
    #     flash("Неверно заполнены поля", "error")

    return render_template("register.html")


@app.route('/')
def index():
    return render_template("index.html")


def save_picture(form_picture):
    random_hex = secrets.token_hex(16)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    full_path = os.path.join(app.root_path, 'static', 'profile_pics/', current_user.username, 'account_image')
    if not os.path.exists(full_path):
        os.mkdir(full_path)
    picture_path = os.path.join(full_path, picture_fn)
    output_size = (40, 40)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


# @app.route('/update_user_account', methods=["GET", "POST"])
# @login_required
# def update_account():
#     if request.method == "POST":
#         if form.picture.data:
#             current_user.image_file = save_picture(form.picture.data)
#         else:
#             form.picture.data = current_user.image_file
#
#     return render_template("user_page.html")


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'py'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# @app.route('/user_page', methods=['GET', 'POST'])
# @login_required
# def upload_file():
#     if request.method == 'POST':
#         # check if the post request has the file part
#         if 'file' not in request.files:
#             flash('No file part')
#             return redirect(request.url)
#         file = request.files['file']
#         # If the user does not select a file, the browser submits an
#         # empty file without a filename.
#         if file.filename == '':
#             flash('No selected file')
#             return redirect(request.url)
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             save_picture()
#             file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#             return redirect(url_for('/', name=filename))
#     return render_template("user_page.html")

@app.route('/user_page', methods=["GET", "POST"])
@login_required
def account():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect('user_page')
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect('user_page')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            full_path = os.path.join(app.root_path, 'static', 'profile_pics/', current_user.username,
                                     'account_image')

            if not os.path.exists(full_path):
                os.makedirs(full_path)

            UPLOAD_FOLDER = full_path
            random_hex = secrets.token_hex(16)
            _, f_ext = os.path.splitext(file.filename)
            picture_fn = random_hex + f_ext
            file.save(os.path.join(UPLOAD_FOLDER, picture_fn))

            image = url_for('static',
                            filename=f'profile_pics/' + current_user.username + '/account_image/' + picture_fn)
            username = current_user.username
            user = UserModel.query.filter_by(username=username).first()
            user.image_file = image
            db.session.commit()

            # i = Image.open(f'{os.path.join(UPLOAD_FOLDER, picture_fn)}')
            # i.thumbnail(size=(40, 40))
            # i.save(f'{os.path.join(UPLOAD_FOLDER, picture_fn)}')

            return redirect('user_page')
    return render_template("user_page.html")


#
# @app.route('/user_page', methods=["GET", "POST"])
# @login_required
# def user_page():
#     # image_file = url_for('static', filename=f'profile_pics/default_pic.svg')
#
#     # image_file = url_for('static', filename=f'profile_pics/' + current_user.username + '/account_img/' +
#     # current_user.image_file)
#     #
#     # if request.method == "POST":
#     #     if form.picture.data:
#     #         current_user.image_file = save_picture(form.picture.data)
#     #     else:
#     #         form.picture.data = current_user.image_file
#     #
#
#     # if form.picture.data:
#     #     current_user.image_file = save_picture(form.picture.data)
#     # else:
#     #     form.picture.data = current_user.image_file
#
#     # image_file = url_for('static',filename=f'profile_pics/' + current_user.username + '/account_img/' +
#     # current_user.image_file)
#
#     form = UpdateAccountForm()
#     if form.validate_on_submit():
#         if form.picture.data:
#             picture_file = save_picture(form.picture.data)
#             current_user.image_file = picture_file
#         db.session.commit()
#         flash('Your account has been updated!', 'success')
#         return redirect(url_for('account'))
#     elif request.method == 'GET':
#         image_file = url_for('static',
#                              filename=f'profile_pics/' + current_user.username + '/account_img/' + current_user.image_file)
#     return render_template('user_page.html', title='Account', image_file=image_file, form=form)


@app.route('/auth', methods=['POST', 'GET'])
def auth():
    if current_user.is_authenticated:
        return redirect('/user_page')
    if request.method == 'POST':
        username = request.form['login']
        user = UserModel.query.filter_by(username=username).first()
        if user is not None and user.check_password(request.form['password']):
            login_user(user)
            return redirect('/user_page')
        else:
            flash('Логин или пароль заполнены некорректно')
    else:
        flash('Пожалуйста заполните поля логина и пароля')
    return render_template('auth.html')

    # login = request.form.get('login')
    # password = request.form.get('password')
    # if login and password:
    #     user = UserModel.query.filter_by(username=login).first()
    #     if user and check_password_hash(user.password, password):
    #         login_user(user)
    #         redirect(url_for('user_page'))
    #     else:
    #         flash('Логин или пароль заполнены некорректно')
    # else:
    #     flash('Пожалуйста заполните поля логина и пароля')
    #     return render_template('auth.html')


@app.route('/logout', methods=['POST', 'GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/about')
def about_us():
    return render_template("about.html")


# @app.route('/course/lesson_<lesson_id>/lesson_<lesson_number>')
# def lessons(lesson_id, lesson_number):
#     return render_template(f"course/lesson_{lesson_id}/lesson_{lesson_number}.html")


@app.route('/course/lesson_<int:lesson_id>/ex_<int:ex_id>')
@login_required
def ex_load(lesson_id, ex_id):
    return render_template("course/lesson_{}/ex_{}.html".format(lesson_id, ex_id))


if __name__ == '__main__':
    db.create_all()
    app.run()
