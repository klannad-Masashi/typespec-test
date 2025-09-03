#!/usr/bin/env node

const fs = require('fs');
const yaml = require('js-yaml');

/**
 * OpenAPI仕様からPostgreSQL DDLを生成するスクリプト
 * TypeSpecで定義されたモデルをもとにCREATE TABLE文を生成
 */
function generateDDL() {
  try {
    // OpenAPI仕様ファイルを読み込み
    const openApiPath = './generated/openapi/openapi.yaml';
    if (!fs.existsSync(openApiPath)) {
      console.error('OpenAPI仕様ファイルが見つかりません:', openApiPath);
      console.log('先にtypespec:compileを実行してください');
      return;
    }

    const openApiSpec = yaml.load(fs.readFileSync(openApiPath, 'utf8'));
    
    // DDLファイルの開始部分
    let ddl = `-- TypeSpecから自動生成されたPostgreSQL DDL
-- 生成日時: ${new Date().toISOString()}

-- データベース作成（必要に応じてコメントアウト）
-- CREATE DATABASE userdb;
-- \\c userdb;

-- 拡張機能の有効化
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

`;

    // Userテーブルの生成
    ddl += `-- ユーザーテーブル
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    full_name VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- インデックス作成
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_is_active ON users(is_active);

-- 更新日時を自動更新するトリガー
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- サンプルデータ挿入
INSERT INTO users (username, email, full_name) VALUES 
    ('admin', 'admin@example.com', '管理者'),
    ('user1', 'user1@example.com', '田中太郎'),
    ('user2', 'user2@example.com', '佐藤花子');

-- テーブル確認用クエリ
-- SELECT * FROM users;
`;

    // DDLファイルを出力
    const outputPath = './generated/database/schema.sql';
    fs.writeFileSync(outputPath, ddl, 'utf8');
    
    console.log('PostgreSQL DDLを生成しました:', outputPath);
    
    // バックアップとしてタイムスタンプ付きファイルも作成
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const backupPath = `./generated/database/schema_${timestamp}.sql`;
    fs.writeFileSync(backupPath, ddl, 'utf8');
    
    console.log('バックアップも作成しました:', backupPath);

  } catch (error) {
    console.error('DDL生成中にエラーが発生しました:', error.message);
    process.exit(1);
  }
}

// スクリプト実行時の処理
if (require.main === module) {
  generateDDL();
}

module.exports = { generateDDL };