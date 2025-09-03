-- TypeSpecから自動生成されたPostgreSQL DDL
-- 生成日時: 2025-09-03T01:10:28.082626

-- データベース作成（必要に応じてコメントアウト）
-- CREATE DATABASE userdb;
-- \c userdb;

-- 拡張機能の有効化
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- createuserrequestsテーブル
CREATE TABLE createuserrequests (
    username VARCHAR(50) UNIQUE,    email VARCHAR(255) UNIQUE,    fullName VARCHAR(100),    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP);

-- createuserrequestsテーブルのインデックス作成
CREATE INDEX idx_createuserrequests_username ON createuserrequests(username);
CREATE INDEX idx_createuserrequests_email ON createuserrequests(email);

-- deleteresponsesテーブル
CREATE TABLE deleteresponses (
    message VARCHAR(255),    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP);

-- deleteresponsesテーブルのインデックス作成

-- errorresponsesテーブル
CREATE TABLE errorresponses (
    code VARCHAR(255),    message VARCHAR(255),    details VARCHAR(255),    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP);

-- errorresponsesテーブルのインデックス作成

-- updateuserrequestsテーブル
CREATE TABLE updateuserrequests (
    username VARCHAR(50) UNIQUE,    email VARCHAR(255) UNIQUE,    fullName VARCHAR(100),    isActive BOOLEAN,    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP);

-- updateuserrequestsテーブルのインデックス作成
CREATE INDEX idx_updateuserrequests_username ON updateuserrequests(username);
CREATE INDEX idx_updateuserrequests_email ON updateuserrequests(email);

-- usersテーブル
CREATE TABLE users (
    id SERIAL PRIMARY KEY NOT NULL,    username VARCHAR(50) UNIQUE,    email VARCHAR(255) UNIQUE,    fullName VARCHAR(100),    createdAt TIMESTAMP WITH TIME ZONE,    updatedAt TIMESTAMP WITH TIME ZONE,    isActive BOOLEAN DEFAULT True,    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP);

-- usersテーブルのインデックス作成
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);

-- usercreateresponsesテーブル
CREATE TABLE usercreateresponses (
    user VARCHAR(255),    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP);

-- usercreateresponsesテーブルのインデックス作成

-- userlistresponsesテーブル
CREATE TABLE userlistresponses (
    users JSONB,    total INTEGER,    page INTEGER,    limit INTEGER,    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP);

-- userlistresponsesテーブルのインデックス作成


-- 更新日時を自動更新するトリガー関数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- createuserrequestsテーブルの更新日時トリガー
CREATE TRIGGER update_createuserrequests_updated_at 
    BEFORE UPDATE ON createuserrequests 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- deleteresponsesテーブルの更新日時トリガー
CREATE TRIGGER update_deleteresponses_updated_at 
    BEFORE UPDATE ON deleteresponses 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- errorresponsesテーブルの更新日時トリガー
CREATE TRIGGER update_errorresponses_updated_at 
    BEFORE UPDATE ON errorresponses 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- updateuserrequestsテーブルの更新日時トリガー
CREATE TRIGGER update_updateuserrequests_updated_at 
    BEFORE UPDATE ON updateuserrequests 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- usersテーブルの更新日時トリガー
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- usercreateresponsesテーブルの更新日時トリガー
CREATE TRIGGER update_usercreateresponses_updated_at 
    BEFORE UPDATE ON usercreateresponses 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- userlistresponsesテーブルの更新日時トリガー
CREATE TRIGGER update_userlistresponses_updated_at 
    BEFORE UPDATE ON userlistresponses 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();


-- サンプルデータ挿入
INSERT INTO users (username, email, full_name) VALUES 
    ('admin', 'admin@example.com', '管理者'),
    ('user1', 'user1@example.com', '田中太郎'),
    ('user2', 'user2@example.com', '佐藤花子');

-- テーブル確認用クエリ
-- SELECT * FROM createuserrequests;
-- SELECT * FROM deleteresponses;
-- SELECT * FROM errorresponses;
-- SELECT * FROM updateuserrequests;
-- SELECT * FROM users;
-- SELECT * FROM usercreateresponses;
-- SELECT * FROM userlistresponses;
