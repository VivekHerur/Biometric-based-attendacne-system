SET @usn = '1RV15CS162';

SELECT @Sem:= attendance.student.Semester,@Sec:=attendance.student.Section from attendance.student where attendance.student.USN=@usn;

SELECT attendance.subject.Subject_code AS Subject,
	(SELECT COUNT(*) FROM attendance.attendance WHERE attendance.attendance.USN = @usn AND (attendance.attendance.Teacher_id , attendance.attendance.Date_time) IN 
		(SELECT attendance.completed_classes.Teacher_id, attendance.completed_classes.Date_time FROM attendance.completed_classes WHERE attendance.completed_classes.Subject_Subject_code = attendance.subject.Subject_code))
AS Attended, 
	(SELECT COUNT(*) FROM attendance.completed_classes WHERE attendance.completed_classes.Subject_Subject_code = attendance.subject.Subject_code AND (attendance.completed_classes.Section_elective = @Sec OR attendance.completed_classes.Section_elective = 
		(SELECT attendance.elective.Classroom_Section_elective FROM attendance.elective WHERE attendance.elective.Student_USN=@usn AND attendance.elective.Subject_Subject_code=attendance.subject.Subject_code))) 
AS Total, 
	IFNULL((SELECT Attended) / (SELECT Total) * 100,0) AS Percentage
FROM attendance.subject WHERE attendance.subject.Subject_code IN 
    (SELECT attendance.subject.Subject_code WHERE attendance.subject.Is_elective = 0 AND attendance.subject.Semester = @Sem) 
OR attendance.subject.Subject_code IN 
	(SELECT attendance.elective.Subject_Subject_code FROM attendance.elective WHERE attendance.elective.Student_USN = @usn)
    