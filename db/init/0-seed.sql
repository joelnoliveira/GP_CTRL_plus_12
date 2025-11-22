-- Create database schema and seed data
-- This SQL file creates tables and populates them with initial data
-- SQLAlchemy will reflect these tables at runtime

-- CREATE TABLE users (
-- 	id	 BIGSERIAL,
-- 	email	 VARCHAR(512) NOT NULL,
-- 	password	 VARCHAR(512) NOT NULL,
-- 	role	 BOOL NOT NULL,
-- 	created_at TIMESTAMP NOT NULL,
-- 	PRIMARY KEY(id)
-- );

-- CREATE TABLE runs_metrics (
-- 	id			 BIGSERIAL,
-- 	target_model		 TEXT NOT NULL,
-- 	attack_model		 TEXT NOT NULL,
-- 	visibility		 TEXT NOT NULL,
-- 	status			 CHAR(255) NOT NULL,
-- 	langfuse_trace_id	 TEXT NOT NULL,
-- 	started_at		 TIMESTAMP NOT NULL,
-- 	ended_at			 TIMESTAMP NOT NULL,
-- 	metrics_asr		 INTEGER,
-- 	metrics_orr		 INTEGER NOT NULL,
-- 	metrics_aor		 INTEGER NOT NULL,
-- 	metrics_useful_majority	 BOOL NOT NULL,
-- 	metrics_veridict_majority BOOL NOT NULL,
-- 	workload_datasets_id	 BIGINT NOT NULL,
-- 	attack_loads_id		 BIGINT NOT NULL,
-- 	scenarios_id		 BIGINT NOT NULL,
-- 	users_id			 BIGINT NOT NULL,
-- 	PRIMARY KEY(id)
-- );

-- CREATE TABLE jury_votes (
-- 	id		 BIGSERIAL,
-- 	jury_index	 SMALLINT,
-- 	usefulness	 BOOL NOT NULL,
-- 	veridict	 BOOL,
-- 	model_name	 TEXT NOT NULL,
-- 	created_at	 TIMESTAMP NOT NULL,
-- 	runs_metrics_id BIGINT NOT NULL,
-- 	PRIMARY KEY(id)
-- );

-- CREATE TABLE scenarios (
-- 	id		 BIGSERIAL,
-- 	name	 TEXT NOT NULL,
-- 	description TEXT NOT NULL,
-- 	created_at	 TIMESTAMP NOT NULL,
-- 	PRIMARY KEY(id)
-- );

-- CREATE TABLE workload_datasets (
-- 	id		 BIGSERIAL,
-- 	name	 TEXT NOT NULL,
-- 	description	 TEXT NOT NULL,
-- 	storage_path TEXT NOT NULL,
-- 	mime_path	 TEXT NOT NULL,
-- 	is_builtin	 BOOL NOT NULL,
-- 	created_at	 TIMESTAMP NOT NULL,
-- 	scenarios_id BIGINT NOT NULL,
-- 	PRIMARY KEY(id)
-- );

-- CREATE TABLE models (
-- 	name BIGINT,
-- 	PRIMARY KEY(name)
-- );

-- CREATE TABLE attack_loads (
-- 	id		 BIGSERIAL,
-- 	name	 TEXT NOT NULL,
-- 	description	 TEXT NOT NULL,
-- 	type	 TEXT NOT NULL,
-- 	storage_path TEXT NOT NULL,
-- 	is_builtin	 BOOL NOT NULL,
-- 	created_at	 TEXT NOT NULL,
-- 	PRIMARY KEY(id)
-- );

-- CREATE TABLE runs_metrics_models (
-- 	runs_metrics_id BIGINT,
-- 	models_name	 BIGINT,
-- 	PRIMARY KEY(runs_metrics_id,models_name)
-- );

-- CREATE TABLE users_attack_loads (
-- 	users_id	 BIGINT NOT NULL,
-- 	attack_loads_id BIGINT,
-- 	PRIMARY KEY(attack_loads_id)
-- );

-- CREATE TABLE users_workload_datasets (
-- 	users_id		 BIGINT NOT NULL,
-- 	workload_datasets_id BIGINT,
-- 	PRIMARY KEY(workload_datasets_id)
-- );

-- CREATE TABLE scenarios_users (
-- 	scenarios_id BIGINT,
-- 	users_id	 BIGINT NOT NULL,
-- 	PRIMARY KEY(scenarios_id)
-- );

-- ALTER TABLE runs_metrics ADD CONSTRAINT runs_metrics_fk1 FOREIGN KEY (workload_datasets_id) REFERENCES workload_datasets(id);
-- ALTER TABLE runs_metrics ADD CONSTRAINT runs_metrics_fk2 FOREIGN KEY (attack_loads_id) REFERENCES attack_loads(id);
-- ALTER TABLE runs_metrics ADD CONSTRAINT runs_metrics_fk3 FOREIGN KEY (scenarios_id) REFERENCES scenarios(id);
-- ALTER TABLE runs_metrics ADD CONSTRAINT runs_metrics_fk4 FOREIGN KEY (users_id) REFERENCES users(id);
-- ALTER TABLE jury_votes ADD UNIQUE (jury_index);
-- ALTER TABLE jury_votes ADD CONSTRAINT jury_votes_fk1 FOREIGN KEY (runs_metrics_id) REFERENCES runs_metrics(id);
-- ALTER TABLE workload_datasets ADD CONSTRAINT workload_datasets_fk1 FOREIGN KEY (scenarios_id) REFERENCES scenarios(id);
-- ALTER TABLE runs_metrics_models ADD CONSTRAINT runs_metrics_models_fk1 FOREIGN KEY (runs_metrics_id) REFERENCES runs_metrics(id);
-- ALTER TABLE runs_metrics_models ADD CONSTRAINT runs_metrics_models_fk2 FOREIGN KEY (models_name) REFERENCES models(name);
-- ALTER TABLE users_attack_loads ADD CONSTRAINT users_attack_loads_fk1 FOREIGN KEY (users_id) REFERENCES users(id);
-- ALTER TABLE users_attack_loads ADD CONSTRAINT users_attack_loads_fk2 FOREIGN KEY (attack_loads_id) REFERENCES attack_loads(id);
-- ALTER TABLE users_workload_datasets ADD CONSTRAINT users_workload_datasets_fk1 FOREIGN KEY (users_id) REFERENCES users(id);
-- ALTER TABLE users_workload_datasets ADD CONSTRAINT users_workload_datasets_fk2 FOREIGN KEY (workload_datasets_id) REFERENCES workload_datasets(id);
-- ALTER TABLE scenarios_users ADD CONSTRAINT scenarios_users_fk1 FOREIGN KEY (scenarios_id) REFERENCES scenarios(id);
-- ALTER TABLE scenarios_users ADD CONSTRAINT scenarios_users_fk2 FOREIGN KEY (users_id) REFERENCES users(id);

