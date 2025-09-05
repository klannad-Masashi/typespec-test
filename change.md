# 1API = 1tspファイル移行時の変更予測

## 概要

現在の構造（1つの`main.tsp`）から将来の構造（1API = 1tspファイル）への移行時に必要な変更箇所の詳細分析。

## 現在の構造 vs 将来の構造

### 現在（1つのmain.tsp）
- **入力**: `typespec/tsp/main.tsp` (User管理APIのすべて)
- **OpenAPI出力**: `output/openapi/openapi.yaml` (1ファイル)
- **生成物**: 1つのサービスに対応するController、DTO、Angular サービス

### 将来（1API = 1tspファイル）
- **入力**: 複数の`*.tsp`ファイル（API別分離）
- **OpenAPI出力**: 複数の`*-api.yaml`ファイル
- **生成物**: API別に分離されたController、DTO、Angularサービス

## 主要な変更箇所

### 1. TypeSpec コンパイル処理 (typespecコンテナ)

**変更が必要な場所:**
- `typespec/package.json` の npm scripts
- `typespec/tspconfig.yaml` の設定
- Docker composeでの実行方法

**想定される入力構造:**
```
typespec/tsp/
├── user-api.tsp          # ユーザー管理API
├── product-api.tsp       # 商品管理API  
├── order-api.tsp         # 注文管理API
├── auth-api.tsp          # 認証API
└── common/               # 共通型定義
    ├── base-types.tsp
    └── error-responses.tsp
```

**コンパイル方式の変更:**
```bash
# 現在
npm run typespec:compile tsp/main.tsp

# 変更後（想定）
npm run typespec:compile tsp/user-api.tsp --output user-api.yaml
npm run typespec:compile tsp/product-api.tsp --output product-api.yaml
# または一括処理
npm run typespec:compile-all
```

**想定されるOpenAPI出力:**
```
output/openapi/
├── user-api.yaml        # ユーザー管理API仕様
├── product-api.yaml     # 商品管理API仕様
├── order-api.yaml       # 注文管理API仕様
└── auth-api.yaml        # 認証API仕様
```

### 2. ジェネレーター main.py

**ファイル**: `generator/main.py`

**現在の引数:**
```python
--input output/openapi/openapi.yaml
```

**変更後の引数（想定）:**
```python
# パターン1: ディレクトリ指定
--input output/openapi/

# パターン2: 複数ファイル指定
--input user-api.yaml,product-api.yaml,order-api.yaml

# パターン3: 設定ファイルベース
--config config/multi-api-config.yaml
```

**必要な変更:**
- 複数入力ファイルの処理ループ
- API別出力ディレクトリの管理
- 引数解析の拡張

### 3. 各ジェネレータークラス

#### A. CSV Generator (`generator/scripts/csv_generator.py`)

**主な変更箇所:**
- `__init__(openapi_path, config_path)`: 複数OpenAPIファイル受け入れ
- `load_openapi_spec()`: 複数仕様ファイル読み込み
- `extract_table_info()`: API別テーブル情報マージ処理

**想定される処理フロー:**
```python
def load_multiple_openapi_specs(self, openapi_dir):
    specs = {}
    for yaml_file in glob.glob(f"{openapi_dir}/*.yaml"):
        api_name = Path(yaml_file).stem.replace('-api', '')
        specs[api_name] = self.load_single_spec(yaml_file)
    return specs

def merge_table_definitions(self, specs):
    # 複数APIからのテーブル定義をマージ
    # 重複チェックと関連性管理
```

#### B. DDL Generator (`generator/scripts/ddl_generator.py`)

**影響度**: 中程度

**主な変更:**
- CSV入力が複数API分になるため、テーブル定義の統合処理
- テーブル間の外部キー関係の管理
- API別DDL生成 vs 統合DDL生成の選択

