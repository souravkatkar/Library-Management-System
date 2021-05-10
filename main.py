from flask import Flask,render_template,request,session,redirect,url_for,json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from datetime import date
from datetime import timedelta
from datetime import datetime

app = Flask(__name__)

app.secret_key = 'HalaMadrid'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.sqlite'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String)
    lname = db.Column(db.String)
    email = db.Column(db.String)
    username = db.Column(db.String)
    password = db.Column(db.String)
    bookstatus = db.relationship('Bookstatus',backref = "user")
 
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    fname = db.Column(db.String)
    lname = db.Column(db.String)
    email = db.Column(db.String)
    username = db.Column(db.String)
    password = db.Column(db.String)

class Books(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    bookname = db.Column(db.String)
    author = db.Column(db.String)
    year = db.Column(db.String)
    bookstatus = db.relationship('Bookstatus',backref = "books")

class Bookstatus(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    book_id = db.Column(db.Integer,db.ForeignKey('books.id'),nullable=False)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    issuedate = db.Column(db.Date)
    returndate = db.Column(db.Date)
    fine = db.Column(db.Integer)
     

db.create_all()
db.session.commit()

admin = Admin.query.all()
print(admin)
if not admin:
    db.session.add(Admin(fname="Johnny",lname="Depp",email="johnny@gmail.com",password="admin",username="admin"))
    db.session.commit()
    #print("added")



@app.route('/')
def index():
    return render_template('index.html')


@app.route('/loginuser',methods=['POST','GET'])
def loginuser():
    if request.method == 'GET':
        data = {
            'error' : ""
        }
        return render_template('loginuser.html',data=data)

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user:

            if password == user.password:
                session['user_id'] = user.id
                session['actor'] = "user"
                
                return redirect(url_for('userhome'))

            else:
                data = {
                    'error': "Invalid Credentials"
                }
                return render_template('loginuser.html',data=data)

        else:
            data = {
                    'error': "Invalid Credentials"
                }
            return render_template('loginuser.html',data=data)



@app.route('/loginadmin',methods=['POST','GET'])
def loginadmin():
    if request.method == 'GET':
        data = {
            'error' : ""
        }
        return render_template('loginadmin.html',data=data)

    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        admin = Admin.query.filter_by(username=username).first()
        if admin:

            if password == admin.password:
                session['user_id'] = admin.id
                session['actor'] = "admin"
                data = {
                    'tab' : "#addbook",
                    'flag' : 99
                }
                return redirect(url_for('adminhome',tab=1,flag=99))

            else:
                data = {
                    'error': "Invalid Credentials"
                }
                return render_template('loginadmin.html',data=data)

        else:
            data = {
                    'error': "Invalid Credentials"
                }
            return render_template('loginadmin.html',data=data)
   

@app.route('/signup',methods=['POST','GET'])
def signup():
    if request.method == 'GET':
        data = {
                'fname' : "",
                'lname' : "",
                'email' : "",
                'username':"",
                "error" : ""
                
            }
        return render_template('signup.html',data=data)

    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        if len(password) < 6:
            data = {
                'name' : fname,
                'lname' : lname,
                'email' : email,
                'username' : username,
                'error' : "Password too short",
            }
            
            return render_template('signup.html',data = data)
            

        user = User.query.filter_by(email=email).first()
        #print(user)
        if user:
            data = {
                'fname' : fname,
                'lname' : lname,
                'username' : username,
                'email' : "",
                'error' : "Email already registered"
            }
            
            return render_template('signup.html',data = data)

        else:
            db.session.add(User(fname=fname,lname=lname,email=email,password=password,username=username))
            db.session.commit()
            user = User.query.filter_by(username=username).first()
            session['user_id'] = user.id
            session['actor'] = "user"
            
            return redirect(url_for('userhome'))
        

@app.route('/logout')
def logout():
    session.clear()
    return render_template('index.html')


@app.route('/addbook',methods=['POST'])
def addbook():
    bookname = request.form['bookname']
    author = request.form['author']
    year = request.form['year']
    #print(bookname,author,year)
    db.session.add(Books(bookname=bookname,author=author,year=year))
    db.session.commit()
    
    return redirect(url_for('adminhome',tab=1,flag=5))
    
    
@app.route('/addadmin',methods=['POST'])
def addadmin():
    fname = request.form['fname']
    lname = request.form['lname']
    email = request.form['email']
    username = request.form['username']
    password = request.form['password']
    db.session.add(Admin(fname=fname,lname=lname,email=email,username=username,password=password))
    db.session.commit()
    books = db.session.query(Books,Bookstatus).outerjoin(Bookstatus).all()

    return redirect(url_for('adminhome',tab=2,flag=6))

@app.route('/issuebook',methods=['POST'])
def issuebook():
    bookid = request.form['issuebookid']
    userid = request.form['issueuserid']
    book = Books.query.filter_by(id = bookid).first()
   
    user = User.query.filter_by(id = userid).first()
    if user:
        if book:
            issuedbooks = Bookstatus.query.filter_by(book_id = bookid).first()
            
            if issuedbooks:
                return redirect(url_for('adminhome',tab=4,flag=0))

            else:
                today = date.today()
                returndate = today + timedelta(days=14)
            
                db.session.add(Bookstatus(book_id = bookid,user_id= userid,issuedate=today,returndate=returndate,fine=0))
                db.session.commit()
                
                return redirect(url_for('adminhome',tab=4,flag=2))
               

        else:
            #print("Book Id invalid")
            return redirect(url_for('adminhome',tab=4,flag=0))


    else:
        #print("User Id invalid")
        books = db.session.query(Books,Bookstatus).outerjoin(Bookstatus).all()
        return redirect(url_for('adminhome',tab=4,flag=1))
        

@app.route('/returnbook',methods=['POST'])
def returnbook():
    bookid = request.form['returnbookid']
    
    book = Bookstatus.query.filter_by(book_id = bookid).first()

    if book:
        Bookstatus.query.filter_by(book_id = bookid).delete() 
        db.session.commit()
        
        #print("Book returned")
        return redirect(url_for('adminhome',tab=4,flag=3))
        

    else:
        #print("Book ID invalid")
    
        return redirect(url_for('adminhome',tab=4,flag=4))
        

# Invalid book ID for issue = 0
# invalid book id for return = 4
# Invalid User Id = 1
# Success Issue = 2
# Success return = 3
# book added = 5
# admin added = 6

@app.route('/adminhome/<tab>/<flag>')
def adminhome(tab,flag):
    #books = db.session.query(Books,Bookstatus).outerjoin(Bookstatus).all()
    books = db.session.query(Books,Bookstatus,User).outerjoin(Bookstatus,Books.id == Bookstatus.book_id).outerjoin(User,Bookstatus.user_id == User.id).all()
    users = User.query.all()
    print(users)
    for book in books:
        if book[1]: 
            today = date.today()
            extradays = today - book[1].returndate           
            if extradays.days > 0:
                book[1].fine = 10*extradays.days
    return render_template('adminhome.html',books = books,tab=tab, flag=flag,users=users)



@app.route('/userhome')
def userhome():
    result = db.session.query(User,Books,Bookstatus).filter(User.id == Bookstatus.user_id,).filter(Books.id==Bookstatus.book_id).filter(User.id == session['user_id']).all()
    booklist = db.session.query(Books,Bookstatus).outerjoin(Bookstatus).all()
    user = User.query.filter_by(id=session['user_id']).first()
    for books in result:
        today = date.today()
        extradays = today - books[2].returndate           
        if extradays.days > 0:
            books[2].fine = 10*extradays.days
    
    return render_template('userhome.html',books = booklist,mybooks = result,user=user)

    

@app.route('/issue',methods=['POST','GET'])
def issue():
    if request.method == 'POST':
        bookid = request.form['issuebookid']
        userid = request.form['issueuserid']
        print("Book id = ",bookid,"Userid = ",userid)
        book = db.session.query(Books).filter(Books.id == bookid).first()
        user = db.session.query(User).filter(User.id == userid).first()
        books = db.session.query(Books,Bookstatus,User).outerjoin(Bookstatus,Books.id == Bookstatus.book_id).outerjoin(User,Bookstatus.user_id == User.id).all()
        users= User.query.all()
        print(users)
        if user:
            if book:
                issuedbooks = Bookstatus.query.filter_by(book_id = bookid).first()
            
                if issuedbooks:
                    print("Book Issued")
                    return redirect(url_for('adminhome',tab=4,flag=0))
                else:
                    print("Modal should be shown")
                    for b in books:
                        if b[1]: 
                            today = date.today()
                            extradays = today - b[1].returndate           
                            if extradays.days > 0:
                                b[1].fine = 10*extradays.days

                    return render_template('adminhome.html',tab=4,flag=99,modal=1,book = book,user = user,books=books,users=users)
            else:
                return redirect(url_for('adminhome',tab=4,flag=0))

        else:
            return redirect(url_for('adminhome',tab =4,flag=1 ))
        

@app.route('/changepassword',methods=['POST'])
def changepassword():
    if request.method=="POST":
        oldpassword = request.form['oldpassword']
        newpassword = request.form['newpassword']
        confirmpassword = request.form['confirmpassword']
        result = db.session.query(User,Books,Bookstatus).filter(User.id == Bookstatus.user_id,).filter(Books.id==Bookstatus.book_id).filter(User.id == session['user_id']).all()
        booklist = db.session.query(Books,Bookstatus).outerjoin(Bookstatus).all()
        user = User.query.filter_by(id=session['user_id']).first()
        for books in result:
            today = date.today()
            extradays = today - books[2].returndate           
            if extradays.days > 0:
                books[2].fine = 10*extradays.days

        user_id = session['user_id']
        user = User.query.filter_by(id = user_id).first()
        if user:
            if oldpassword == user.password:
                if newpassword == confirmpassword:
                    user.password = newpassword
                    db.session.commit()
                    message = "Password Changed Successfully!!"
                    return render_template('userhome.html',message=message,tab=3,user=user,books = booklist,mybooks = result)

                else:
                    error = "New Password and Confirm password doesn't match!!"
                    return render_template('userhome.html',error=error,tab=3,user=user,books = booklist,mybooks = result)

            else:
                error = "Incorrect Old password!!"
                return render_template('userhome.html',error=error,tab=3,user=user,books = booklist,mybooks = result)











if __name__ == "__main__":
    app.run(debug = True)