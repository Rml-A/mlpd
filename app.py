from flask import Flask, render_template, request, redirect, url_for
from flask import flash
from models import db, Task
from sqlalchemy import or_

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'qwerty'
db.init_app(app)

# # Создание всех таблиц при первом запуске приложения
# with app.app_context():
#     db.create_all()


@app.route('/', methods=['GET'])
def index():
    search_query = request.args.get('search', '')
    status_filter = request.args.get('status', '')

    tasks = Task.query

    if search_query:
        tasks = tasks.filter(or_(Task.title.contains(search_query), Task.description.contains(search_query)))
    if status_filter:
        tasks = tasks.filter_by(status=status_filter)

    tasks = tasks.all()

    return render_template('index.html', tasks=tasks)


@app.route('/create', methods=['GET', 'POST'])
def create_task():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        new_task = Task(title=title, description=description)
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('index'))
    else:
        return render_template('create_task.html')


@app.route('/delete/<int:id>')
def delete_task(id):
    task_to_delete = Task.query.get_or_404(id)
    db.session.delete(task_to_delete)
    db.session.commit()
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

# Удалить маршрут если он нигде не используется!!!
# @app.route('/update_task_status/<int:task_id>', methods=['POST'])
# def update_task_status(task_id):
#     new_status = request.form['new_status']
#     task = Task.query.get(task_id)
#     if task:
#         task.status = new_status
#         db.session.commit()
#         flash('Статус задачи успешно обновлен', 'success')
#     else:
#         flash('Задача не найдена', 'error')
#     return redirect(url_for('index'))


@app.route('/tasks')
def tasks():
    status = request.args.get('status')
    if status:
        tasks = Task.query.filter_by(status=status).all()
    else:
        tasks = Task.query.all()
    return render_template('tasks.html', tasks=tasks)





if __name__ == '__main__':
    app.run(debug=True)