**想定される出力構造:**
```
output/ddl/
├── users.sql           # UserAPIから生成
├── products.sql        # ProductAPIから生成
├── orders.sql          # OrderAPIから生成
└── master-schema.sql   # 全テーブル統合版
```

#### C. Spring Generator (`generator/scripts/spring_generator.py`)

**影響度**: 🔴 高（大幅変更が必要）

**現在の出力構造:**
```
output/backend/main/java/com/example/userapi/
├── controller/UserController.java
└── dto/*.java
```

**変更後の出力構造:**
```
output/backend/main/java/com/example/
├── userapi/
│   ├── controller/UserController.java
│   └── dto/*.java
├── productapi/
│   ├── controller/ProductController.java  
│   └── dto/*.java
└── orderapi/
    ├── controller/OrderController.java
    └── dto/*.java
```

**必要な変更:**
```python
# パッケージ名の動的生成
def get_package_name(self, api_name, config):
    base = config.get('apis', {}).get(api_name, {}).get('base_package')
    return base or f"com.example.{api_name}api"

# 複数OpenAPI仕様からの並列生成
def generate_from_multiple_specs(self, specs, config):
    for api_name, spec in specs.items():
        output_dir = self.get_api_output_dir(api_name)
        self.generate_single_api(spec, output_dir, api_name)
```

#### D. Angular Generator (`generator/scripts/angular_generator.py`)

**影響度**: 🔴 高（大幅変更が必要）

**現在の出力構造:**
```
app/
├── models/*.model.ts
└── services/*.service.ts
```

**変更後の出力構造:**
```
app/
├── user/               # ユーザー関連
│   ├── models/
│   │   ├── user.model.ts
│   │   └── create-user-request.model.ts
│   └── services/
│       └── user.service.ts
├── product/           # 商品関連
│   ├── models/
│   │   ├── product.model.ts
│   │   └── create-product-request.model.ts
│   └── services/
│       └── product.service.ts
└── order/            # 注文関連
    ├── models/
    └── services/
```

**必要な変更:**
```python
# モジュール別ディレクトリ作成
def create_module_directories(self, api_name):
    module_dir = self.output_dir / api_name
    (module_dir / "models").mkdir(parents=True, exist_ok=True)
    (module_dir / "services").mkdir(parents=True, exist_ok=True)

# Angular モジュール別インポート管理
def generate_module_imports(self, api_name, models):
    # API間の型参照とインポート文の管理
```

### 4. 設定ファイル (`config/generator_config.yaml`)

**影響度**: 🔴 高

**現在の設定:**
```yaml
spring:
  base_package: com.example.userapi

angular:
  api_base_url: http://localhost:8080/api
```

**変更後の設定（想定）:**
```yaml
# グローバル設定
global:
  output_base: output/
  
# API別設定
apis:
  user:
    input_file: user-api.yaml
    spring:
      base_package: com.example.userapi
    angular:
      module_name: user
      api_base_url: http://localhost:8080/api/user
    
  product:
    input_file: product-api.yaml
    spring:
      base_package: com.example.productapi
    angular:
      module_name: product
      api_base_url: http://localhost:8080/api/product
      
  order:
    input_file: order-api.yaml
    spring:
      base_package: com.example.orderapi
    angular:
      module_name: order
      api_base_url: http://localhost:8080/api/order

# 依存関係管理
dependencies:
  # API間の依存関係定義
  - from: order
    to: [user, product]
    type: reference
```

### 5. テンプレートファイル

**影響度**: 🟡 中程度

**変更の可能性:**
- `generator/templates/spring/controller.java.j2`: パッケージ名の動的設定
- `generator/templates/angular/interface.ts.j2`: モジュール構造対応

**Spring Boot テンプレート変更例:**
```java
// 現在
package {{ config.spring.base_package }}.{{ config.spring.controller_package }};

// 変更後
package {{ api_config.spring.base_package }}.{{ api_config.spring.controller_package }};
```

### 6. Docker Compose & TypeSpec実行

**影響度**: 🟡 中程度

