from flask import Flask, request, render_template, redirect, url_for, session,flash
from flask_restful import Resource, Api
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, Course,Lesson,Blogpost
from database import session as db_session
from sqlalchemy.exc import IntegrityError,PendingRollbackError
import base64
import json
import datetime

app = Flask(__name__)
api = Api(app)
app.secret_key = 'LMSFYNDCAPSTONE_PROJECT_F4I3AL_!M4M'

# Home Route
import base64
@app.route('/')
def index_page():
    username = session.get('username')
    blogs = db_session.query(Blogpost).all()

    try:
        # Convert the binary thumbnail to base64 for each blog in the blogs list
        for blog in blogs:
            if blog.thumbnail:  # Only encode if thumbnail exists
                blog.thumbnail = base64.b64encode(blog.thumbnail).decode('utf-8')
            else:
                blog.thumbnail = None  # Handle missing thumbnails

        return render_template('index.html', username=username, blogs=blogs)

    except PendingRollbackError:
        db_session.rollback()  # Rollback the session if an error has occurred
        return "Transaction failed and was rolled back due to previous issues. Please try again."




# Login Page
@app.get('/login')
def get_login():
    return render_template('login.html')


@app.post('/login')
def user_login():
    email = request.form.get('Email')
    password = request.form.get('Password')

    # Check if the user exists in the database
    user = db_session.query(User).filter_by(email=email).first()

    if user:
        # Verify the password
        if check_password_hash(user.password, password):
            # Store user information in the session
            session['username'] = user.username
            session['role'] = user.role

            if user.role == 'student':
                return render_template('index.html', username=user.username)
            elif user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return render_template('index.html', username=None)
        else:
            return render_template('login.html', error="Incorrect password. Please try again.")
    else:
        return render_template('login.html', error="We can't find your credentials. Kindly sign up with a new account.")


# Sign-In Page
@app.get('/signup')
def signin_page():
    return render_template('signup.html')

@app.post('/signin')
def user_signin():
    name = request.form.get('Username')
    email = request.form.get('Email')
    role = 'student'
    password = request.form.get('Password')

    # new_admin = User(username='Admin', email='admin@codify.com', role='admin', password=generate_password_hash('pass123'))
    # db_session.add(new_admin)
    # db_session.commit()
    

    existing_email = db_session.query(User).filter_by(email=email).first()
    if existing_email:
        return render_template('signup.html', error="The Email already exists. Kindly choose another Email.")

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    new_user = User(username=name, email=email, role=role, password=hashed_password)
    db_session.add(new_user)

    try:
        db_session.commit()
        return render_template('signup.html', success="Account created successfully!")
    except IntegrityError as e:
        db_session.rollback()
        return render_template('signup.html', error=f"An error occurred: {e}")

#--------------------------COURSES VIEWS----------------------------------------------->

#students courses dashboard
@app.route('/courses')
def courses():
    username = session.get('username')
    courses=db_session.query(Course).all()
    # if 'username' not in session or session.get('role') != 'admin' or 'student' :
    #     return render_template('courses.html',no_enroll="Please Login as Student to Access the course",all_course=all_course)
    for course in courses:
        course.thumbnail=base64.b64encode(course.course_thumbnail).decode("utf-8")
    return render_template('courses.html',courses=courses,username=username)
@app.route('/lessons/<int:id>')
def course_lessons(id):
    course = db_session.query(Course).filter_by(id=id).first()
    
    if not course:
        return "Course not found", 404
    
    return render_template('course_lessons.html', course=course)
@app.route('/courses/course_description/<int:id>')
def course_description(id):
    username = session.get('username')
    course = db_session.query(Course).filter_by(id=id).first()
    if course:
        course.thumbnail = base64.b64encode(course.course_thumbnail).decode("utf-8")
    return render_template("course_description.html", course=course,username=username)



#-------------------------------Admin Views--------------------------------->
# Admin Dashboard with Access Control
@app.route('/admin/show-users/')
def show_users():
    # if 'username' not in session or session.get('role') != 'admin':
    #     return redirect(url_for('get_login'))
    users = db_session.query(User).all()
    
    return render_template('showusers.html')


@app.route('/admin/show-courses/')
def show_courses():
    # if 'username' not in session or session.get('role') != 'admin':
    #     return redirect(url_for('get_login'))
    courses = db_session.query(Course).all()
    for course in courses:
        course.thumbnail=base64.b64encode(course.course_thumbnail).decode("utf-8")
    return render_template('showcourses.html',courses=courses)

