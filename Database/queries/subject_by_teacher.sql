SELECT 
    attendance.schedule.Classroom_Semester,
    attendance.schedule.Classroom_Section_elective,
    attendance.schedule.Subject_Subject_code
FROM
    attendance.schedule
WHERE
    attendance.schedule.Teacher_Teacher_id = '1CS02'
GROUP BY attendance.schedule.Classroom_Semester , attendance.schedule.Classroom_Section_elective , attendance.schedule.Subject_Subject_code