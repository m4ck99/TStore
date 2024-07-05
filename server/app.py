from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import hashlib


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fileName = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    md5hash = db.Column(db.String(200))
    action = db.Column(db.String(200), nullable=False)
    dateCreated = db.Column(db.DateTime, default=datetime.utcnow)
    def __repr__(self):
        return '<Task %r>' % self.id

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download/')
def download():
    fileNames = Todo.query.order_by(Todo.dateCreated).all()
    return render_template('download.html', fileNames=fileNames)
@app.route('/Download/<int:id>', methods=['GET'])
def Download(id):
    if request.method == 'GET':
        setAction = Todo.query.get(id)
        setAction.action = 'download'
        db.session.commit()
        return redirect('/')

@app.route('/upload/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        fileLocation = request.form.get('locationtextbox')
        fileName = request.form.get('filenametextbox')
        hashm = hashlib.md5(fileLocation.encode()).hexdigest()
        try:
            db.session.add(Todo(fileName=fileName, md5hash=hashm, location=fileLocation, action='upload'))
            db.session.commit()
            return redirect('/')
        except Exception as e:
            print(f'Error: {e}')
            return 'Some error occurred'
    return render_template('upload.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
