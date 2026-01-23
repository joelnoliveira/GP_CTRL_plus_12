-- Create database schema and seed data
-- This SQL file creates tables and populates them with initial data
-- SQLAlchemy will reflect these tables at runtime

CREATE SCHEMA IF NOT EXISTS langfuse;


CREATE TABLE users (
	id	 BIGSERIAL,
	email	 VARCHAR(512) NOT NULL,
	password	 VARCHAR(512) NOT NULL,
	role	 BOOL NOT NULL,
	created_at TIMESTAMP NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE runs_metrics (
	id			 BIGSERIAL,
	target_model		 TEXT NOT NULL,
	attack_model		 TEXT,
	visibility		 TEXT NOT NULL,
	role_play_option_id BIGINT,
	attack_type		 VARCHAR(255),
	status			 CHAR(255) NOT NULL,
	langfuse_trace_id	 TEXT,
	started_at		 TIMESTAMP NOT NULL,
	ended_at			 TIMESTAMP NOT NULL,
	metrics_asr		 FLOAT,
	metrics_orr		 FLOAT,
	metrics_aor		 FLOAT,
	metrics_veridict_majority BOOL,
	template_datasets_id	 BIGINT,
	scenarios_id		 BIGINT NOT NULL,
	users_id			 BIGINT NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE jury_votes (
	id		 BIGSERIAL,
	jury_index	 SMALLINT,
	usefulness	 BOOL NOT NULL,
	veridict	 BOOL,
	model_name	 TEXT NOT NULL,
	created_at	 TIMESTAMP NOT NULL,
	runs_metrics_id BIGINT NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE scenarios (
	id		 BIGSERIAL,
	name	 TEXT NOT NULL,
	description TEXT NOT NULL,
	is_builtin BOOL NOT NULL,
	storage_path TEXT NOT NULL,
	created_at	 TIMESTAMP NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE template_datasets (
	id		 BIGSERIAL,
	name	 TEXT NOT NULL,
	description	 TEXT NOT NULL,
	storage_path TEXT NOT NULL,
	is_builtin	 BOOL NOT NULL,
	created_at	 TIMESTAMP NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE role_play_options (
	id		 BIGSERIAL,
	name	 TEXT NOT NULL,
	description TEXT NOT NULL,
	is_builtin BOOL NOT NULL,
	storage_path TEXT NOT NULL,
	created_at	 TIMESTAMP NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE models (
	name BIGINT,
	PRIMARY KEY(name)
);

CREATE TABLE runs_metrics_models (
	runs_metrics_id BIGINT,
	models_name	 BIGINT,
	PRIMARY KEY(runs_metrics_id,models_name)
);

CREATE TABLE users_template_datasets (
	users_id		 BIGINT NOT NULL,
	template_datasets_id BIGINT,
	PRIMARY KEY(template_datasets_id)
);

CREATE TABLE scenarios_users (
	scenarios_id BIGINT,
	users_id	 BIGINT NOT NULL,
	PRIMARY KEY(scenarios_id)
);

CREATE TABLE api_key_configs (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    provider VARCHAR(50) DEFAULT 'OPEN_AI',
    model_name VARCHAR(100),
    api_key VARCHAR(500),
    user_id BIGINT NOT NULL
);

ALTER TABLE api_key_configs ADD CONSTRAINT api_key_configs_fk1 
    FOREIGN KEY (user_id) REFERENCES users(id);

ALTER TABLE runs_metrics ADD CONSTRAINT runs_metrics_fk1 FOREIGN KEY (template_datasets_id) REFERENCES template_datasets(id);
ALTER TABLE runs_metrics ADD CONSTRAINT runs_metrics_fk2 FOREIGN KEY (scenarios_id) REFERENCES scenarios(id);
ALTER TABLE runs_metrics ADD CONSTRAINT runs_metrics_fk3 FOREIGN KEY (users_id) REFERENCES users(id);
ALTER TABLE runs_metrics ADD CONSTRAINT runs_metrics_fk4 FOREIGN KEY (role_play_option_id) REFERENCES role_play_options(id);
ALTER TABLE jury_votes ADD UNIQUE (jury_index);
ALTER TABLE jury_votes ADD CONSTRAINT jury_votes_fk1 FOREIGN KEY (runs_metrics_id) REFERENCES runs_metrics(id);
ALTER TABLE runs_metrics_models ADD CONSTRAINT runs_metrics_models_fk1 FOREIGN KEY (runs_metrics_id) REFERENCES runs_metrics(id);
ALTER TABLE runs_metrics_models ADD CONSTRAINT runs_metrics_models_fk2 FOREIGN KEY (models_name) REFERENCES models(name);
ALTER TABLE users_template_datasets ADD CONSTRAINT users_template_datasets_fk1 FOREIGN KEY (users_id) REFERENCES users(id);
ALTER TABLE users_template_datasets ADD CONSTRAINT users_template_datasets_fk2 FOREIGN KEY (template_datasets_id) REFERENCES template_datasets(id);
ALTER TABLE scenarios_users ADD CONSTRAINT scenarios_users_fk1 FOREIGN KEY (scenarios_id) REFERENCES scenarios(id);
ALTER TABLE scenarios_users ADD CONSTRAINT scenarios_users_fk2 FOREIGN KEY (users_id) REFERENCES users(id);
-- ALTER TABLE users_api_key_configs ADD CONSTRAINT users_api_key_configs_fk1 FOREIGN KEY (users_id) REFERENCES users(id);
-- ALTER TABLE users_api_key_configs ADD CONSTRAINT users_api_key_configs_fk2 FOREIGN KEY (api_key_configs_id) REFERENCES api_key_configs(id);


-- ==================== SEED DATA: Scenarios ====================
-- Scenarios definem o TIPO de teste/ataque que pode ser feito
INSERT INTO scenarios (name, description, is_builtin, created_at, storage_path) VALUES
	('malicious_goals', 'Malicious Goals', TRUE, NOW(), '/backend/datasets/malicious_goals.json'),
	('vulnerable_goals', 'Vulnerable Goals', TRUE, NOW(), '/backend/datasets/vulnerable_goals.json'),
	('over_refusal_test', 'Over Refusal Test', TRUE, NOW(), '/backend/datasets/or-bench-hard-1k.yaml');


-- ==================== SEED DATA: Default Datasets ====================
-- Datasets são os ficheiros com prompts/objetivos usados nos testes
INSERT INTO template_datasets (name, description, storage_path, is_builtin, created_at) VALUES
    -- Datasets para Single Turn Attack (scenario_id = 1)
    -- ('Malicious Goals', 'Dataset com objetivos maliciosos para testes de segurança', '/backend/datasets/malicious_goals.json', 'application/json', TRUE, NOW(), 1),
    -- ('Malicious Goals (80 entries)', 'Versão reduzida do dataset de objetivos maliciosos com 80 entradas', '/backend/datasets/malicious_goals_80entries.json', 'application/json', TRUE, NOW(), 1),
    -- ('Vulnerable Goals', 'Dataset com objetivos vulneráveis baseados em CWE', '/backend/datasets/vulnerable_goals.json', 'application/json', TRUE, NOW(), 1),
    -- ('LLM Security Eval', 'Dataset para avaliação de segurança de LLMs', '/backend/datasets/llmseceval.json', 'application/json', TRUE, NOW(), 1),
    -- ('Cleaned LLM Security Eval', 'Versão limpa do dataset de avaliação de segurança de LLMs', '/backend/datasets/cleaned_llmseceval.json', 'application/json', TRUE, NOW(), 1),
    -- ('RMC Bench', 'RMC Benchmark dataset', '/backend/datasets/rmc_bench.json', 'application/json', TRUE, NOW(), 1),
    -- Datasets para Template Attack (scenario_id = 2)
    ('JailBreakV_28K', 'JailBreak V 28K', '/backend/datasets/JailBreakV_28K_clean.yaml', TRUE, NOW()),
    ('pliny_prompts_escaped', 'Pliny Prompts', '/backend/datasets/pliny_prompts_escaped.yaml', TRUE, NOW());
    -- Datasets para Over-Refusal Test (scenario_id = 3)
    -- ('OR-Bench Hard 1k', 'OR-Bench dataset com 1000 prompts legítimos que modelos frequentemente recusam', '/backend/datasets/or-bench-hard-1k.yaml', 'application/x-yaml', TRUE, NOW(), 3);

-- ==================== SEED DATA: Role Play Options ====================
INSERT INTO role_play_options (name, description, is_builtin, created_at, storage_path) VALUES
	('VIDEO_GAME', 'Video-game', TRUE, NOW(), '/backend/datasets/orchestrators/role_play/video_game.yaml'),
	('MR_ROBOT', 'Mr. Robot', TRUE, NOW(), '/backend/datasets/orchestrators/role_play/mr_robot.yaml');
INSERT INTO users (email, password, role, created_at) VALUES
    ('test@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.V.qHfiJA.yLz2e', FALSE, NOW());