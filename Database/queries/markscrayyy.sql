SELECT 
    attendance.marks.Subject_Subject_code,
    attendance.marks.Test1,
    (select IF(attendance.subject.LB_AS<=1,40,45) FROM attendance.subject WHERE attendance.subject.Subject_code=attendance.marks.Subject_Subject_code) as Test1T,
    attendance.marks.Test2,
    (select IF(attendance.subject.LB_AS<=1,40,45) FROM attendance.subject WHERE attendance.subject.Subject_code=attendance.marks.Subject_Subject_code) as Test2T,
    attendance.marks.Test3,
    (select IF(attendance.subject.LB_AS<=1,40,45) FROM attendance.subject WHERE attendance.subject.Subject_code=attendance.marks.Subject_Subject_code) as Test3T,
    attendance.marks.AS_SS AS Assigment_Lab,
    (select IF(attendance.subject.LB_AS<=1,20,10) FROM attendance.subject WHERE attendance.subject.Subject_code=attendance.marks.Subject_Subject_code) as AssigmentT,
    attendance.marks.Internal_Lab
FROM
    attendance.marks
WHERE
    attendance.marks.Student_USN = '1RV15CS162';

    