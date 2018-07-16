set @usn='1RV15CS168';
SET @sub='12HSI51';
SELECT @Sem:= attendance.student.Semester,@Sec:=attendance.student.Section from attendance.student where attendance.student.USN=@usn;

select attendance.completed_classes.Date_time,IF(exists(select * from attendance.attendance where attendance.attendance.USN=@usn and attendance.attendance.Date_time=attendance.completed_classes.Date_time and attendance.attendance.Teacher_id=attendance.completed_classes.Teacher_id),1,0) as Pressent from attendance.completed_classes where attendance.completed_classes.Subject_Subject_code = @sub AND (attendance.completed_classes.Section_elective = @Sec OR attendance.completed_classes.Section_elective = 
		(SELECT attendance.elective.Classroom_Section_elective FROM attendance.elective WHERE attendance.elective.Student_USN=@usn AND attendance.elective.Subject_Subject_code=@sub))