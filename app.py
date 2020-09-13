import sqlite3 as sl
from flask import Flask, render_template, request, url_for, session, redirect, jsonify
import datetime
import hashlib

current_user_id=1
current_post_slug=""  # this is a primitive solution. do better
current_post_id=1
current_comment_id=1

db = sl.connect("firstDatabase.db")
cs = db.cursor()
cs.execute("create table if not exists  Users (id INT PRIMARY KEY UNIQUE, user_name, password, email, posts, comments TEXT, tw, fb)")
cs.execute("create table if not exists Posts (id INT PRIMARY KEY UNIQUE, slug UNIQUE, writer_name, category, title, content, comments TEXT, date TEXT, ip )")
cs.execute("create table if not exists Comments (comment_id INT PRIMARY KEY UNIQUE, commenter_name, post_slug, content, date )")
cs.execute("create table if not exists Categories (cat_name TEXT PRIMARY KEY UNIQUE, cat_slug, posts )")
db.commit()
db.close()

app=Flask(__name__)
app.secret_key = "raxacoricofallapatorius"
@app.route("/")
def index():
    return redirect(url_for("home"))

# try to make this clean if you have time
@app.route("/home")
def home():
    db = sl.connect("firstDatabase.db")
    cs = db.cursor()
    cs.execute('SELECT * from Posts ORDER BY id DESC;')
    rows = cs.fetchall()
    all_posts=""
    template = """
       <div class="card mb-4">
             <div class="card-body">
               <h2 class="card-title">{}</h2>
               <p class="card-text">{}</p>
               <a href="/post/{}" class="btn btn-primary">Devamı &rarr;</a>
             </div>
             <div class="card-footer text-muted">
              Yayın tarihi: {} Yazar:
               <a href="/profile/{}">{}</a>
             </div>
           </div>
       """
    for row in rows[0:3]:
        title = row[4]
        content = row[-4][0:290]+"..."
        slug = row[1]
        date = row[-2]
        writer = row[2]
        all_posts+=template.format(title, content, slug, date, writer, writer)
    db.commit()
    db.close()
    if 'username' in session:
        user_name = session['username']
        return render_template("session_home.html", user_name=user_name, all_posts=all_posts)
    return render_template("home.html", all_posts=all_posts)

@app.route("/post/<slug>")
def post(slug):
    global current_post_slug
    current_post_slug=slug # for a new comment
    db = sl.connect("firstDatabase.db")
    cs = db.cursor()
    cs.execute('SELECT * from Posts')
    rows = cs.fetchall()
    comments=post_title=yazar=post_date=post_content=all_comments = ""
    for row in rows:
        if row[1]==slug:
            comments=row[-3]
            post_title = row[4]
            yazar = row[2]
            post_date = row[-2]
            post_content = row[-4]
    template=""" <div class="media mb-4">
          <img class="d-flex mr-3 rounded-circle" src="http://placehold.it/50x50" alt="">
          <div class="media-body">
            <h5 class="mt-0">{}</h5>
            {}
          </div>
        </div> """
    comment_ids=comments.split("ayrac")
    db.commit()
    db.close()
    db = sl.connect("firstDatabase.db")
    cs = db.cursor()
    cs.execute('SELECT * from Comments')
    rows = cs.fetchall()
    for id in comment_ids:
        for row in rows:
            if str(row[0])==id:
                commenter=row[1]
                comment_of_post=row[-2]  # add date?
                my_template=template
                all_comments+=my_template.format(commenter,comment_of_post)
    db.commit()
    db.close()
    if 'username' in session:
        user_name = session['username']
        return render_template("session_post.html",user_name=user_name, post_title=post_title, yazar=yazar, post_date=post_date, post_content=post_content, comments=all_comments)
    return render_template("post.html", post_title=post_title, yazar=yazar, post_date=post_date, post_content=post_content, comments=all_comments)

@app.route("/category/<cat>")
def category(cat):
    db = sl.connect("firstDatabase.db")
    cs = db.cursor()
    cs.execute('SELECT * from Posts ORDER BY id DESC;')
    rows = cs.fetchall()
    all_posts = ""
    template = """
           <div class="card mb-4">
                 <div class="card-body">
                   <h2 class="card-title">{}</h2>
                   <p class="card-text">{}</p>
                   <a href="/post/{}" class="btn btn-primary">Devamı &rarr;</a>
                 </div>
                 <div class="card-footer text-muted">
                  Yayın tarihi: {} Yazar:
                   <a href="/profile/{}">{}</a>
                 </div>
               </div>
           """
    cat_posts=[]
    for row in rows:
        if row[3]==cat:
            cat_posts.append(row)
    for row in cat_posts[0:3]:
        title = row[4]
        content = row[-4][0:290] + "..."
        slug = row[1]
        date = row[-2]
        writer = row[2]
        all_posts += template.format(title, content, slug, date, writer, writer)
    db.commit()
    db.close()
    if 'username' in session:
        user_name = session['username']
        return render_template("session_category.html", user_name=user_name, category=cat, all_posts=all_posts)
    return render_template("category.html", category=cat, all_posts=all_posts)


