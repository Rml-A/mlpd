from flask import Flask, render_template, request, redirect, url_for
from models import db, Task

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# # Создание всех таблиц при первом запуске приложения
# with app.app_context():
#     db.create_all()


@app.route('/', methods=['GET'])
def index():
    status_filter = request.args.get('status', '')
    if status_filter:
        tasks = Task.query.filter_by(status=status_filter).all()
    else:
        tasks = Task.query.all()
    return render_template('index.html', tasks=tasks)


@app.route('/create', methods=['POST'])
def create_task():
    title = request.form['title']
    description = request.form['description']
    new_task = Task(title=title, description=description)
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for('index'))


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
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit_task.html', task=task)


@app.route('/view/<int:id>')
def view_task(id):
    task = Task.query.get_or_404(id)
    return render_template('view_task.html', task=task)




if __name__ == '__main__':
    app.run(debug=True)
