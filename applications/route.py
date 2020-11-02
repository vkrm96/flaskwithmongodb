from applications import app, db, api
from flask import render_template, request, Response, json, flash, redirect, url_for, session, jsonify
from applications.models import User, Course, Enrollement
from applications.forms import LoginForm, RegisterForm
from flask_restplus import Resource
from werkzeug.utils import cached_property

courseData=[{"courseID":"1111","title":"PHP 111","description":"Intro to PHP","credits":"3","term":"Fall, Spring"}, {"courseID":"2222","title":"Java 1","description":"Intro to Java Programming","credits":"4","term":"Spring"}, {"courseID":"3333","title":"Adv PHP 201","description":"Advanced PHP Programming","credits":"3","term":"Fall"}, {"courseID":"4444","title":"Angular 1","description":"Intro to Angular","credits":"3","term":"Fall, Spring"}, {"courseID":"5555","title":"Java 2","description":"Advanced Java Programming","credits":"4","term":"Fall"}]
#####################################################
@api.route('/api', '/api/')
class GetAndPost(Resource):
    #Get all data
    def get(self):
        return jsonify(User.objects.all())
    # post
    def post(self):
        data=api.payload
        user = User(user_id=data['user_id'], email=data['email'], first_name=data['first_name'], last_name=data['last_name'])
        user.set_password(data['password'])
        user.save()
        return jsonify(User.objects(user_id=data['user_id']))
#Get one
@api.route('/api/<idx>')
class GetUpdateDelete(Resource):
    def get(self,idx):
        return jsonify(User.objects(user_id=idx))
#put

    def put(self,idx):
        data=api.payload
        User.objects(user_id=idx).update(**data)
        return jsonify(User.objects(user_id=idx))

#Delete
    def delete(self,idx):

        User.objects(user_id=idx).delete()
        return jsonify("data is deleted")
##########################################################
@app.route("/")
@app.route("/index")
@app.route("/home")
def index():
    return render_template("index.html", index=True)

@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get('username'):
        return redirect(url_for('index'))
    form=LoginForm()
    if form.validate_on_submit():
        email=form.email.data
        password=form.password.data
        user=User.objects(email=email).first()
        if user and user.get_password(password):
            flash(f"{user.first_name}, sucessfully loged in", "success")
            session['user_id']=user.user_id
            session['username']=user.first_name
            return redirect("/index")
        else:
            flash("Something went wrong", "danger" )
    return render_template("login.html",form=form, login=True)

@app.route("/logout")
def logout():
    session['user_id']=False
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route("/courses/")
@app.route("/courses/<term>")
def courses(term="2019"):

    classes=Course.objects.order_by("+courseID")
    return render_template("courses.html", courseData=classes, term=term, courses=True)

@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get('username'):
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        user_id=User.objects.count()
        user_id +=1
        email=form.email.data
        password=form.password.data
        first_name=form.first_name.data
        last_name=form.last_name.data

        user = User(user_id=user_id, email=email, first_name=first_name, last_name=last_name)
        user.set_password(password)
        user.save()
        flash("You have successfully registered", "sucess")
        return redirect(url_for("index"))
    return render_template("register.html", title="Register", form=form, register=True)

@app.route("/enrollement", methods=["GET", "POST"])
def enrollement():
    if not session.get('username'):
        return redirect(url_for('login'))
    courseID=request.form.get('courseID')
    courseTitle=request.form.get('title')
    user_id=session.get('user_id')
    if courseID:
        if Enrollement.objects(user_id=user_id, courseID=courseID):
            flash("Already registered in this course { courseTitle }", "danger")
            return redirect(url_for("courses"))
        else:
            Enrollement(user_id=user_id, courseID=courseID).save()
            flash("you are enrolled in {courseTitle}", "sucess")
    classes = list(User.objects.aggregate(*[
    {
        '$lookup': {
            'from': 'enrollement',
            'localField': 'user_id',
            'foreignField': 'user_id',
            'as': 'r1'
        }
    }, {
        '$unwind': {
            'path': '$r1',
            'includeArrayIndex': 'r1_id',
            'preserveNullAndEmptyArrays': False
        }
    }, {
        '$lookup': {
            'from': 'course',
            'localField': 'r1.courseID',
            'foreignField': 'courseID',
            'as': 'r2'
        }
    }, {
        '$unwind': {
            'path': '$r2',
            'preserveNullAndEmptyArrays': False
        }
    }, {
        '$match': {
            'user_id': user_id
        }
    }, {
        '$sort': {
            'courseID': 1
        }
    }
]))

    return render_template("enrollement.html", enrollement=True, title="Enrollement", classes=classes)

#@app.route("/api/")
#@app.route("/api/<idx>")
#def api(idx = None):
#    if(idx == None):
#        jdata=courseData
#    else:
#        jdata= courseData[int(idx)]
#    return Response(json.dumps(jdata))



@app.route("/user")
def user():
    #User(user_id=1, first_name="Vikram", last_name="Choudhary", email="vikram@123.com", password="vikram123").save()
    #User(user_id=2, first_name="pravin", last_name="Choudhary", email="pravin@123.com", password="pravin123").save()
    users=User.objects.all()
    return render_template("user.html", users=users)
