from flask import Flask, g, render_template, redirect, url_for, request, session, flash, abort
from uuid import uuid4
from utils import *
from werkzeug.exceptions import NotFound

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

@app.route("/")
def index():
    return redirect(url_for('lists'))

@app.route("/lists", methods=['GET', 'POST'])
def lists():
    if request.method == 'GET':
        return render_template('lists.html',
                               lists=session['lists'],
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
def list_details(list_id):
    lst = get_list_by_id(list_id, session['lists'])
    if lst:
        return render_template('list.html', lst=lst)
    else:
        abort(404, description="List not found.")
        # raise NotFound(description="List not found.")


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html', error_message=error.description), 404


@app.route('/lists/<list_id>/complete_all', methods=['POST'])
def complete_all_todos(list_id):
    # 1. Validate list
    todo_list = get_list_by_id(list_id, session['lists'])
    if not todo_list:
        abort(404, description='List not found.')

    for todo in todo_list['todos']:
        todo['completed'] = True

    session.modified = True
    flash('All todos marked as completed!', 'success')

    return redirect(url_for('list_details', list_id=list_id))

@app.route('/lists/<list_id>/edit', methods=['GET', 'POST'])
def edit_list(list_id):
    todo_list = get_list_by_id(list_id, session['lists'])
    if not todo_list:
        abort(404, description='List not found.')

    if request.method == 'GET':
        return render_template('edit_list.html', lst=todo_list)

    if request.method == 'POST':
        list_title = request.form.get('list_title').strip()
        error = error_for_list_title(list_title, session['lists'])
        if error:
            flash(error, 'error')
            return render_template('edit_list.html', lst=todo_list)

        todo_list['title'] = list_title
        session.modified = True
        flash('List title changed successfully', 'success')

        return redirect(url_for('list_details', list_id=list_id))

@app.route('/lists/<list_id>/delete', methods=['POST'])
def delete_list(list_id):
    todo_list = get_list_by_id(list_id, session['lists'])
    if not todo_list:
        abort(404, description="List not found.")

    session['lists'].remove(todo_list)
    session.modified = True
    flash(f'List "{todo_list['title']}" deleted successfully.', 'success')

    return redirect(url_for('lists'))

@app.route('/lists/<list_id>/todos/<todo_id>/toggle', methods=['POST'])
def toggle_todo(list_id, todo_id):
     # 1. List validation
    todo_list = get_list_by_id(list_id, session['lists'])
    if not todo_list:
        abort(404, description="List not found.")

    # 2. Todo validation
    todo = get_todo_by_id(todo_id, todo_list['todos'])
    if not todo:
        abort(404, description="Todo not found.")


    # 3. Success - changing todo completion state
    todo['completed'] = (request.form['completed'] == 'True')
    session.modified = True
    flash('Todo state changed successfully.', 'success')

    return redirect(url_for('list_details', list_id=list_id))


@app.route('/lists/<list_id>/todos/<todo_id>/delete', methods=['POST'])
def delete_todo(list_id, todo_id):
    # 1. List validation
    todo_list = get_list_by_id(list_id, session['lists'])
    if not todo_list:
        abort(404, description="List not found.")

    # 2. Todo validation
    todo = get_todo_by_id(todo_id, todo_list['todos'])
    if not todo:
        abort(404, description="Todo not found.")


    # 3. Success - deleting todo
    todo_list['todos'].remove(todo)
    session.modified = True
    flash('Todo deleted.', 'success')

    return redirect(url_for('list_details', list_id=list_id))

# @app.post is same as @app.route(path, methods=['POST'])
@app.post('/lists/<list_id>/todos')
def add_todo(list_id):

    # 1. List validation
    todo_list = get_list_by_id(list_id, session['lists'])
    if not todo_list:
        abort(404, description="List not found.")
    # 2. Todo validation
    todo_title = request.form.get('todo').strip()
    error = error_for_todo_title(todo_title)
    if error:
        flash(error, 'error')
        return render_template('list.html', lst=todo_list)
    # 3. Todo creation
    todo = {
        'id': str(uuid4()),
        'title': todo_title,
        'completed' : False
    }
    todo_list['todos'].append(todo)
    session.modified = True
    flash('Todo created successfully!', 'success')

    return redirect(url_for('list_details', list_id=list_id))

if __name__ == "__main__":
    app.run(debug=True, port=5003)