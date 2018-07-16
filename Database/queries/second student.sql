SET @usn = '1RV15CS162';
SET @sub='12HSI51';
SELECT @Sem:= attendance.student.Semester,@Sec:=attendance.student.Section from attendance.student where attendance.student.USN=@usn;

SELECT 
	(SELECT COUNT(*) FROM attendance.attendance WHERE attendance.attendance.USN = @usn AND (attendance.attendance.Teacher_id , attendance.attendance.Date_time) IN 
		(SELECT attendance.completed_classes.Teacher_id, attendance.completed_classes.Date_time FROM attendance.completed_classes WHERE attendance.completed_classes.Subject_Subject_code = @sub))
AS Attended, 
	(SELECT COUNT(*) FROM attendance.completed_classes WHERE attendance.completed_classes.Subject_Subject_code = @sub AND (attendance.completed_classes.Section_elective = @Sec OR attendance.completed_classes.Section_elective = 
		(SELECT attendance.elective.Classroom_Section_elective FROM attendance.elective WHERE attendance.elective.Student_USN=@usn AND attendance.elective.Subject_Subject_code=@sub))) 
AS Total, 
	IFNULL((SELECT Attended) / (SELECT Total) * 100,0) AS Percentage
    