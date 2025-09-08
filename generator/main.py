#!/usr/bin/env python3
"""
TypeSpec Generator メインスクリプト
TypeSpec定義からDDL、Spring Boot、Angularのコードを生成

Python 3.12.3対応版 - マルチAPI対応
"""

import sys
import os
import argparse
import logging
import glob
import yaml
from pathlib import Path

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from generator.scripts.csv_generator import CSVGenerator
from generator.scripts.ddl_generator import DDLGenerator
from generator.scripts.spring_generator import SpringGenerator  
from generator.scripts.angular_generator import AngularGenerator
from generator.scripts.java_enum_generator import JavaEnumGenerator

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def discover_openapi_files(input_path):
    """
    OpenAPI仕様ファイルを検出する
    
    Args:
        input_path: 入力パス（ディレクトリまたはファイル）
        
    Returns:
        dict: {api_name: file_path} の辞書
    """
    openapi_files = {}
    input_path = Path(input_path)
    
    if input_path.is_file():
        # 単一ファイルの場合
        api_name = input_path.stem.replace('-api', '')
        if api_name == 'openapi':  # レガシー単一ファイル
            api_name = 'main'
        openapi_files[api_name] = str(input_path)
        logger.info(f"単一ファイルを検出: {api_name} -> {input_path}")
    elif input_path.is_dir():
        # ディレクトリの場合、*.yamlファイルを検索
        yaml_files = list(input_path.glob("*.yaml")) + list(input_path.glob("*.yml"))
        for yaml_file in yaml_files:
            api_name = yaml_file.stem.replace('-api', '')
            openapi_files[api_name] = str(yaml_file)
            logger.info(f"APIファイルを検出: {api_name} -> {yaml_file}")
    else:
        logger.error(f"入力パスが見つかりません: {input_path}")
        
    return openapi_files


def load_multi_api_config(config_path):
    """
    マルチAPI設定を読み込む
    
    Args:
        config_path: 設定ファイルパス
        
    Returns:
        dict: 設定データ
    """
    if not Path(config_path).exists():
        logger.warning(f"設定ファイルが見つかりません: {config_path}")
        return {}
        
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
        
    return config


def main():
    """メイン処理 - マルチAPI対応"""
    parser = argparse.ArgumentParser(description='TypeSpec Generator - マルチAPI対応版')
    parser.add_argument(
        '--target', 
        choices=['all', 'csv', 'ddl', 'spring', 'angular', 'java-enum'],
        default='all',
        help='生成対象 (default: all)'
    )
    parser.add_argument(
        '--input',
        default='output/openapi',
        help='OpenAPI仕様ファイル/ディレクトリのパス (default: output/openapi)'
    )
    parser.add_argument(
        '--config',
        default='config/generator_config.yaml', 
        help='設定ファイルのパス (default: config/generator_config.yaml)'
    )
    parser.add_argument(
        '--legacy-mode',
        action='store_true',
        help='レガシー単一ファイルモード (openapi.yaml)'
    )
    
    args = parser.parse_args()
    
    try:
        # レガシーモードの場合は従来の単一ファイルパスを使用
        if args.legacy_mode:
            args.input = 'output/openapi/openapi.yaml'
            
        # OpenAPI仕様ファイルを検出
        openapi_files = discover_openapi_files(args.input)
        if not openapi_files:
            logger.error(f"OpenAPI仕様ファイルが見つかりません: {args.input}")
            logger.info("先にTypeSpecコンパイルを実行してください:")
            logger.info("  マルチAPI: npm run typespec:compile-separate")
            logger.info("  単一API: npm run typespec:compile")
            return 1
            
        # 設定ファイルを読み込み
        config = load_multi_api_config(args.config)
        
        logger.info(f"検出されたAPI: {list(openapi_files.keys())}")
        
        # 各ジェネレータの実行
        if args.target in ['all', 'csv']:
            logger.info("CSV生成を開始...")
            csv_gen = CSVGenerator(openapi_files, args.config)
            csv_gen.generate()
            logger.info("CSV生成完了")
            
        if args.target in ['all', 'ddl']:
            logger.info("DDL生成を開始...")
            ddl_gen = DDLGenerator(config_path=args.config)
            ddl_gen.generate()
            logger.info("DDL生成完了")
            
        if args.target in ['all', 'spring']:
            logger.info("Spring Boot生成を開始...")
            spring_gen = SpringGenerator(openapi_files, args.config)
            spring_gen.generate()
            logger.info("Spring Boot生成完了")
            
        if args.target in ['all', 'angular']:
            logger.info("Angular生成を開始...")
            angular_gen = AngularGenerator(openapi_files, args.config)
            angular_gen.generate()
            logger.info("Angular生成完了")
            
        if args.target in ['all', 'java-enum']:
            logger.info("Java Enum生成を開始...")
            java_enum_gen = JavaEnumGenerator(openapi_files, args.config)
            java_enum_gen.generate()
            logger.info("Java Enum生成完了")
            
        logger.info("全ての生成処理が完了しました")
        return 0
        
    except Exception as e:
        logger.error(f"生成処理でエラーが発生しました: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())