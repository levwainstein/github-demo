DELETE FROM project_delegator;
DELETE FROM repository;
DELETE FROM project;

insert into project ( select tag.id as id, SUBSTRING(tag.name, 9, 100) as name, 'missing' as trello_link, 'missing' as repo_link, now(), NULL from tag where tag.name like 'project:%' );

INSERT INTO repository(id, name, url, project_id, created, updated) VALUES (1, "md-coach-dashboard", "https://github.com/beehive-software/md-coach-dashboard", 2, now(), NULL);
INSERT INTO repository(id, name, url, project_id, created, updated) VALUES (2, "md-app", "https://github.com/beehive-software/md-app", 2, now(), NULL);
INSERT INTO repository(id, name, url, project_id, created, updated) VALUES (3, "md-backend", "https://github.com/beehive-software/md-backend", 13, now(), NULL);
INSERT INTO repository(id, name, url, project_id, created, updated) VALUES (4, "bz-app", "https://github.com/beehive-software/bz-app", 8, now(), NULL);
INSERT INTO repository(id, name, url, project_id, created, updated) VALUES (5, "atomic", "https://github.com/beehive-software/atomic-tf", 4, now(), NULL);
INSERT INTO repository(id, name, url, project_id, created, updated) VALUES (6, "beehive-frontend", "https://github.com/beehive-software/beehive-frontend", 6, now(), NULL);
INSERT INTO repository(id, name, url, project_id, created, updated) VALUES (7, "beehive-dashboards", "https://github.com/beehive-software/beehive-dashboards", 6, now(), NULL);
INSERT INTO repository(id, name, url, project_id, created, updated) VALUES (8, "np-backend", "https://github.com/beehive-software/np-backend", 19, now(), NULL);

INSERT INTO project_delegator(id, user_id, project_id) VALUES (1, "waCmxkmo", 2);
INSERT INTO project_delegator(id, user_id, project_id) VALUES (2, "waCmxkmo", 13);
INSERT INTO project_delegator(id, user_id, project_id) VALUES (3, "waCmxkmo", 8);
INSERT INTO project_delegator(id, user_id, project_id) VALUES (4, "l4a17fC4", 4);
INSERT INTO project_delegator(id, user_id, project_id) VALUES (5, "yY76KnJZ", 6);
INSERT INTO project_delegator(id, user_id, project_id) VALUES (6, "EwEpKNvF", 19);
