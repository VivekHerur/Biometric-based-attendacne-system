SELECT 
    attendance.marks.Subject_Subject_code,
    attendance.marks.Test1,
    attendance.marks.Test2,
    attendance.marks.Test3,
    attendance.marks.AS_SS AS Assigment_Lab,
    attendance.marks.Internal_Lab
FROM
    attendance.marks
WHERE
    attendance.marks.Student_USN = '1RV15CS162';

    