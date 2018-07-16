from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
from datetime import timedelta
import re
app = Flask(__name__)

uusn=0
#Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Suraj1997'
app.config['MYSQL_DB'] = 'attendance'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

#init MYSQL
mysql = MySQL(app)

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=10)


x=0
#User login
@app.route('/', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        #Get Form Fields
        username = request.form['username']
        global x
        x=username
        password_candidate = request.form['password']

        #Create cursor
        cur1 = mysql.connection.cursor()
        cur2 = mysql.connection.cursor()
        cur3 = mysql.connection.cursor()


        #Get user by username
        result1 = cur1.execute("SELECT * FROM student WHERE USN = %s",[username])
        result2 = cur2.execute("SELECT * FROM teacher WHERE Teacher_id = %s",[username])
        result3 = cur3.execute("SELECT * FROM admin WHERE idAdmin = %s",[username])

        if result1 > 0:
            #Get Stored hash 
            data = cur1.fetchone()
            password = data['Password']
            name1 = data['First_name']
            name2 = data['Middle_name']
            name3 = data['Last_name']
            semester = data['Semester']
            section = data['Section']

            #Password comparison
            if sha256_crypt.verify(password_candidate, password):
                #PASSED
                session['logged_in'] = True
                session['username']=username
                session['name']=name1
                session['name2']=name2
                session['name3']=name3
                session['semester']=semester
                session['section']=section
                
                #flash('You are now logged in', 'success')
                return redirect(url_for('dashboard_student'))
            else:
                error = 'Invalid password'
                return render_template('index.html', error=error)
            #Close connection
            cur1.close()

        elif result2 > 0:
            #Get Stored hash 
            data = cur2.fetchone()
            password = data['Password']
            name1 = data['First_name']
            name2 = data['Middle_name']
            name3 = data['Last_name']

            #Password comparison
            if sha256_crypt.verify(password_candidate, password):
                #PASSED
                session['logged_in'] = True
                session['username']=username
                session['name']=name1
                session['name2']=name2
                session['name3']=name3
                
                #flash('You are now logged in', 'success')
                return redirect(url_for('dashboard_teacher'))
            else:
                error = 'Invalid password'
                return render_template('index.html', error=error)
            #Close connection
            cur2.close()

        elif result3 > 0:
            #Get Stored hash 
            data = cur3.fetchone()
            password = data['Password']
            name = data['idAdmin']

            #Password comparison
            if sha256_crypt.verify(password_candidate, password):
                #PASSED
                session['logged_in'] = True
                session['name']=name
                
                #flash('You are now logged in', 'success')
                return redirect(url_for('dashboard_admin'))
            else:
                error = 'Invalid password'
                return render_template('index.html', error=error)
            #Close connection
            cur3.close()
        else:
            #If user is not present in database
            error = 'Username not found'
            return render_template('index.html', error=error)


    return render_template('index.html')

#To prevent direct access through path
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Please Login', 'danger')
            return redirect(url_for('login'))
    return wrap

#To end session and logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You are now logged out','success')
    return redirect(url_for('login'))

class RegisterForm(Form):
    password = PasswordField('Password', [validators.DataRequired(), validators.EqualTo('confirm', message='Passwords do not match')])
    confirm = PasswordField('Confirm Password')

@app.route('/changepwd', methods=['GET', 'POST'])
def changepwd():
    
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        if len(str(form.password.data)) < 8:
            error = 'Please enter a password of length 8 characters or more'
            return render_template('change.html', error=error, form=form)
            
        password = sha256_crypt.encrypt(str(form.password.data))
        cur = mysql.connection.cursor()

        cur.execute("UPDATE student set password = %s where USN = %s",[password,x])
        
        mysql.connection.commit()
        cur.close()

        flash('Your password is changed','success')
        session.clear()
        return redirect(url_for('login'))
    return render_template('change.html', form=form)

#Link to the dashboard
@app.route('/dashboard_student')
@is_logged_in
def dashboard_student():
    return render_template('dashboard_student.html')

@app.route('/dashboard_teacher')
@is_logged_in
def dashboard_teacher():
    return render_template('dashboard_teacher.html')

@app.route('/dashboard_admin')
@is_logged_in
def dashboard_admin():
    return render_template('dashboard_admin.html')

#Link to About
@app.route('/aboutstudent')
def aboutstudent():
    return render_template('aboutstudent.html')

@app.route('/aboutteacher')
def aboutteacher():
    return render_template('aboutteacher.html')

@app.route('/aboutadmin')
def aboutadmin():
    return render_template('aboutadmin.html')

@app.route('/enter_details')
def enterdetails():
    return render_template('details2.html')

y=0
@app.route('/studentwiseattendance', methods=['GET','POST'])
def studentwiseattendance():
    cur = mysql.connection.cursor()
    cur2 = mysql.connection.cursor()
    cur3 = mysql.connection.cursor()
    cur4 = mysql.connection.cursor()
    cur3.execute("SELECT DISTINCTROW student.USN, student.First_name, student.Last_name FROM attendance.student, attendance.teacher,attendance.schedule WHERE teacher.Teacher_id = %s AND teacher.Teacher_id = schedule.Teacher_Teacher_id AND student.Semester = schedule.Classroom_Semester AND student.Section = schedule.Classroom_Section_elective",[x])
    names=cur3.fetchall()
    if request.method=='POST':
        username=request.form['username']
        global y
        y=username
        user = cur2.execute("SELECT * FROM student where USN = %s",[username])
        if user==0:
            error='USN NOT FOUND'
            return render_template('studentwiseattendance.html',error=error, names=names)
        cur.execute("SET @usn = %s",[username])
        cur.execute("SELECT @Sem:= attendance.student.Semester,@Sec:=attendance.student.Section from attendance.student where attendance.student.USN=@usn")
        student_data= cur.execute("SELECT attendance.subject.Subject_code AS Subject, (SELECT COUNT(*) FROM attendance.attendance WHERE attendance.attendance.USN = @usn AND (attendance.attendance.Teacher_id , attendance.attendance.Date_time) IN (SELECT attendance.completed_classes.Teacher_id, attendance.completed_classes.Date_time FROM attendance.completed_classes WHERE attendance.completed_classes.Subject_Subject_code = attendance.subject.Subject_code)) AS Attended, (SELECT COUNT(*) FROM attendance.completed_classes WHERE attendance.completed_classes.Subject_Subject_code = attendance.subject.Subject_code AND (attendance.completed_classes.Section_elective = @Sec OR attendance.completed_classes.Section_elective = (SELECT attendance.elective.Classroom_Section_elective FROM attendance.elective WHERE attendance.elective.Student_USN=@usn AND attendance.elective.Subject_Subject_code=attendance.subject.Subject_code))) AS Total, IFNULL((SELECT Attended) / (SELECT Total) * 100,0) AS Percentage FROM attendance.subject WHERE attendance.subject.Subject_code IN (SELECT attendance.subject.Subject_code WHERE attendance.subject.Is_elective = 0 AND attendance.subject.Semester = @Sem) OR attendance.subject.Subject_code IN (SELECT attendance.elective.Subject_Subject_code FROM attendance.elective WHERE attendance.elective.Student_USN = @usn)")
        cur4.execute("SELECT attendance.marks.Subject_Subject_code,attendance.marks.Test1,attendance.marks.Test2,attendance.marks.Test3,attendance.marks.AS_SS AS Assigment_Lab,attendance.marks.Internal_Lab FROM attendance.marks WHERE attendance.marks.Student_USN = %s",[username])
        marks=cur4.fetchall()
        percentages=cur.fetchall()
        return render_template('studentwisetable.html',percentages=percentages, name=username,marks=marks)
    cur.close()
    cur2.close()
    cur3.close()
    cur4.close()
    return render_template('studentwiseattendance.html',names=names)

@app.route('/addteacher', methods=['GET','POST'])
def addteacher():
    cur = mysql.connection.cursor()
    if request.method=='POST':
        id=request.form['id']
        fn=request.form['first']
        mn=request.form['middle']
        ln=request.form['last']
        pas=sha256_crypt.hash(id)
        cur.execute("INSERT INTO attendance.teacher (Teacher_id, First_name, Middle_name, Last_name, Password) VALUES (%s,%s,%s,%s,%s)",[id,fn,mn,ln,pas])
        mysql.connection.commit()
        flash('Teacher Added','success')
        return render_template('details2.html')
    cur.close()
    return render_template('addteacher.html')

@app.route('/addsubject', methods=['GET','POST'])
def addsubject():
    cur = mysql.connection.cursor()
    if request.method=='POST':
        id=request.form['id']
        fn=request.form['sn']
        sem=request.form['sem']
        ls=request.form['opt']
        ele=request.form['elec']
        if ele=="E":
            ele=1
        else:
            ele=0

        if ls=="Self Study":
            ls=1
        elif ls=="Lab":
            ls=0
        else:
            ls=2
        cur.execute("INSERT INTO attendance.subject (Subject_code, Subject_Name, LB_AS, Is_elective, Semester) VALUES (%s, %s," + str(ls) + ","+ str(ele) + ","+str(sem)+")",[id,fn])
        mysql.connection.commit()
        flash('Subject Added','success')
        return render_template('details2.html')
    cur.close()
    return render_template('addsubject.html')

@app.route('/addstudent', methods=['GET','POST'])
def addstudent():
    cur = mysql.connection.cursor()
    cur2 = mysql.connection.cursor()
    if request.method=='POST':
        id=request.form['id']
        fn=request.form['first']
        mn=request.form['middle']
        ln=request.form['last']
        pas=sha256_crypt.hash(id)
        sem=request.form['sem']
        sec=request.form['sec']
        cid=request.form['cid']
        r=cur2.execute("SELECT * FROM attendance.teacher WHERE Teacher_id = %s",[cid])
        if r<=0:
            flash('Counselor ID not found','danger')
            return render_template('details2.html')
        else:
            cur.execute("INSERT INTO attendance.student (USN, First_name, Middle_name, Last_name, Password, Semester, Section, Counselor) VALUES (%s,%s,%s,%s,%s," + str(sem) +",%s,%s)",[id,fn,mn,ln,pas,sec,cid])
            mysql.connection.commit()
            flash('Student Added','success')
            return render_template('details2.html')
    cur.close()
    cur2.close()
    return render_template('addstudent.html')

@app.route('/addschedule', methods=['GET','POST'])
def addschedule():
    cur = mysql.connection.cursor()
    if request.method=='POST':
        sem=request.form['sem']
        sec=request.form['sec']
        time=request.form['time']
        sub=request.form['sub']
        tid=request.form['tid']
        week=request.form['week']
        cur.execute("INSERT INTO attendance.schedule (Classroom_Semester, Classroom_Section_elective, Date_time, Subject_Subject_code, Teacher_Teacher_id, Week) VALUES ("+ str(sem) + ", %s, %s, %s, %s,"+ str(week)+")",[sec,time,sub,tid])
        mysql.connection.commit()
        flash('Schedule Added','success')
        return render_template('details2.html')
    cur.close()
    return render_template('addschedule.html')

@app.route('/modifyschedule', methods=['GET','POST'])
def modifyschedule():
    cur = mysql.connection.cursor()
    if request.method=='POST':
        sem=request.form['sem']
        sec=request.form['sec']
        time=request.form['time']
        sub=request.form['sub']
        tid=request.form['tid']
        week=request.form['week']
        sem2=request.form['sem2']
        sec2=request.form['sec2']
        time2=request.form['time2']
        week2=request.form['week2']
        cur.execute("DELETE FROM attendance.schedule WHERE Classroom_Semester="+str(sem2)+" and Classroom_Section_elective=%s and Date_time=%s and Week="+str(week2),[sec2,time2])
        mysql.connection.commit()
        cur.execute("INSERT INTO attendance.schedule (Classroom_Semester, Classroom_Section_elective, Date_time, Subject_Subject_code, Teacher_Teacher_id, Week) VALUES ("+ str(sem) + ", %s, %s, %s, %s,"+ str(week)+")",[sec,time,sub,tid])
        mysql.connection.commit()
        flash('Schedule Modified','success')
        return render_template('details2.html')
    cur.close()
    return render_template('modifyschedule.html')

@app.route('/eraseschedule', methods=['GET','POST'])
def eraseschedule():
    cur = mysql.connection.cursor()
    if request.method=='POST':
        sem2=request.form['sem2']
        sec2=request.form['sec2']
        time2=request.form['time2']
        week2=request.form['week2']
        cur.execute("DELETE FROM attendance.schedule WHERE Classroom_Semester="+str(sem2)+" and Classroom_Section_elective=%s and Date_time=%s and Week="+str(week2),[sec2,time2])
        mysql.connection.commit()
        flash('Schedule Erased','success')
        return render_template('details2.html')
    cur.close()
    return render_template('eraseschedule.html')

@app.route('/view_details')
def viewdetails():
    cur=mysql.connection.cursor()
    cur.execute("SELECT attendance.student.Semester, attendance.student.Section FROM attendance.student GROUP BY attendance.student.Semester , attendance.student.Section")
    data=cur.fetchall()
    cur.close()
    return render_template('viewdetails.html',data=data)

f1=0
f2=0
@app.route('/details/<sem>/<sec>')
def details(sem,sec):
    cur=mysql.connection.cursor()
    global f1
    f1=sem
    global f2
    f2=sec
    cur.execute("select attendance.schedule.Subject_Subject_code from attendance.schedule where attendance.schedule.Classroom_Semester = "+str(sem)+" and attendance.schedule.Classroom_Section_elective = %s group by attendance.schedule.Subject_Subject_code",[sec])
    data=cur.fetchall()
    cur.close()
    return render_template('subjectperclass.html',data=data)

@app.route('/details/<code>')
def det(code):
    cur=mysql.connection.cursor()
    cur.execute("SET @sub=%s",[code])
    cur.execute("SET @sec=%s",[f2])
    cur.execute("SET @sem=%s",[f1])
    cur.execute("select attendance.student.USN, IFNULL((SELECT attendance.completed_classes.Date_time FROM attendance.completed_classes WHERE attendance.completed_classes.Subject_Subject_code = @sub AND attendance.completed_classes.Section_elective = @sec AND attendance.completed_classes.Semester = @sem ORDER BY attendance.completed_classes.Date_time limit 0,1 ) in(select attendance.attendance.Date_time from attendance.attendance where attendance.attendance.USN=attendance.student.USN),-1) as 'd1',IFNULL((SELECT attendance.completed_classes.Date_time FROM attendance.completed_classes WHERE attendance.completed_classes.Subject_Subject_code = @sub AND attendance.completed_classes.Section_elective = @sec AND attendance.completed_classes.Semester = @sem ORDER BY attendance.completed_classes.Date_time limit 1,1 ) in(select attendance.attendance.Date_time from attendance.attendance where attendance.attendance.USN=attendance.student.USN),-1) as 'd2',IFNULL((SELECT attendance.completed_classes.Date_time FROM attendance.completed_classes WHERE attendance.completed_classes.Subject_Subject_code = @sub AND attendance.completed_classes.Section_elective = @sec AND attendance.completed_classes.Semester = @sem ORDER BY attendance.completed_classes.Date_time limit 2,1 ) in(select attendance.attendance.Date_time from attendance.attendance where attendance.attendance.USN=attendance.student.USN),-1) as 'd3',IFNULL((SELECT attendance.completed_classes.Date_time FROM attendance.completed_classes WHERE attendance.completed_classes.Subject_Subject_code = @sub AND attendance.completed_classes.Section_elective = @sec AND attendance.completed_classes.Semester = @sem ORDER BY attendance.completed_classes.Date_time limit 3,1 ) in(select attendance.attendance.Date_time from attendance.attendance where attendance.attendance.USN=attendance.student.USN),-1) as 'd4', IFNULL((SELECT attendance.completed_classes.Date_time FROM attendance.completed_classes WHERE attendance.completed_classes.Subject_Subject_code = @sub AND attendance.completed_classes.Section_elective = @sec AND attendance.completed_classes.Semester = @sem ORDER BY attendance.completed_classes.Date_time limit 4,1 ) in(select attendance.attendance.Date_time from attendance.attendance where attendance.attendance.USN=attendance.student.USN),-1) as 'd5' from attendance.student where attendance.student.Semester = @sem and (attendance.student.Section = @sec or @sec in(select attendance.elective.Classroom_Section_elective from attendance.elective where attendance.elective.Student_USN= attendance.student.USN))")
    data=cur.fetchall()
    equate(data)
    cur.close()
    return render_template('viewattendance.html',data=data,sem=f1,sec=f2,code=code)
    

@app.route('/studstudentwiseattendance', methods=['GET','POST'])
def studstudentwiseattendance():
    cur = mysql.connection.cursor()
    username=x
    cur.execute("SET @usn = %s",[x])
    cur.execute("SELECT @Sem:= attendance.student.Semester,@Sec:=attendance.student.Section from attendance.student where attendance.student.USN=@usn")
    student_data= cur.execute("SELECT attendance.subject.Subject_code AS Subject, (SELECT COUNT(*) FROM attendance.attendance WHERE attendance.attendance.USN = @usn AND (attendance.attendance.Teacher_id , attendance.attendance.Date_time) IN (SELECT attendance.completed_classes.Teacher_id, attendance.completed_classes.Date_time FROM attendance.completed_classes WHERE attendance.completed_classes.Subject_Subject_code = attendance.subject.Subject_code)) AS Attended, (SELECT COUNT(*) FROM attendance.completed_classes WHERE attendance.completed_classes.Subject_Subject_code = attendance.subject.Subject_code AND (attendance.completed_classes.Section_elective = @Sec OR attendance.completed_classes.Section_elective = (SELECT attendance.elective.Classroom_Section_elective FROM attendance.elective WHERE attendance.elective.Student_USN=@usn AND attendance.elective.Subject_Subject_code=attendance.subject.Subject_code))) AS Total, IFNULL((SELECT Attended) / (SELECT Total) * 100,0) AS Percentage FROM attendance.subject WHERE attendance.subject.Subject_code IN (SELECT attendance.subject.Subject_code WHERE attendance.subject.Is_elective = 0 AND attendance.subject.Semester = @Sem) OR attendance.subject.Subject_code IN (SELECT attendance.elective.Subject_Subject_code FROM attendance.elective WHERE attendance.elective.Student_USN = @usn)")
    percentages=cur.fetchall()
    cur.close()
    return render_template('studstudentwiseattendance.html',percentages=percentages, name=username)

@app.route('/studmarks')
def studmarks():
    cur = mysql.connection.cursor()
    username=x
    cur.execute("SELECT attendance.marks.Subject_Subject_code,attendance.marks.Test1,attendance.marks.Test2,attendance.marks.Test3,attendance.marks.AS_SS AS Assigment_Lab,attendance.marks.Internal_Lab FROM attendance.marks WHERE attendance.marks.Student_USN = %s",[x])
    marks=cur.fetchall()
    cur.close()
    return render_template('studmarks.html',marks=marks)

@app.route('/his/stud/<code>')
def his(code):
    cur=mysql.connection.cursor()
    username=x
    coursecode= code
    cur.execute("set @usn=%s",[username])
    cur.execute("SET @sub=%s",[coursecode])
    cur.execute("SELECT @Sem:= attendance.student.Semester,@Sec:=attendance.student.Section from attendance.student where attendance.student.USN=@usn")
    lol=cur.execute("select attendance.completed_classes.Date_time,IF(exists(select * from attendance.attendance where attendance.attendance.USN=@usn and attendance.attendance.Date_time=attendance.completed_classes.Date_time and attendance.attendance.Teacher_id=attendance.completed_classes.Teacher_id),1,0) as Pressent from attendance.completed_classes where attendance.completed_classes.Subject_Subject_code = @sub AND (attendance.completed_classes.Section_elective = @Sec OR attendance.completed_classes.Section_elective = (SELECT attendance.elective.Classroom_Section_elective FROM attendance.elective WHERE attendance.elective.Student_USN=@usn AND attendance.elective.Subject_Subject_code=@sub))")
    tabs=cur.fetchall()
    cur.close()
    return render_template('historys.html',coursecode=coursecode,tabs=tabs)

@app.route('/his/teach/<code>')
def hist(code):
    cur=mysql.connection.cursor()
    username=uusn
    coursecode=code
    cur.execute("set @usn=%s",[username])
    cur.execute("SET @sub= %s",[code])
    cur.execute("SELECT @Sem:= attendance.student.Semester,@Sec:=attendance.student.Section from attendance.student where attendance.student.USN=@usn")
    lol=cur.execute("select attendance.completed_classes.Date_time,IF(exists(select * from attendance.attendance where attendance.attendance.USN=@usn and attendance.attendance.Date_time=attendance.completed_classes.Date_time and attendance.attendance.Teacher_id=attendance.completed_classes.Teacher_id),1,0) as Pressent from attendance.completed_classes where attendance.completed_classes.Subject_Subject_code = @sub AND (attendance.completed_classes.Section_elective = @Sec OR attendance.completed_classes.Section_elective = (SELECT attendance.elective.Classroom_Section_elective FROM attendance.elective WHERE attendance.elective.Student_USN=@usn AND attendance.elective.Subject_Subject_code=@sub))")
    tabs=cur.fetchall()
    cur.close()
    return render_template('historyt.html',coursecode=coursecode,tabs=tabs,name=uusn)



@app.route('/code/<code>')
def sub(code):
    cur=mysql.connection.cursor()
    cur2=mysql.connection.cursor()
    cur3=mysql.connection.cursor()
    username=x
    coursecode=code
    cur2.execute("SELECT subject.Subject_Name from subject where Subject_code = %s",[coursecode])
    cur.execute("SET @usn = %s",[x])
    cur.execute("SET @sub= %s",[coursecode])
    cur.execute("SELECT @Sem:= attendance.student.Semester,@Sec:=attendance.student.Section from attendance.student where attendance.student.USN=@usn")
    data=cur.execute("SELECT (SELECT COUNT(*) FROM attendance.attendance WHERE attendance.attendance.USN = @usn AND (attendance.attendance.Teacher_id , attendance.attendance.Date_time) IN (SELECT attendance.completed_classes.Teacher_id, attendance.completed_classes.Date_time FROM attendance.completed_classes WHERE attendance.completed_classes.Subject_Subject_code = @sub)) AS Attended, (SELECT COUNT(*) FROM attendance.completed_classes WHERE attendance.completed_classes.Subject_Subject_code = @sub AND (attendance.completed_classes.Section_elective = @Sec OR attendance.completed_classes.Section_elective = (SELECT attendance.elective.Classroom_Section_elective FROM attendance.elective WHERE attendance.elective.Student_USN=@usn AND attendance.elective.Subject_Subject_code=@sub))) AS Total, IFNULL((SELECT Attended) / (SELECT Total) * 100,0) AS Percentage")
    cur3.execute("SET @sub=%s",[coursecode])
    cur3.execute("SET @usn=%s",[x])
    lol=cur3.execute("select * from (select 'Test1' AS Marks,attendance.marks.Test1 as Given,(select IF(attendance.subject.LB_AS<=1,40,45) FROM attendance.subject WHERE attendance.subject.Subject_code=attendance.marks.Subject_Subject_code) as Total from attendance.marks where attendance.marks.Student_USN=@usn and attendance.marks.Subject_Subject_code=@sub UNION ALL SELECT 'Test2' ,attendance.marks.Test2,(select IF(attendance.subject.LB_AS<=1,40,45) FROM attendance.subject WHERE attendance.subject.Subject_code=attendance.marks.Subject_Subject_code) from attendance.marks where attendance.marks.Student_USN=@usn and attendance.marks.Subject_Subject_code=@sub UNION ALL SELECT 'Test3' ,attendance.marks.Test3,(select IF(attendance.subject.LB_AS<=1,40,45) FROM attendance.subject WHERE attendance.subject.Subject_code=attendance.marks.Subject_Subject_code) from attendance.marks where attendance.marks.Student_USN=@usn and attendance.marks.Subject_Subject_code=@sub UNION ALL SELECT (SELECT IF(attendance.subject.LB_AS <=1,'Self Study','Assignment') FROM attendance.subject WHERE attendance.subject.Subject_code = @sub),attendance.marks.AS_SS,(select IF(attendance.subject.LB_AS<=1,20,10) FROM attendance.subject WHERE attendance.subject.Subject_code=attendance.marks.Subject_Subject_code) from attendance.marks where attendance.marks.Student_USN=@usn and attendance.marks.Subject_Subject_code=@sub UNION ALL SELECT (SELECT IF(attendance.subject.LB_AS =0,'Lab',NULL) FROM attendance.subject WHERE attendance.subject.Subject_code = @sub),attendance.marks.Internal_Lab,'50' from attendance.marks where attendance.marks.Student_USN=@usn and attendance.marks.Subject_Subject_code=@sub ) T1 where Marks IS NOT NULL")
    percentages=cur.fetchall()
    name=cur2.fetchone()
    tabs=cur3.fetchall()
    cur.close()
    cur2.close()
    cur3.close()
    return render_template('student2.html',percentages=percentages,coursecode=coursecode,name=name,tabs=tabs)

@app.route('/classtaught')
def classtaught():
    cur=mysql.connection.cursor()
    username=x
    cur.execute("SELECT attendance.schedule.Classroom_Semester,attendance.schedule.Classroom_Section_elective,attendance.schedule.Subject_Subject_code FROM attendance.schedule WHERE attendance.schedule.Teacher_Teacher_id = %s GROUP BY attendance.schedule.Classroom_Semester , attendance.schedule.Classroom_Section_elective , attendance.schedule.Subject_Subject_code",[x])
    data=cur.fetchall()
    return render_template('classtaught.html',data=data)

z=0
@app.route('/counselstudents',methods=['GET','POST'])
def counselstudents():
    cur=mysql.connection.cursor()
    cur2=mysql.connection.cursor()
    cur4=mysql.connection.cursor()
    username=x
    cur.execute("SELECT attendance.student.USN,attendance.student.First_name,attendance.student.Middle_name,attendance.student.Last_name,attendance.student.Semester,attendance.student.Section FROM attendance.student WHERE attendance.student.Counselor = %s",[x])
    data=cur.fetchall()
    cur.close()
    cur2.close()
    cur4.close()
    return render_template('counselstudents.html',data=data)

@app.route('/counselstudents/<usn>')
def counselstud(usn):
        #username=request.form['username']
    cur=mysql.connection.cursor()
    cur4=mysql.connection.cursor()
    cur2=mysql.connection.cursor()
    usernames=usn
    global z
    z=usernames
    global uusn
    uusn=usn
    user = cur2.execute("SELECT * FROM student where USN = %s",[usernames])
    if user==0:
        error='USN NOT FOUND'
        return render_template('studentwiseattendance.html',error=error, names=names)
    cur.execute("SET @usn = %s",[usernames])
    cur.execute("SELECT @Sem:= attendance.student.Semester,@Sec:=attendance.student.Section from attendance.student where attendance.student.USN=@usn")
    student_data= cur.execute("SELECT attendance.subject.Subject_code AS Subject, (SELECT COUNT(*) FROM attendance.attendance WHERE attendance.attendance.USN = @usn AND (attendance.attendance.Teacher_id , attendance.attendance.Date_time) IN (SELECT attendance.completed_classes.Teacher_id, attendance.completed_classes.Date_time FROM attendance.completed_classes WHERE attendance.completed_classes.Subject_Subject_code = attendance.subject.Subject_code)) AS Attended, (SELECT COUNT(*) FROM attendance.completed_classes WHERE attendance.completed_classes.Subject_Subject_code = attendance.subject.Subject_code AND (attendance.completed_classes.Section_elective = @Sec OR attendance.completed_classes.Section_elective = (SELECT attendance.elective.Classroom_Section_elective FROM attendance.elective WHERE attendance.elective.Student_USN=@usn AND attendance.elective.Subject_Subject_code=attendance.subject.Subject_code))) AS Total, IFNULL((SELECT Attended) / (SELECT Total) * 100,0) AS Percentage FROM attendance.subject WHERE attendance.subject.Subject_code IN (SELECT attendance.subject.Subject_code WHERE attendance.subject.Is_elective = 0 AND attendance.subject.Semester = @Sem) OR attendance.subject.Subject_code IN (SELECT attendance.elective.Subject_Subject_code FROM attendance.elective WHERE attendance.elective.Student_USN = @usn)")
    cur4.execute("SELECT attendance.marks.Subject_Subject_code,attendance.marks.Test1,attendance.marks.Test2,attendance.marks.Test3,attendance.marks.AS_SS AS Assigment_Lab,attendance.marks.Internal_Lab FROM attendance.marks WHERE attendance.marks.Student_USN = %s",[usernames])
    marks=cur4.fetchall()
    percentages=cur.fetchall()
    cur.close()
    cur4.close()
    cur2.close()
    return render_template('studentwisetable.html',percentages=percentages, name=usernames,marks=marks)

cde=0
se=0
sc=0
res2=0


@app.route('/edit',methods=['GET','POST'])
def edit():
    cur=mysql.connection.cursor()
    if request.method=='POST':
        code=request.form['code']
        global cde
        cde=code
        sem=request.form['sem']
        global se
        se=sem
        sec=request.form['section']
        global sc
        sc=sec
        cur.execute("SET @sub=%s",[code])
        cur.execute("SET @sec=%s",[sec])
        cur.execute("SET @sem=%s",[sem])
        cur.execute("select attendance.student.USN, IFNULL((SELECT attendance.completed_classes.Date_time FROM attendance.completed_classes WHERE attendance.completed_classes.Subject_Subject_code = @sub AND attendance.completed_classes.Section_elective = @sec AND attendance.completed_classes.Semester = @sem ORDER BY attendance.completed_classes.Date_time limit 0,1 ) in(select attendance.attendance.Date_time from attendance.attendance where attendance.attendance.USN=attendance.student.USN),-1) as 'd1',IFNULL((SELECT attendance.completed_classes.Date_time FROM attendance.completed_classes WHERE attendance.completed_classes.Subject_Subject_code = @sub AND attendance.completed_classes.Section_elective = @sec AND attendance.completed_classes.Semester = @sem ORDER BY attendance.completed_classes.Date_time limit 1,1 ) in(select attendance.attendance.Date_time from attendance.attendance where attendance.attendance.USN=attendance.student.USN),-1) as 'd2',IFNULL((SELECT attendance.completed_classes.Date_time FROM attendance.completed_classes WHERE attendance.completed_classes.Subject_Subject_code = @sub AND attendance.completed_classes.Section_elective = @sec AND attendance.completed_classes.Semester = @sem ORDER BY attendance.completed_classes.Date_time limit 2,1 ) in(select attendance.attendance.Date_time from attendance.attendance where attendance.attendance.USN=attendance.student.USN),-1) as 'd3',IFNULL((SELECT attendance.completed_classes.Date_time FROM attendance.completed_classes WHERE attendance.completed_classes.Subject_Subject_code = @sub AND attendance.completed_classes.Section_elective = @sec AND attendance.completed_classes.Semester = @sem ORDER BY attendance.completed_classes.Date_time limit 3,1 ) in(select attendance.attendance.Date_time from attendance.attendance where attendance.attendance.USN=attendance.student.USN),-1) as 'd4', IFNULL((SELECT attendance.completed_classes.Date_time FROM attendance.completed_classes WHERE attendance.completed_classes.Subject_Subject_code = @sub AND attendance.completed_classes.Section_elective = @sec AND attendance.completed_classes.Semester = @sem ORDER BY attendance.completed_classes.Date_time limit 4,1 ) in(select attendance.attendance.Date_time from attendance.attendance where attendance.attendance.USN=attendance.student.USN),-1) as 'd5' from attendance.student where attendance.student.Semester = @sem and (attendance.student.Section = @sec or @sec in(select attendance.elective.Classroom_Section_elective from attendance.elective where attendance.elective.Student_USN= attendance.student.USN))")
        res=cur.fetchall()
        equate(res)
        return render_template('edittable.html',res=res,sem=sem,sec=sec,code=code)
    cur.close()
    return render_template('edit.html')

def equate(res):
    global res2
    res2=res

@app.route('/insert',methods=['GET','POST'])
def insert():
    if request.method=='POST':
        cur=mysql.connection.cursor()
        #cur2=mysql.connection.cursor()
        #cur2.execute("SET @sub=%s",[cde])
        #cur2.execute("SET @sec=%s",[sc])
        #cur2.execute("SET @sem=%s",[se])
        #cur2.execute("select attendance.student.USN, IFNULL((SELECT attendance.completed_classes.Date_time FROM attendance.completed_classes WHERE attendance.completed_classes.Subject_Subject_code = @sub AND attendance.completed_classes.Section_elective = @sec AND attendance.completed_classes.Semester = @sem ORDER BY attendance.completed_classes.Date_time limit 0,1 ) in(select attendance.attendance.Date_time from attendance.attendance where attendance.attendance.USN=attendance.student.USN),-1) as 'd1',IFNULL((SELECT attendance.completed_classes.Date_time FROM attendance.completed_classes WHERE attendance.completed_classes.Subject_Subject_code = @sub AND attendance.completed_classes.Section_elective = @sec AND attendance.completed_classes.Semester = @sem ORDER BY attendance.completed_classes.Date_time limit 1,1 ) in(select attendance.attendance.Date_time from attendance.attendance where attendance.attendance.USN=attendance.student.USN),-1) as 'd2',IFNULL((SELECT attendance.completed_classes.Date_time FROM attendance.completed_classes WHERE attendance.completed_classes.Subject_Subject_code = @sub AND attendance.completed_classes.Section_elective = @sec AND attendance.completed_classes.Semester = @sem ORDER BY attendance.completed_classes.Date_time limit 2,1 ) in(select attendance.attendance.Date_time from attendance.attendance where attendance.attendance.USN=attendance.student.USN),-1) as 'd3',IFNULL((SELECT attendance.completed_classes.Date_time FROM attendance.completed_classes WHERE attendance.completed_classes.Subject_Subject_code = @sub AND attendance.completed_classes.Section_elective = @sec AND attendance.completed_classes.Semester = @sem ORDER BY attendance.completed_classes.Date_time limit 3,1 ) in(select attendance.attendance.Date_time from attendance.attendance where attendance.attendance.USN=attendance.student.USN),-1) as 'd4', IFNULL((SELECT attendance.completed_classes.Date_time FROM attendance.completed_classes WHERE attendance.completed_classes.Subject_Subject_code = @sub AND attendance.completed_classes.Section_elective = @sec AND attendance.completed_classes.Semester = @sem ORDER BY attendance.completed_classes.Date_time limit 4,1 ) in(select attendance.attendance.Date_time from attendance.attendance where attendance.attendance.USN=attendance.student.USN),-1) as 'd5' from attendance.student where attendance.student.Semester = @sem and (attendance.student.Section = @sec or @sec in(select attendance.elective.Classroom_Section_elective from attendance.elective where attendance.elective.Student_USN= attendance.student.USN))")
        #res2=cur2.fetchall()

        for x in res2:
            for y in range(1,6):
                #print(type(x["d"+str(y)]))
                if (type(request.form.get(x["USN"]+str(y))) is str) and x["d"+str(y)]==0:
                    print('tick')
                    cur3=mysql.connection.cursor()
                    cur4=mysql.connection.cursor()
                    cur3.execute("SELECT attendance.completed_classes.Date_time,attendance.completed_classes.Teacher_id FROM attendance.completed_classes WHERE attendance.completed_classes.Subject_Subject_code = %s AND attendance.completed_classes.Section_elective = %s AND attendance.completed_classes.Semester = %s ORDER BY attendance.completed_classes.Date_time limit " + str(y-1) + ",1",[cde,sc,se])
                    fin=cur3.fetchone()
                    id=fin["Teacher_id"]
                    dt=fin["Date_time"]
                    cur4.execute("INSERT INTO attendance.attendance (USN, Teacher_id, Date_time) VALUES (%s, %s, %s)",[x["USN"],id,dt])
                    mysql.connection.commit()
                    cur3.close()
                    cur4.close()

                elif (type(request.form.get(x["USN"]+str(y))) is str) == False and x["d"+str(y)]==1:
                    print('untick')
                    cur3=mysql.connection.cursor()
                    cur4=mysql.connection.cursor()
                    cur3.execute("SELECT attendance.completed_classes.Date_time,attendance.completed_classes.Teacher_id FROM attendance.completed_classes WHERE attendance.completed_classes.Subject_Subject_code = %s AND attendance.completed_classes.Section_elective = %s AND attendance.completed_classes.Semester = %s ORDER BY attendance.completed_classes.Date_time limit " + str(y-1) + ",1",[cde,sc,se])
                    fin=cur3.fetchone()
                    id=fin["Teacher_id"]
                    dt=fin["Date_time"]
                    cur4.execute("DELETE FROM attendance.attendance WHERE USN=%s and Teacher_id=%s and Date_time = %s",[x["USN"],id,dt])
                    mysql.connection.commit()
                    cur3.close()
                    cur4.close()
        cur.execute("SET @sub=%s",[cde])
        cur.execute("SET @sec=%s",[sc])
        cur.execute("SET @sem=%s",[se])
        cur.execute("select attendance.student.USN, IFNULL((SELECT attendance.completed_classes.Date_time FROM attendance.completed_classes WHERE attendance.completed_classes.Subject_Subject_code = @sub AND attendance.completed_classes.Section_elective = @sec AND attendance.completed_classes.Semester = @sem ORDER BY attendance.completed_classes.Date_time limit 0,1 ) in(select attendance.attendance.Date_time from attendance.attendance where attendance.attendance.USN=attendance.student.USN),-1) as 'd1',IFNULL((SELECT attendance.completed_classes.Date_time FROM attendance.completed_classes WHERE attendance.completed_classes.Subject_Subject_code = @sub AND attendance.completed_classes.Section_elective = @sec AND attendance.completed_classes.Semester = @sem ORDER BY attendance.completed_classes.Date_time limit 1,1 ) in(select attendance.attendance.Date_time from attendance.attendance where attendance.attendance.USN=attendance.student.USN),-1) as 'd2',IFNULL((SELECT attendance.completed_classes.Date_time FROM attendance.completed_classes WHERE attendance.completed_classes.Subject_Subject_code = @sub AND attendance.completed_classes.Section_elective = @sec AND attendance.completed_classes.Semester = @sem ORDER BY attendance.completed_classes.Date_time limit 2,1 ) in(select attendance.attendance.Date_time from attendance.attendance where attendance.attendance.USN=attendance.student.USN),-1) as 'd3',IFNULL((SELECT attendance.completed_classes.Date_time FROM attendance.completed_classes WHERE attendance.completed_classes.Subject_Subject_code = @sub AND attendance.completed_classes.Section_elective = @sec AND attendance.completed_classes.Semester = @sem ORDER BY attendance.completed_classes.Date_time limit 3,1 ) in(select attendance.attendance.Date_time from attendance.attendance where attendance.attendance.USN=attendance.student.USN),-1) as 'd4', IFNULL((SELECT attendance.completed_classes.Date_time FROM attendance.completed_classes WHERE attendance.completed_classes.Subject_Subject_code = @sub AND attendance.completed_classes.Section_elective = @sec AND attendance.completed_classes.Semester = @sem ORDER BY attendance.completed_classes.Date_time limit 4,1 ) in(select attendance.attendance.Date_time from attendance.attendance where attendance.attendance.USN=attendance.student.USN),-1) as 'd5' from attendance.student where attendance.student.Semester = @sem and (attendance.student.Section = @sec or @sec in(select attendance.elective.Classroom_Section_elective from attendance.elective where attendance.elective.Student_USN= attendance.student.USN))")
        res=cur.fetchall()
        equate(res)
        flash('Attendance Updated','success')        
        return render_template('edittable.html',res=res,sem=se,sec=sc,code=cde)    


@app.route('/user/<code>/<sem>/<sec>')
def subdata(code,sem,sec):
    cur=mysql.connection.cursor()
    cod=code
    global cde
    cde=cod
    seme=sem
    global se
    se=seme
    sect=sec
    global sc
    sc=sect
    cur.execute("SET @sub=%s",[cod])
    cur.execute("SET @sec=%s",[sect])
    cur.execute("SET @sem=%s",[seme])
    cur.execute("select attendance.student.USN, IFNULL((SELECT attendance.completed_classes.Date_time FROM attendance.completed_classes WHERE attendance.completed_classes.Subject_Subject_code = @sub AND attendance.completed_classes.Section_elective = @sec AND attendance.completed_classes.Semester = @sem ORDER BY attendance.completed_classes.Date_time limit 0,1 ) in(select attendance.attendance.Date_time from attendance.attendance where attendance.attendance.USN=attendance.student.USN),-1) as 'd1',IFNULL((SELECT attendance.completed_classes.Date_time FROM attendance.completed_classes WHERE attendance.completed_classes.Subject_Subject_code = @sub AND attendance.completed_classes.Section_elective = @sec AND attendance.completed_classes.Semester = @sem ORDER BY attendance.completed_classes.Date_time limit 1,1 ) in(select attendance.attendance.Date_time from attendance.attendance where attendance.attendance.USN=attendance.student.USN),-1) as 'd2',IFNULL((SELECT attendance.completed_classes.Date_time FROM attendance.completed_classes WHERE attendance.completed_classes.Subject_Subject_code = @sub AND attendance.completed_classes.Section_elective = @sec AND attendance.completed_classes.Semester = @sem ORDER BY attendance.completed_classes.Date_time limit 2,1 ) in(select attendance.attendance.Date_time from attendance.attendance where attendance.attendance.USN=attendance.student.USN),-1) as 'd3',IFNULL((SELECT attendance.completed_classes.Date_time FROM attendance.completed_classes WHERE attendance.completed_classes.Subject_Subject_code = @sub AND attendance.completed_classes.Section_elective = @sec AND attendance.completed_classes.Semester = @sem ORDER BY attendance.completed_classes.Date_time limit 3,1 ) in(select attendance.attendance.Date_time from attendance.attendance where attendance.attendance.USN=attendance.student.USN),-1) as 'd4', IFNULL((SELECT attendance.completed_classes.Date_time FROM attendance.completed_classes WHERE attendance.completed_classes.Subject_Subject_code = @sub AND attendance.completed_classes.Section_elective = @sec AND attendance.completed_classes.Semester = @sem ORDER BY attendance.completed_classes.Date_time limit 4,1 ) in(select attendance.attendance.Date_time from attendance.attendance where attendance.attendance.USN=attendance.student.USN),-1) as 'd5' from attendance.student where attendance.student.Semester = @sem and (attendance.student.Section = @sec or @sec in(select attendance.elective.Classroom_Section_elective from attendance.elective where attendance.elective.Student_USN= attendance.student.USN))")
    res=cur.fetchall()
    equate(res)
    cur.close()
    return render_template('edittable.html',res=res,sem=sem,sec=sec,code=code)

            
            #print(type(request.form.get(x["USN"]+'2')) is str)
        # print(type(request.form.get(x["USN"]+'3')) is str)
            #print(type(request.form.get(x["USN"]+'4')) is str)
            #print(type(request.form.get(x["USN"]+'5')) is str)

            

        
                
            


                    


if __name__ == '__main__':
    app.secret_key='dreamlandbiryani'
    app.run(debug=True)
    