**変更箇所:** 
- `typespec/tspconfig.yaml`
- `typespec/package.json` の npm scripts
- docker-compose.ymlでの実行方式

**TypeSpec設定変更（想定）:**
```yaml
# 複数ファイル対応の設定
emit:
  - "@typespec/openapi3"

options:
  "@typespec/openapi3":
    emitter-output-dir: "{output-dir}"
    file-type: yaml
    
# 新設：マルチファイル設定
multi-compile:
  enabled: true
  input-pattern: "tsp/*-api.tsp"
  output-pattern: "{basename}.yaml"
```

## 変更の優先度

### 🔴 高優先度（必須変更）
1. **main.py**: 複数入力ファイル対応
2. **spring_generator.py**: パッケージ別出力
3. **angular_generator.py**: モジュール別出力
4. **設定ファイル**: 複数API管理

### 🟡 中優先度（重要だが段階的対応可）
1. **csv_generator.py**: 複数API統合
2. **ddl_generator.py**: 関連テーブル管理
3. **TypeSpec実行方式**: バッチ処理対応

### 🟢 低優先度（既存互換性維持可能）
1. **テンプレートファイル**: 小規模修正
2. **Docker設定**: 実行方式の調整

## 推奨実装順序

### Phase 1: 基盤対応
1. **main.pyで複数ファイル入力対応**
   - 引数解析の拡張
   - 複数OpenAPIファイル処理ループ
   - エラーハンドリング強化

2. **設定ファイル拡張**
   - 複数API設定構造の定義
   - 既存設定との互換性維持

### Phase 2: 生成器コア変更
1. **Spring Boot生成器の出力構造変更**
   - API別パッケージ生成
   - DTO間の依存関係管理
   - Controller分離

2. **Angular生成器のモジュール別出力**
   - API別ディレクトリ構造
   - モジュール間インポート管理
   - サービス分離

### Phase 3: 統合処理
1. **CSV/DDL生成器の統合処理**
   - 複数APIからのテーブル定義統合
   - 関連テーブル管理
   - 外部キー自動生成

2. **依存関係管理システム**
   - API間の型参照
   - 循環依存検出
   - インポート最適化

### Phase 4: 最適化
1. **TypeSpecコンパイル処理の最適化**
   - 並列コンパイル
   - 増分コンパイル
   - 共通型の効率的管理

2. **生成パフォーマンス向上**
   - キャッシュ機能
   - 増分生成
   - バリデーション強化

## 技術的課題

### 1. 型の共有と依存関係
- 複数API間でのDTO共有
- 循環参照の回避
- インポート文の自動生成

### 2. データベース設計
- API別テーブル vs 統合テーブル
- 外部キー制約の管理
- マイグレーション戦略

### 3. バージョニング
- API別バージョン管理
- 互換性維持
- 段階的マイグレーション

## 互換性維持戦略

1. **段階的移行**
   - 既存の単一API方式を保持
   - マルチAPI方式をオプションとして追加
   - 設定による動作切り替え

2. **設定ファイルの互換性**
   - 既存設定形式のサポート継続
   - 新旧設定の自動変換

3. **出力構造の選択制**
   - レガシー出力構造の維持オプション
   - 新構造への段階的移行パス

## 見積もり工数

- **Phase 1**: 2-3週間
- **Phase 2**: 4-6週間
- **Phase 3**: 2-3週間  
- **Phase 4**: 2-4週間

**総計**: 10-16週間（段階的リリース前提）

## リスクと対策

### 高リスク
1. **Spring Boot生成の複雑化** → 段階的実装とテスト強化
2. **Angular構造の大幅変更** → 既存プロジェクトへの影響分析

### 中リスク
1. **TypeSpec依存関係管理** → 共通型ライブラリの設計
2. **データベース統合** → マイグレーション計画の策定

### 対策
- プロトタイプによる事前検証
- 既存プロジェクトでの動作確認
- ロールバック計画の策定