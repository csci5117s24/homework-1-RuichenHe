from flask import Flask
from flask import render_template, request, redirect, url_for
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/survey')
def accept():
    return render_template('survey.html')

@app.route('/decline')
def decline():
    return render_template('decline.html')

@app.route('/thanks', methods=['POST', 'GET'])
def thanks():
    if request.method == 'POST':
        return render_template('thanks.html')
    else:
        return redirect(url_for('index'))