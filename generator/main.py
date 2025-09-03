#!/usr/bin/env python3
"""
TypeSpec Generator メインスクリプト
TypeSpec定義からDDL、Spring Boot、Angularのコードを生成
"""

import sys
import os
import argparse
import logging
from pathlib import Path

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from generator.scripts.ddl_generator import DDLGenerator
from generator.scripts.spring_generator import SpringGenerator  
from generator.scripts.angular_generator import AngularGenerator

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(description='TypeSpec Generator')
    parser.add_argument(
        '--target', 
        choices=['all', 'ddl', 'spring', 'angular'],
        default='all',
        help='生成対象 (default: all)'
    )
    parser.add_argument(
        '--input',
        default='temp/openapi/openapi.yaml',
        help='OpenAPI仕様ファイルのパス (default: temp/openapi/openapi.yaml)'
    )
    parser.add_argument(
        '--config',
        default='config/generator_config.yaml', 
        help='設定ファイルのパス (default: config/generator_config.yaml)'
    )
    
    args = parser.parse_args()
    
    try:
        # OpenAPI仕様ファイルの存在チェック
        if not os.path.exists(args.input):
            logger.error(f"OpenAPI仕様ファイルが見つかりません: {args.input}")
            logger.info("先にTypeSpecコンパイルを実行してください: npm run typespec:compile")
            return 1
            
        # 各ジェネレータの実行
        if args.target in ['all', 'ddl']:
            logger.info("DDL生成を開始...")
            ddl_gen = DDLGenerator(args.input, args.config)
            ddl_gen.generate()
            logger.info("DDL生成完了")
            
        if args.target in ['all', 'spring']:
            logger.info("Spring Boot生成を開始...")
            spring_gen = SpringGenerator(args.input, args.config)
            spring_gen.generate()
            logger.info("Spring Boot生成完了")
            
        if args.target in ['all', 'angular']:
            logger.info("Angular生成を開始...")
            angular_gen = AngularGenerator(args.input, args.config)
            angular_gen.generate()
            logger.info("Angular生成完了")
            
        logger.info("全ての生成処理が完了しました")
        return 0
        
    except Exception as e:
        logger.error(f"生成処理でエラーが発生しました: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())