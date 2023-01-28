from flask import Flask
from flask import render_template,url_for,request,redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from flask import send_from_directory


UPLOAD_FOLDER = 'static/images/'
ALLOWED_EXTENSIONS = set([ 'png', 'jpg', 'jpeg', 'gif'])
app=Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///flaskblog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db=SQLAlchemy(app)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

class Article(db.Model):
    id=db.Column(db.Integer, primary_key=True) #номер статьи
    title=db.Column(db.String(100), nullable=False) #название статьи
    intro=db.Column(db.String(100), nullable=False) #
    text=db.Column(db.Text, nullable=False) #текст статьи
    date=db.Column(db.DateTime, default=datetime.utcnow) #дата и время публикации
    file=db.Column(db.Text, nullable=False)


    def __repr__(self):
        return '<Article %r>' %self.id

@app.route('/')
def index():
    articles = Article.query.order_by(Article.date.desc()).all()
    return render_template('index.html',articles=articles)


@app.route('/about')
def about():
    return render_template('about.html')



@app.route('/posts')
def posts():
    articles=Article.query.order_by(Article.date.desc()).all()
    return render_template('posts.html',articles=articles)

@app.route('/posts/<int:id>')
def posts_detail(id):
    article=Article.query.get(id)
    return render_template('posts_detail.html',article=article)


@app.route('/posts/<int:id>/delete')
def posts_delete(id):
    article=Article.query.get_or_404(id)

    try:
        db.session.delete(article)
        db.session.commit()

        return redirect('/posts')

    except:
        return 'При удалении статьи произошла ошибка'


@app.route('/posts/<int:id>/update',methods=['POST','GET'])
def post_update(id):
    article=Article.query.get(id)
    if request.method=='POST':
        article.file = request.files['file']
        article.title=request.form['title']
        article.intro = request.form['intro']
        article.text = request.form['text']

        if article.file and allowed_file(article.file.filename):
            filename = secure_filename(article.file.filename)
        article.file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        dirname = os.path.dirname(app.config['UPLOAD_FOLDER'])
        article.file=os.path.join(dirname+'/'+filename)

        try:
            db.session.commit()
            return redirect('/posts')

        except:
            return 'При изменении статьи произошла ошибка'
    else:
        article=Article.query.get(id)
        return render_template('post_update.html',article=article)




@app.route('/create-article',methods=['POST','GET'])
def create_article():
    if request.method=='POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        dirname = os.path.dirname(app.config['UPLOAD_FOLDER'])
        file=os.path.join(dirname+'/'+filename)

        title=request.form['title']
        intro = request.form['intro']
        text = request.form['text']

        article=Article(title=title,intro=intro,text=text,file=file)

        try:
            db.session.add(article)
            db.session.commit()
            return redirect('/posts')

        except:
            return 'При добавлении статьи произошла ошибка'
    else:
        return render_template('create-article.html')



@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


if __name__=='__main__':
    app.run(debug=True)