@app.route("/login")
def login():
    return render_template("login.html")

@app.route('/datas',methods = ['POST'])
def datas():
   if request.method == 'POST':
      user_name = request.form['user_name']
      password= request.form['user_password']
      result = hashlib.sha512(password.encode())
      hash_password = result.hexdigest()
      db = sl.connect("firstDatabase.db")
      cs = db.cursor()
      cs.execute('SELECT * from Users')
      rows = cs.fetchall()
      db.commit()
      db.close()
      for row in rows:
          if row[1]==user_name and row[2]==hash_password:
              session['username'] = request.form['user_name']
              return redirect(url_for("home", user_name=user_name))
      return render_template("login.html", hata="Kullanıcı adı veya şifreyi yanlış girdiniz!" )

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/new_user", methods = ['POST'])
def new_user():
    if request.method == 'POST':
        global current_user_id

        user_name=request.form['new_name']
        password=request.form['new_password']
        result = hashlib.sha512(password.encode())
        hash_password=result.hexdigest()
        email=request.form['new_email']
        db = sl.connect("firstDatabase.db")
        cs = db.cursor()
        cs.execute("insert or ignore into Users values (?, ?, ?, ?, ?, ?, ?, ?)", (current_user_id,user_name,hash_password,email, "", "","","",))
        db.commit()
        db.close()
        current_user_id+=1
        return render_template("login.html",new="Kayıt Başarılı!")

@app.route("/create_post")
def create_post():
    return render_template("create_post.html", user_name=session["username"])

@app.route("/new_post", methods = ['POST'])
def new_post():
    if request.method == 'POST':
        global current_post_id
        slug = request.form['slug']
        writer = session['username']
        category = request.form['category']
        title=request.form['title']
        content=request.form['content']
        date=str(datetime.datetime.now())
        db = sl.connect("firstDatabase.db")
        cs = db.cursor()
        cs.execute("insert or ignore into Posts values (?, ?, ?, ?, ?, ?, ?, ?, ?)", (current_post_id, slug, writer, category, title, content, "", date, str(request.remote_addr)))
        cs.execute('SELECT * from Users')
        rows = cs.fetchall()
        posts=""
        for row in rows:
            if row[1]==writer:
                posts=row[-4]
        cs.execute("update Users set posts= ? where  user_name= ? ", (posts+"ayrac"+slug, writer))
        db.commit()

        cs.execute('SELECT * from Categories')
        rows = cs.fetchall()
        for row in rows:
            if row[0]==category:
                posts=row[-1]
        cs.execute("update Categories set posts= ? where  cat_name= ? ", (posts + "ayrac" + slug, category))
        db.commit()
        db.close()
        current_post_id+=1
        return redirect(url_for("post",slug=slug))

@app.route("/comment", methods = ['POST'])
def comment():
    if request.method == 'POST':
        global current_comment_id
        global current_post_slug
        comment_id=current_comment_id
        current_comment_id+=1
        commenter = session['username']
        post_slug = current_post_slug
        content = request.form['content']
        date = str(datetime.datetime.now())
        db = sl.connect("firstDatabase.db")
        cs = db.cursor()
        cs.execute("insert or ignore into Comments values (?, ?, ?, ?, ?)", (comment_id, commenter, post_slug, content, date,))
        cs.execute('SELECT * from Posts')
        rows = cs.fetchall()
        comments = ""
        writer = ""
        for row in rows:
            if row[1] == post_slug:
                comments = row[-3]
                writer=row[3]
        cs.execute("update Posts set comments= ? where  slug= ? ", (comments+"ayrac"+str(comment_id), post_slug))

        cs.execute('SELECT * from Users')
        rows = cs.fetchall()
        for row in rows:
            if row[2] == writer:
                comments = row[-3]
        cs.execute("update Users set comments= ? where  user_name= ? ", (comments+"ayrac"+str(comment_id), commenter))
        db.commit()
        db.close()

        return redirect(url_for("post", slug=current_post_slug))

