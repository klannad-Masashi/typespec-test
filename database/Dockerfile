# PostgreSQL データベース環境
FROM postgres:15-alpine

# カスタム初期化スクリプト用のディレクトリ
COPY ddl/*.sql /docker-entrypoint-initdb.d/

# 環境変数の設定（デフォルト値）
ENV POSTGRES_DB=userdb
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=password

# PostgreSQLのデフォルトポート
EXPOSE 5432