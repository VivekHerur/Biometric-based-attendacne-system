ALTER TABLE `attendance`.`marks` 
CHANGE COLUMN `Test1` `Test1` DECIMAL(4,2) NULL DEFAULT NULL ,
CHANGE COLUMN `Test2` `Test2` DECIMAL(4,2) NULL DEFAULT NULL ,
CHANGE COLUMN `Test3` `Test3` DECIMAL(4,2) NULL DEFAULT NULL ,
CHANGE COLUMN `AS_SS` `AS_SS` DECIMAL(4,2) NULL DEFAULT NULL ,
CHANGE COLUMN `Internal_Lab` `Internal_Lab` DECIMAL(4,2) NULL DEFAULT NULL ;

INSERT INTO `attendance`.`marks` (`Student_USN`, `Subject_Subject_code`, `Test1`, `Test2`, `Test3`, `AS_SS`, `Internal_Lab`) VALUES ('1RV15CS162', '12CS52', '36.5', '34.5', NULL, NULL, NULL);
INSERT INTO `attendance`.`marks` (`Student_USN`, `Subject_Subject_code`, `Test1`, `Test2`, `Test3`, `AS_SS`, `Internal_Lab`) VALUES ('1RV15CS162', '12CS53', NULL, '38', NULL, NULL, NULL);
INSERT INTO `attendance`.`marks` (`Student_USN`, `Subject_Subject_code`, `Test1`, `Test2`, `Test3`, `AS_SS`, `Internal_Lab`) VALUES ('1RV15CS162', '12CS54', '34.5', '28.5', NULL, NULL, NULL);
INSERT INTO `attendance`.`marks` (`Student_USN`, `Subject_Subject_code`, `Test1`, `Test2`, `Test3`, `AS_SS`, `Internal_Lab`) VALUES ('1RV15CS162', '12CS5A4', '31.5', '34.5', NULL, NULL, NULL);
INSERT INTO `attendance`.`marks` (`Student_USN`, `Subject_Subject_code`, `Test1`, `Test2`, `Test3`, `AS_SS`, `Internal_Lab`) VALUES ('1RV15CS162', '12CS5B5', '39.5', NULL, NULL, NULL, NULL);
INSERT INTO `attendance`.`marks` (`Student_USN`, `Subject_Subject_code`, `Test1`, `Test2`, `Test3`, `AS_SS`, `Internal_Lab`) VALUES ('1RV15CS162', '12HSI51', NULL, '27.5', NULL, NULL, NULL);
INSERT INTO `attendance`.`marks` (`Student_USN`, `Subject_Subject_code`, `Test1`, `Test2`, `Test3`, `AS_SS`, `Internal_Lab`) VALUES ('1RV15CS168', '12CS52', '31.5', '34.5', NULL, NULL, NULL);
INSERT INTO `attendance`.`marks` (`Student_USN`, `Subject_Subject_code`, `Test1`, `Test2`, `Test3`, `AS_SS`, `Internal_Lab`) VALUES ('1RV15CS168', '12CS53', NULL, '34', NULL, NULL, NULL);
INSERT INTO `attendance`.`marks` (`Student_USN`, `Subject_Subject_code`, `Test1`, `Test2`, `Test3`, `AS_SS`, `Internal_Lab`) VALUES ('1RV15CS168', '12CS54', NULL, '31', NULL, NULL, NULL);
INSERT INTO `attendance`.`marks` (`Student_USN`, `Subject_Subject_code`, `Test1`, `Test2`, `Test3`, `AS_SS`, `Internal_Lab`) VALUES ('1RV15CS168', '12CS5A4', '28.5', '33', NULL, NULL, NULL);
INSERT INTO `attendance`.`marks` (`Student_USN`, `Subject_Subject_code`, `Test1`, `Test2`, `Test3`, `AS_SS`, `Internal_Lab`) VALUES ('1RV15CS168', '12CS5B5', '36.5', NULL, NULL, NULL, NULL);
INSERT INTO `attendance`.`marks` (`Student_USN`, `Subject_Subject_code`, `Test1`, `Test2`, `Test3`, `AS_SS`, `Internal_Lab`) VALUES ('1RV15CS168', '12HSI51', NULL, '31', NULL, NULL, NULL);