@app.route("/profile/<user_name>")
def profile(user_name):
    db = sl.connect("firstDatabase.db")
    cs = db.cursor()
    cs.execute('SELECT * from Posts ORDER BY id DESC;')
    rows = cs.fetchall()
    all_posts = ""
    template = """
               <div class="card mb-4">
                     <div class="card-body">
                       <h2 class="card-title">{}</h2>
                       <p class="card-text">{}</p>
                       <a href="/post/{}" class="btn btn-primary">Devamı &rarr;</a>
                     </div>
                     <div class="card-footer text-muted">
                      Yayın tarihi: {} Yazar:
                       <a href="/profile/{}">{}</a>
                     </div>
                   </div>
               """
    user_posts = []
    for row in rows:
        if row[2] == user_name:
            user_posts.append(row)
    post_number=len(user_posts)
    for row in user_posts[0:3]:
        title = row[4]
        content = row[-4][0:290] + "..."
        slug = row[1]
        date = row[-2]
        writer = row[2]
        all_posts += template.format(title, content, slug, date, writer, writer)
    db.commit()
    db.close()

    db = sl.connect("firstDatabase.db")
    cs = db.cursor()
    cs.execute('SELECT * from Users ORDER BY id DESC;')
    rows = cs.fetchall()
    for row in rows:
        if row[1] == user_name:
            tw=row[-2]
            fb=row[-1]
            print(row[-3]) # doesn't work on
            comment_number=len(row[-3].split("ayrac"))

    if "username" in session and session["username"]!=user_name:
        return render_template("session_profile.html", person=user_name, all_posts=all_posts, post_number=post_number, fb=fb, tw=tw, comment_number=comment_number, user_name=session["username"] )
    elif "username" in session and session["username"]==user_name:
        return render_template("my_profile.html", person=user_name, all_posts=all_posts, post_number=post_number, fb=fb, tw=tw, comment_number=comment_number, user_name=session["username"] )
    return render_template("profile.html", person=user_name, all_posts=all_posts, post_number=post_number, fb=fb, tw=tw, comment_number=comment_number )

@app.route("/social", methods = ['POST'])
def social():
    if request.method == 'POST':
        fb_link=request.form['fb']
        tw_link=request.form['tw']
        db = sl.connect("firstDatabase.db")
        cs = db.cursor()
        cs.execute("update Users set fb= ? where  user_name= ? ", (fb_link, session["username"]))
        db.commit()
        cs.execute("update Users set tw= ? where  user_name= ? ", (tw_link, session["username"]))
        db.commit()
        db.close()
        return redirect(url_for("profile", user_name=session["username"]))

@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route("/api/post")
def api_post():
    db = sl.connect("firstDatabase.db")
    cs = db.cursor()
    cs.execute('SELECT * from Posts')
    rows = cs.fetchall()
    posts=[]
    for row in rows:
        posts.append(row[0:8])
    db.commit()
    db.close()
    return jsonify({'posts':posts[0:10]})

@app.route("/api/post/<id>")
def api_post_id(id):
    db = sl.connect("firstDatabase.db")
    cs = db.cursor()
    cs.execute('SELECT * from Posts')
    rows = cs.fetchall()
    post=comments=None
    for row in rows:
        if str(row[0])==str(id):
            post=row
            comments=row[-3].split("ayrac")
    db.commit()

    all_comments=[]
    db = sl.connect("firstDatabase.db")
    cs = db.cursor()
    cs.execute('SELECT * from Comments')
    rows = cs.fetchall()
    for row in rows:
        if str(row[0]) in comments:
            all_comments.append(row)
    db.commit()
    db.close()

    return jsonify({'comments':all_comments, 'post-'+id:post[0:6]+[post[7]] })

@app.route("/api/category")
def api_categories():
    db = sl.connect("firstDatabase.db")
    cs = db.cursor()
    cs.execute('SELECT * from Categories')
    rows = cs.fetchall()
    categories=[]
    for row in rows:
        categories.append(row[0:2])
    db.commit()
    db.close()
    return jsonify({'categories':categories})

@app.route("/api/category/<cat>")
def api_cat(cat):
    db = sl.connect("firstDatabase.db")
    cs = db.cursor()
    cs.execute('SELECT * from Posts')
    rows = cs.fetchall()
    posts=[]
    for row in rows:
        if row[3]==cat:
            posts.append(row[:-1])
    db.commit()
    db.close()
    return jsonify({'posts-'+cat:posts})

@app.route("/api/user/<user_name>")
def api_user(user_name):
    db = sl.connect("firstDatabase.db")
    cs = db.cursor()
    cs.execute('SELECT * from Users')
    rows = cs.fetchall()
    user=None
    for row in rows:
        if row[1]==user_name:
            user=row
    db.commit()
    db.close()
    return jsonify({user_name:[user[1], user[4].split("ayrac")[1:], user[-1], user[-2]]})

if __name__ == "__main__":
    app.run(debug = True)
