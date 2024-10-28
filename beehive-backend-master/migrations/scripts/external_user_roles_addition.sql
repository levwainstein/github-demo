INSERT INTO project(id, name, repo_link, trello_link) VALUES(19, 'nicklas', 'missing', 'missing');

INSERT INTO external_user_role(id, email, role, price_per_hour) VALUES (10, "usmanbashir.mirza@gmail.com", 2, 35);
INSERT INTO external_user_role(id, email, role, price_per_hour) VALUES (11, "hassamhassan.qc@gmail.com", 2, 30);

INSERT INTO diary_log(id, created, external_user_id, project, date, duration_hours, text) VALUES (396,'2024-04-01 07:04:19','10','atomic','2024-04-01',6,'Initiate task AGK-741 for adding sponsored and organic metrics in profit dropdown on store page and split it into two segments for backend, one for the store page and other for advance report page. Initially, focus on store page task after that i will create other related tasks.\nReview child task for AGK-740 make backend final and create task for frontend modifications\nRegarding AGK-738, I am currently executing  historical payment report for Garnetics store.');
INSERT INTO diary_log(id, created, external_user_id, project, date, duration_hours, text) VALUES (395,'2024-04-01 15:52:14','11','nicklas','2024-04-01',4.5,'Onboarding, meeting and documentation reading  ');