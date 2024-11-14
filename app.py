from flask import Flask, render_template, redirect, url_for, request, session, flash
from uuid import uuid4
from utils import error_for_list_title

app = Flask(__name__)
app.secret_key = 'secret1'


@app.before_request
def initialize_session():
    if 'lists' not in session:
        session['lists'] = []

@app.route("/")
def index():
    return redirect(url_for('lists'))

@app.route("/lists", methods=['GET', 'POST'])
def lists():
    if request.method == 'GET':
        return render_template('lists.html', lists=session['lists'], example=None)
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
    lst = [lst for lst in session['lists'] if lst['id'] == list_id][0]
    return str(lst)


if __name__ == "__main__":
    app.run(debug=True, port=5003)