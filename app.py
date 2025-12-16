from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# データベースの設定 (SQLiteを使用。ファイル名は blog.db)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- データベースのモデル（設計図） ---

# 記事の設計図
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    likes = db.Column(db.Integer, default=0)  # いいね数
    # 記事に紐づくコメントへの参照
    comments = db.relationship('Comment', backref='post', lazy=True)

# コメントの設計図
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(200), nullable=False)
    # どの記事へのコメントか紐付けるID
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

# データベースを初期化（初回のみ実行される）
with app.app_context():
    db.create_all()

# --- ルーティング（ページと機能の処理） ---

# 1. トップページ（記事一覧）
@app.route('/')
def index():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('index.html', posts=posts)

# 2. 記事投稿ページ
@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        # データベースに保存
        new_post = Post(title=title, content=content)
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('create.html')

# 3. 記事詳細ページ（ここでコメント表示も行う）
@app.route('/post/<int:id>')
def detail(id):
    post = Post.query.get_or_404(id)
    return render_template('detail.html', post=post)

# 4. いいね機能
@app.route('/like/<int:id>')
def like(id):
    post = Post.query.get_or_404(id)
    post.likes += 1  # いいねを1増やす
    db.session.commit()
    return redirect(url_for('detail', id=id))

# 5. コメント投稿機能
@app.route('/comment/<int:post_id>', methods=['POST'])
def add_comment(post_id):
    body = request.form['body']
    new_comment = Comment(body=body, post_id=post_id)
    db.session.add(new_comment)
    db.session.commit()
    return redirect(url_for('detail', id=post_id))

if __name__ == '__main__':
    app.run(debug=True)