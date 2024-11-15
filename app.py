from flask import Flask, g, render_template, redirect, url_for, request, session, flash, abort
from uuid import uuid4
from utils import *
from werkzeug.exceptions import NotFound
from functools import wraps

app = Flask(__name__)
app.secret_key = 'secret1'

@app.before_request
def initialize_session():
    if 'lists' not in session:
        session['lists'] = []

@app.context_processor
def list_utilities_processor():
    return {'is_list_completed': is_list_completed,
            }

def require_list(f):
    @wraps(f)

    def wrapper(*args, **kwargs):
        list_id = kwargs.get('list_id')
        lst = get_list_by_id(list_id, session['lists'])
        if lst:
            return f(lst=lst, *args, **kwargs)
        else:
            abort(404, description="List not found.")

    return wrapper

def require_todo(f):
    @wraps(f)

    @require_list
    def wrapper(lst, *args, **kwargs):
        todo_id = kwargs.get('todo_id')
        todo = get_todo_by_id(todo_id, lst['todos'])
        if not todo:
            abort(404, description="Todo not found.")
        return f(todo=todo, lst=lst, *args, **kwargs)

    return wrapper


@app.route("/")
def index():
    return redirect(url_for('lists'))

@app.route("/lists", methods=['GET', 'POST'])
def lists():
    if request.method == 'GET':
        lists = sort_items(session['lists'], is_list_completed)
        return render_template('lists.html',
                               lists=lists,
                               count_todos_remaining=count_todos_remaining)
    if request.method == 'POST':
        title = request.form.get('list_title').strip()
        error = error_for_list_title(title, session['lists'])
        if error:
            flash(error, 'error')
            return render_template('new_list.html', title=title)

        session['lists'].append({
            'id': str(uuid4()),
            'title': title,
            'todos': []
        })
        session.modified = True
        flash(f'{request.form.get('list_title').strip()} has been added!', 'success')
        return redirect(url_for('lists'))

@app.route('/lists/new')
def new_list():
    return render_template('new_list.html')


@app.route('/lists/<list_id>')
@require_list
def list_details(lst, list_id):
    todos = sort_items(lst['todos'], is_todo_completed)
    return render_template('list.html', lst=lst, todos=todos)


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html', error_message=error.description), 404


@app.route('/lists/<list_id>/complete_all', methods=['POST'])
@require_list
def complete_all_todos(lst, list_id):
    for todo in lst['todos']:
        todo['completed'] = True

    session.modified = True
    flash('All todos marked as completed!', 'success')

    return redirect(url_for('list_details', list_id=list_id))

@app.route('/lists/<list_id>/edit', methods=['GET', 'POST'])
@require_list
def edit_list(lst, list_id):

    if request.method == 'GET':
        return render_template('edit_list.html', lst=lst)

    if request.method == 'POST':
        list_title = request.form.get('list_title').strip()
        error = error_for_list_title(list_title, session['lists'])
        if error:
            flash(error, 'error')
            return render_template('edit_list.html', lst=lst)

        lst['title'] = list_title
        session.modified = True
        flash('List title changed successfully', 'success')

        return redirect(url_for('list_details', list_id=list_id))

@app.route('/lists/<list_id>/delete', methods=['POST'])
@require_list
def delete_list(lst, list_id):
    session['lists'].remove(lst)
    session.modified = True
    flash(f'List "{lst['title']}" deleted successfully.', 'success')

    return redirect(url_for('lists'))


@app.route('/lists/<list_id>/todos/<todo_id>/toggle', methods=['POST'])
@require_todo
def toggle_todo(lst, todo, list_id, todo_id):
    todo['completed'] = (request.form['completed'] == 'True')
    session.modified = True
    flash('Todo state changed successfully.', 'success')

    return redirect(url_for('list_details', list_id=list_id))


@app.route('/lists/<list_id>/todos/<todo_id>/delete', methods=['POST'])
@require_todo
def delete_todo(lst, todo, list_id, todo_id):
    lst['todos'].remove(todo)
    session.modified = True
    flash('Todo deleted.', 'success')

    return redirect(url_for('list_details', list_id=list_id))

# @app.post is same as @app.route(path, methods=['POST'])
@app.post('/lists/<list_id>/todos')
@require_list
def add_todo(lst, list_id):
    # 1. Todo title validation
    todo_title = request.form.get('todo').strip()
    error = error_for_todo_title(todo_title)
    if error:
        flash(error, 'error')
        return render_template('list.html', lst=lst)
    # 2. Todo creation
    todo = {
        'id': str(uuid4()),
        'title': todo_title,
        'completed' : False
    }
    lst['todos'].append(todo)
    session.modified = True
    flash('Todo created successfully!', 'success')

    return redirect(url_for('list_details', list_id=list_id))

if __name__ == "__main__":
    app.run(debug=True, port=5003)