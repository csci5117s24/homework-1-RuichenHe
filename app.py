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
        print(request.form['userInput'])
        print(request.form['options'])
        print(request.form['selectionOption'])
        return render_template('thanks.html')
    else:
        return redirect(url_for('index'))
    
@app.route('/hi', methods=['GET'])
def hello_world():
  user_name = request.args.get("userName", "unknown")
  return render_template('main.html', user=user_name) 