@app.route('/admin/deletecourse/<int:id>',methods=['POST'])
def deletecourse(id):
    course=db_session.query(Course).get(id)
    db_session.delete(course)
    db_session.commit()
    return redirect(url_for('show_courses',Success="Successfully deleted"))
@app.route('/admin/update_course/<int:course_id>/', methods=['GET', 'POST'])
def update_course(course_id):
    course = db_session.query(Course).filter_by(id=course_id).first()
    if not course:
        return "Course not found", 404

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        
        if not title or not description:
            flash("Title and Description are required.", "error")
            return redirect(url_for('update_course', course_id=course_id))
        
        # Update course details
        course.title = title
        course.description = description

        if 'Thumbnail' in request.files:
            thumbnail = request.files['Thumbnail'].read()
            if thumbnail:
                course.course_thumbnail = thumbnail

        # Extract lessons
        lessons = []
        index = 0
        while True:
            lesson_title = request.form.get(f'lessons[{index}][title]')
            lesson_content = request.form.get(f'lessons[{index}][content]')
            lesson_link = request.form.get(f'lessons[{index}][course_link]')

            if not lesson_title:
                break

            lessons.append({
                'title': lesson_title,
                'content': lesson_content,
                'course_link': lesson_link
            })
            index += 1

        # Remove existing lessons and add updated ones
        db_session.query(Lesson).filter_by(course_id=course_id).delete()

        for lesson in lessons:
            updated_lesson = Lesson(
                title=lesson['title'],
                content=lesson['content'],
                course_link=lesson['course_link'],
                course_id=course.id
            )
            db_session.add(updated_lesson)

        db_session.commit()
        print("Course Updated")
        return redirect(url_for('index_page'))

    existing_lessons = db_session.query(Lesson).filter_by(course_id=course_id).all()
    return render_template('updatecourse.html', course=course, lessons=existing_lessons)

@app.route('/admin/add_course/', methods=['GET', 'POST'])
def add_course():
    if request.method == 'POST':
        # Get course data
        title = request.form['title']
        description = request.form['description']
        course_thumbnail = request.files['Thumbnail'].read()

        # Collect lessons from JSON-formatted data sent with the form
        lessons_data = request.form.get('lessons')
        lessons_list = eval(lessons_data)  # Convert string to Python list

        # Create course instance
        new_course = Course(title=title, description=description,course_thumbnail=course_thumbnail )
        db_session.add(new_course)
        db_session.commit()

        # Add lessons
        for lesson in lessons_list:
            new_lesson = Lesson(
                title=lesson['title'],
                content=lesson['content'],
                course_link=lesson['course_link'],
                course_id=new_course.id
            )
            db_session.add(new_lesson)
        db_session.commit()
        print("Courses Added")
        return redirect(url_for('index_page'))

  
    return render_template('addcourse.html')

@app.route('/admin/addblog/', methods=['GET', 'POST'])
def addblog():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['Description']
        category = request.form['category']
        thumbnail = request.files['Thumbnail'].read()  # Read the uploaded file as binary data
        
        try:
            # Create the blog post instance
            blog = Blogpost(
                title=title,
                category=category,
                description=description,
                thumbnail=thumbnail  # Store the binary image data
            )

            db_session.add(blog)
            db_session.commit()

            return render_template('addblog.html', success=f'{title} successfully added to the Blog page')

        except Exception as e:
            # If an error occurs, print the error and perform a rollback
            print(f"Error occurred: {e}")
            db_session.rollback()  # Rollback any changes if there was an error

            return render_template('addblog.html', error='There was an error while uploading the Blog page')

    return render_template('addblog.html')
@app.route('/admin') 
def admin_dashboard():
    # Check if the user is logged in and is an admin
    # if 'username' not in session or session.get('role') != 'admin':
    #     return redirect(url_for('get_login'))

    users = db_session.query(User).all()
    courses = db_session.query(Course).all()
    students=db_session.query(User).filter_by(role='student').count()
    user_count=students
    courses_count=len(courses)
    print(courses_count)

    return render_template('admin.html', users=users, courses=courses,user_count=user_count,courses_count=courses_count)

#---------------------------------------ADMIN VIEWS END---------------------------> 




@app.route('/certificate/')
def certificate():
    user=session.get('username')
    time = datetime.datetime.now().strftime('%d-%m-%y')
    return render_template('certificate.html',user=user,time=time)


# Logout Route
@app.route('/logout')
def logout():
    session.clear()  # Clear the session
    return redirect(url_for('index_page'))


if __name__ == '__main__':
    app.run(debug=True)
