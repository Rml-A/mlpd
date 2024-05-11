from flask import Flask, render_template, request, redirect, url_for
from flask import flash, abort
from models import db, Task, User
from sqlalchemy import or_, func
from forms import RegistrationForm, LoginForm, TaskForm
from flask_login import current_user, login_user, logout_user, LoginManager, login_required
from datetime import datetime


app = Flask(__name__)
login_manager = LoginManager(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'qwerty'
db.init_app(app)

# # Создание всех таблиц при первом запуске приложения
# with app.app_context():
#     db.create_all()


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@login_manager.user_loader
def load_user(user_id):
    # Здесь необходимо реализовать загрузку пользователя из базы данных или другого источника данных
    return User.query.get(int(user_id))


@app.route('/', methods=['GET'])
def index():
    if current_user.is_authenticated:
        # Маршрут для аутентифицированных пользователей
        search_query = request.args.get('search', '')
        status_filter = request.args.get('status', '')
        created_at_filter = request.args.get('created_at', '')  # Получаем значение фильтрации по дате создания
        tasks = Task.query.filter_by(user_id=current_user.id)

        if search_query:
            tasks = tasks.filter(or_(Task.title.contains(search_query), Task.description.contains(search_query)))
        if status_filter:
            tasks = tasks.filter_by(status=status_filter)
        if created_at_filter:  # Если есть фильтр по дате создания, фильтруем задачи по этому параметру
            created_at_date = datetime.strptime(created_at_filter, '%d.%m.%Y').date()  # Преобразуем строку в объект datetime.date
            tasks = tasks.filter(func.date(Task.created_at) == func.date(created_at_date))

        tasks = tasks.all()

        return render_template('index.html', tasks=tasks)
    else:
        # Маршрут для неаутентифицированных пользователей
        login_form = LoginForm()
        registration_form = RegistrationForm()
        return render_template('landing_page.html', login_form=login_form, registration_form=registration_form)


@app.route('/create', methods=['GET', 'POST'])
@login_required
def create_task():
    form = TaskForm()

    if form.validate_on_submit():
        title = form.title.data
        description = form.description.data
        created_at = datetime.utcnow()  # Получение текущего времени
        new_task = Task(title=title, description=description, user_id=current_user.id, created_at=created_at)  # Передача времени создания в объект задачи
        db.session.add(new_task)
        db.session.commit()
        flash('Task created successfully', 'success')
        return redirect(url_for('index'))
    return render_template('create_task.html', form=form, datetime=datetime)


@app.route('/delete/<int:id>')
def delete_task(id):
    task_to_delete = db.session.get(Task, id)
    if task_to_delete is None:
        abort(404)
    db.session.delete(task_to_delete)
    db.session.commit()
    flash('Task deleted successfully', 'success')
    return redirect(url_for('index'))


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_task(id):
    task = Task.query.get_or_404(id)
    if request.method == 'POST':
        task.title = request.form['title']
        task.description = request.form['description']
        task.status = request.form['status']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit_task.html', task=task)


@app.route('/view/<int:id>')
def view_task(id):
    task = Task.query.get_or_404(id)
    return render_template('view_task.html', task=task)



@app.route('/tasks')
@login_required
def tasks():
    status = request.args.get('status')
    created_at = request.args.get('created_at')  # Получаем дату создания из запроса

    tasks = Task.query.filter_by(user_id=current_user.id)

    if status:
        tasks = tasks.filter_by(status=status)

    if created_at:
        # Парсим дату создания из строки в формат datetime
        try:
            created_at_date = datetime.strptime(created_at, '%d.%m.%Y')
            # Фильтруем задачи по дате создания
            tasks = tasks.filter(func.date(Task.created_at) == func.date(created_at_date))
        except ValueError:
            flash('Неверный формат даты', 'danger')

    tasks = tasks.all()

    return render_template('tasks.html', tasks=tasks)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)





if __name__ == '__main__':
    app.run(debug=True)
