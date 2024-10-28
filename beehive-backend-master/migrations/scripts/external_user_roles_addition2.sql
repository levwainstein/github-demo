INSERT INTO tag(id, name) VALUES(26, 'project:aedp');
INSERT INTO project(id, name, repo_link, trello_link) VALUES(26, 'aedp', 'missing', 'missing');

INSERT INTO external_user_role(id, email, role, price_per_hour) VALUES (12, "kaiaschweig@gmail.com", 5, 35);

INSERT INTO diary_log(created, external_user_id, project, date, duration_hours, text) VALUES ('2024-05-14 13:05:30','12','aedp','2024-05-14',3,'Figma wireframe and document organization');