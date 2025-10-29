from flask import Flask, jsonify,request,url_for,redirect,render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Student(db.Model):
    student_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    roll_number = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100) )


class Course(db.Model):
    courses = {'course-1' : 1 , 'course-2' : 2 , 'course-3' : 3 , 'course-4' : 4 }
    course_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    course_name = db.Column(db.String(100), nullable=False)
    course_code = db.Column(db.String(20), unique=True, nullable=False)
    course_description = db.Column(db.String(200) )
    
    
class Enrollments(db.Model):
    enrollment_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    estudent_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    ecourse_id = db.Column(db.Integer, db.ForeignKey('course.course_id'), nullable=False)
    
app.app_context().push()
# db.create_all()

@app.route('/',methods=['GET', 'POST']) 
def home():
    student = Student.query.all()
    return render_template('index.html' , students=student)


@app.route('/student/create', methods=['GET', 'POST'])
def create_student():
    if request.method == 'GET':
        return render_template('create_student.html')
    
    elif request.method == 'POST':
        roll_number = request.form['roll']
        first_name = request.form['f_name']
        last_name = request.form['l_name']
        scourse = request.form['courses']
        
        exists = Student.query.filter_by(roll_number=roll_number).first()
        if exists is None:
      
            db.session.add(Student(roll_number=roll_number, first_name=first_name, last_name=last_name))
            db.session.commit()
            courses = request.form.getlist('courses')
            for course in courses:
                student=Student.query.filter_by(roll_number=roll_number).first()
                student_id = student.student_id if student else None
                course_id=Course.courses.get(course)
                if student_id and course_id:
                    enrollment = Enrollments(estudent_id=student_id, ecourse_id=course_id)
                    db.session.add(enrollment)
                    db.session.commit()
            return redirect(url_for('home'))
        return render_template('exists.html')

        db.session.commit()
        
        return redirect(url_for('home'))
    

@app.route('/student/<int:student_id>/delete', methods=['GET', 'POST'])
def delete(student_id):
    Student.query.filter_by(student_id=student_id).delete()
    Enrollments.query.filter_by(estudent_id=student_id).delete()
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/student/<int:student_id>/', methods=['GET'])
def student_detail(student_id):
    student = Student.query.filter_by(student_id=student_id).first()
    enrollments = Enrollments.query.filter_by(estudent_id=student_id).all()
    course_ids = [enrollment.ecourse_id for enrollment in enrollments]
    courses = Course.query.filter(Course.course_id.in_(course_ids)).all()
    return render_template('student_detail.html', student=student, courses=courses)

# @app.route('/student/<int:student_id>')
# def student_detail(student_id):
#     student = Student.query.filter_by(studentid=student_id).first()
#     enrollments = Enrollments.query.filter_by(estudentid=student_id).all()
#     enrollment_details = []
#     for enroll in enrollments:
#         course = Course.query.filter_by(courseid=enroll.ecourseid).first()
#         if course:
#             enrollment_details.append({
#                 'course_code': course.coursecode,
#                 'course_name': course.coursename,
#                 'course_description': course.coursedescription
#             })
#     return render_template('student_detail.html', student=student, enrollment_details=enrollment_details)


@app.route('/<int:student_id>/update', methods=['GET', 'POST'])
def update(student_id):
    student = Student.query.filter_by(student_id=student_id).first()
    if request.method == 'GET':
        enrollments = Enrollments.query.filter_by(estudent_id=student_id).all()
        course_ids = [enrollment.ecourse_id for enrollment in enrollments]
        return render_template('update_student.html', student=student, course_ids=course_ids)
    
    elif request.method == 'POST':
        student.roll_number = request.form['roll']
        student.first_name = request.form['f_name']
        student.last_name = request.form['l_name']
        
        Enrollments.query.filter_by(estudent_id=student_id).delete()
        db.session.commit()
        
        courses = request.form.getlist('courses')
        for course in courses:
            course_id=Course.courses.get(course)
            enrollment = Enrollments(estudent_id=student_id, ecourse_id=course_id)
            db.session.add(enrollment)
            db.session.commit()
        
        db.session.commit()
        return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
    
    
