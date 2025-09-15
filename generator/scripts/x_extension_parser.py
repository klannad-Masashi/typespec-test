#!/usr/bin/env python3
"""
OpenAPI x-拡張フィールドパーサー
TypeSpecカスタムデコレーターから生成されたx-拡張フィールドを解析し、
適切なバリデーションアノテーションやルールに変換する
"""

import logging
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ValidationTypeEnum(Enum):
    """バリデーションタイプ列挙型"""
    STRING = "string"
    NUMBER = "number"
    OBJECT = "object"
    ARRAY = "array"
    INSTANT = "instant"
    ENUM = "enum"


@dataclass
class ValidationRule:
    """バリデーションルール情報"""
    validation_type: ValidationTypeEnum
    pattern: Optional[str] = None
    value: Optional[str] = None
    required: bool = True
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    min_items: Optional[int] = None
    max_items: Optional[int] = None
    custom_validator: Optional[str] = None
    
    def __post_init__(self):
        """バリデーションルール初期化後処理"""
        if self.validation_type == ValidationTypeEnum.STRING and self.value:
            self.custom_validator = self._resolve_string_validator(self.value)
    
    def _resolve_string_validator(self, value: str) -> str:
        """文字列バリデーターパターンの解決"""
        validators = {
            "jisX0213withAlphaNumericSymbol": "JIS_X0213_WITH_ALPHANUMERIC_SYMBOL",
            "alphanumericPattern": "ALPHANUMERIC_PATTERN",
            "all": "ALL_STRING_VALIDATION"
        }
        return validators.get(value, f"CUSTOM_{value.upper()}")


@dataclass
class SpringBootAnnotation:
    """Spring Boot用バリデーションアノテーション"""
    annotation_name: str
    parameters: Dict[str, Any]
    import_statement: str
    
    def to_annotation_string(self) -> str:
        """アノテーション文字列生成（カスタムアノテーション形式対応）"""
        if not self.parameters:
            return f"@{self.annotation_name}"
        
        params = []
        for key, value in self.parameters.items():
            if isinstance(value, str):
                # Enum参照やType参照の場合は引用符を付けない
                if value.startswith(('UnitCheckString.Type.', 'UnitCheckNumber.Type.', 'UnitCheckArray.Type.')):
                    params.append(f'{key} = {value}')
                else:
                    params.append(f'{key} = "{value}"')
            elif isinstance(value, bool):
                params.append(f'{key} = {str(value).lower()}')
            else:
                params.append(f'{key} = {value}')
        
        # パラメーターが1つの場合は1行、複数の場合は複数行形式
        if len(params) == 1:
            return f"@{self.annotation_name}({params[0]})"
        elif len(params) > 1:
            # 複数行形式でルートファイルと同じスタイルにする
            param_lines = [f"            {param}" for param in params]
            param_str = ",\n".join(param_lines)
            return f"@{self.annotation_name}(\n{param_str}\n        )"
        else:
            return f"@{self.annotation_name}"


@dataclass
class AngularValidator:
    """Angular用バリデーター"""
    validator_name: str
    validator_function: str
    import_statement: str
    error_message: str


class XExtensionParser:
    """x-拡張フィールドパーサー"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def parse_property_extensions(self, property_schema: Dict[str, Any], field_name: str = None) -> List[ValidationRule]:
        """
        プロパティスキーマからx-拡張フィールドを解析してバリデーションルールを生成
        
        Args:
            property_schema: OpenAPIプロパティスキーマ
            field_name: フィールド名（required判定用）
            
        Returns:
            ValidationRuleのリスト
        """
        validation_rules = []
        
        # x-unitCheckString の処理
        if 'x-unitCheckString' in property_schema:
            rule = self._parse_string_validation(property_schema, field_name)
            if rule:
                validation_rules.append(rule)
        
        # x-unitCheckNumber の処理
        if 'x-unitCheckNumber' in property_schema:
            rule = self._parse_number_validation(property_schema, field_name)
            if rule:
                validation_rules.append(rule)
        
        # x-unitCheckObject の処理
        if 'x-unitCheckObject' in property_schema:
            rule = ValidationRule(
                validation_type=ValidationTypeEnum.OBJECT,
                required=True  # オブジェクトは基本的に必須
            )
            validation_rules.append(rule)
        
        # x-unitCheckArray の処理
        if 'x-unitCheckArray' in property_schema:
            rule = self._parse_array_validation(property_schema, field_name)
            if rule:
                validation_rules.append(rule)
        
        # x-unitCheckInstant の処理
        if 'x-unitCheckInstant' in property_schema:
            rule = ValidationRule(
                validation_type=ValidationTypeEnum.INSTANT,
                required=True  # 日時は基本的に必須
            )
            validation_rules.append(rule)
        
        # x-unitCheckEnum の処理
        if 'x-unitCheckEnum' in property_schema:
            rule = ValidationRule(
                validation_type=ValidationTypeEnum.ENUM,
                required=True  # Enumは基本的に必須
            )
            validation_rules.append(rule)
        
        return validation_rules
    
    def _parse_string_validation(self, property_schema: Dict[str, Any], field_name: str = None) -> Optional[ValidationRule]:
        """文字列バリデーションの解析"""
        x_unit_check = property_schema.get('x-unitCheckString')
        
        # 基本的な文字列バリデーション情報を取得
        # ルートファイルのrequired判定ロジック：nullableValueとnotEmptyはisRequired=false
        is_optional_field = field_name in ['nullableValue', 'notEmpty'] if field_name else False
        rule = ValidationRule(
            validation_type=ValidationTypeEnum.STRING,
            required=not is_optional_field
        )
        
        # パターン情報の取得
        if isinstance(x_unit_check, dict):
            rule.value = x_unit_check.get('value')
        elif isinstance(x_unit_check, str):
            rule.value = x_unit_check if x_unit_check != 'all' else None
        
        # OpenAPI標準のpatternがあれば取得
        if 'pattern' in property_schema:
            rule.pattern = property_schema['pattern']
        
        # 長さ制限の取得
        if 'maxLength' in property_schema:
            rule.max_length = property_schema['maxLength']
        if 'minLength' in property_schema:
            rule.min_length = property_schema['minLength']
        
        return rule
    
    def _parse_number_validation(self, property_schema: Dict[str, Any], field_name: str = None) -> Optional[ValidationRule]:
        """数値バリデーションの解析"""
        rule = ValidationRule(
            validation_type=ValidationTypeEnum.NUMBER,
            required=True  # 数値は基本的に必須
        )
        
        # 最小最大値の取得
        if 'minimum' in property_schema:
            rule.min_value = property_schema['minimum']
        if 'maximum' in property_schema:
            rule.max_value = property_schema['maximum']
        
        return rule
    
    def _parse_array_validation(self, property_schema: Dict[str, Any], field_name: str = None) -> Optional[ValidationRule]:
        """配列バリデーションの解析"""
        rule = ValidationRule(
            validation_type=ValidationTypeEnum.ARRAY,
            required=True  # 配列は基本的に必須
        )
        
        # 配列要素数制限の取得
        if 'minItems' in property_schema:
            rule.min_items = property_schema['minItems']
        if 'maxItems' in property_schema:
            rule.max_items = property_schema['maxItems']
        
        return rule
    
    def to_spring_boot_annotations(self, validation_rules: List[ValidationRule]) -> List[SpringBootAnnotation]:
        """バリデーションルールをSpring Bootアノテーションに変換"""
        annotations = []
        
        for rule in validation_rules:
            if rule.validation_type == ValidationTypeEnum.STRING:
                annotations.extend(self._create_string_annotations(rule))
            elif rule.validation_type == ValidationTypeEnum.NUMBER:
                annotations.extend(self._create_number_annotations(rule))
            elif rule.validation_type == ValidationTypeEnum.OBJECT:
                annotations.append(SpringBootAnnotation(
                    annotation_name="UnitCheckObject",
                    parameters={},
                    import_statement="// カスタムアノテーション（プロジェクト固有）"
                ))
            elif rule.validation_type == ValidationTypeEnum.ARRAY:
                annotations.extend(self._create_array_annotations(rule))
            elif rule.validation_type == ValidationTypeEnum.INSTANT:
                annotations.append(SpringBootAnnotation(
                    annotation_name="UnitCheckInstant",
                    parameters={},
                    import_statement="// カスタムアノテーション（プロジェクト固有）"
                ))
            elif rule.validation_type == ValidationTypeEnum.ENUM:
                annotations.append(SpringBootAnnotation(
                    annotation_name="UnitCheckEnum",
                    parameters={},
                    import_statement="// カスタムアノテーション（プロジェクト固有）"
                ))
        
        return annotations
    
    def _create_string_annotations(self, rule: ValidationRule) -> List[SpringBootAnnotation]:
        """文字列用アノテーション生成（カスタムアノテーション対応）"""
        annotations = []
        
        # UnitCheckStringカスタムアノテーションを生成
        params = {}
        
        # isRequired パラメーター
        if not rule.required:
            params['isRequired'] = False
        
        # pattern パラメーター
        if rule.value:
            params['pattern'] = f"UnitCheckString.Type.{rule.value}"
        else:
            params['pattern'] = "UnitCheckString.Type.all"
        
        # maxLength パラメーター
        if rule.max_length is not None:
            params['maxLength'] = rule.max_length
        
        # minLength パラメーター（UnitCheckStringにはminLengthがないようなので除外）
        
        annotations.append(SpringBootAnnotation(
            annotation_name="UnitCheckString",
            parameters=params,
            import_statement="// カスタムアノテーション（プロジェクト固有）"
        ))
        
        return annotations
    
    def _create_number_annotations(self, rule: ValidationRule) -> List[SpringBootAnnotation]:
        """数値用アノテーション生成（カスタムアノテーション対応）"""
        annotations = []
        
        # UnitCheckNumberカスタムアノテーションを生成
        params = {}
        
        # isRequired パラメーター（数値の場合、通常は必須）
        if not rule.required:
            params['isRequired'] = False
        
        # minLength/maxLength パラメーター（数値の場合は値の範囲）
        if rule.min_value is not None:
            params['minLength'] = rule.min_value
        
        if rule.max_value is not None:
            params['maxLength'] = rule.max_value
        
        annotations.append(SpringBootAnnotation(
            annotation_name="UnitCheckNumber",
            parameters=params,
            import_statement="// カスタムアノテーション（プロジェクト固有）"
        ))
        
        return annotations
    
    def _create_array_annotations(self, rule: ValidationRule) -> List[SpringBootAnnotation]:
        """配列用アノテーション生成（カスタムアノテーション対応）"""
        annotations = []
        
        # UnitCheckArrayカスタムアノテーションを生成
        params = {}
        
        # isRequired パラメーター
        if not rule.required:
            params['isRequired'] = False
        
        # minLength/maxLength パラメーター（配列の要素数制限）
        if rule.min_items is not None:
            params['minLength'] = rule.min_items
        
        if rule.max_items is not None:
            params['maxLength'] = rule.max_items
        
        annotations.append(SpringBootAnnotation(
            annotation_name="UnitCheckArray",
            parameters=params,
            import_statement="// カスタムアノテーション（プロジェクト固有）"
        ))
        
        return annotations
    
    def to_angular_validators(self, validation_rules: List[ValidationRule]) -> List[AngularValidator]:
        """バリデーションルールをAngularバリデーターに変換"""
        validators = []
        
        for rule in validation_rules:
            if rule.validation_type == ValidationTypeEnum.STRING:
                validators.extend(self._create_angular_string_validators(rule))
            elif rule.validation_type == ValidationTypeEnum.NUMBER:
                validators.extend(self._create_angular_number_validators(rule))
            elif rule.validation_type == ValidationTypeEnum.ARRAY:
                validators.extend(self._create_angular_array_validators(rule))
        
        return validators
    
    def _create_angular_string_validators(self, rule: ValidationRule) -> List[AngularValidator]:
        """Angular文字列バリデーター生成"""
        validators = []
        
        if rule.required:
            validators.append(AngularValidator(
                validator_name="required",
                validator_function="Validators.required",
                import_statement="import { Validators } from '@angular/forms';",
                error_message="この項目は必須です"
            ))
        
        if rule.min_length is not None:
            validators.append(AngularValidator(
                validator_name="minlength",
                validator_function=f"Validators.minLength({rule.min_length})",
                import_statement="import { Validators } from '@angular/forms';",
                error_message=f"最低{rule.min_length}文字入力してください"
            ))
        
        if rule.max_length is not None:
            validators.append(AngularValidator(
                validator_name="maxlength",
                validator_function=f"Validators.maxLength({rule.max_length})",
                import_statement="import { Validators } from '@angular/forms';",
                error_message=f"{rule.max_length}文字以内で入力してください"
            ))
        
        if rule.pattern:
            validators.append(AngularValidator(
                validator_name="pattern",
                validator_function=f"Validators.pattern(/{rule.pattern}/)",
                import_statement="import { Validators } from '@angular/forms';",
                error_message="入力形式が正しくありません"
            ))
        
        if rule.custom_validator:
            validator_name = rule.custom_validator.lower().replace('_', '')
            validators.append(AngularValidator(
                validator_name=validator_name,
                validator_function=f"CustomValidators.{validator_name}",
                import_statement="import { CustomValidators } from '../validators/custom-validators';",
                error_message=self._get_custom_error_message(rule.custom_validator)
            ))
        
        return validators
    
    def _create_angular_number_validators(self, rule: ValidationRule) -> List[AngularValidator]:
        """Angular数値バリデーター生成"""
        validators = []
        
        if rule.required:
            validators.append(AngularValidator(
                validator_name="required",
                validator_function="Validators.required",
                import_statement="import { Validators } from '@angular/forms';",
                error_message="この項目は必須です"
            ))
        
        if rule.min_value is not None:
            validators.append(AngularValidator(
                validator_name="min",
                validator_function=f"Validators.min({rule.min_value})",
                import_statement="import { Validators } from '@angular/forms';",
                error_message=f"{rule.min_value}以上の値を入力してください"
            ))
        
        if rule.max_value is not None:
            validators.append(AngularValidator(
                validator_name="max",
                validator_function=f"Validators.max({rule.max_value})",
                import_statement="import { Validators } from '@angular/forms';",
                error_message=f"{rule.max_value}以下の値を入力してください"
            ))
        
        return validators
    
    def _create_angular_array_validators(self, rule: ValidationRule) -> List[AngularValidator]:
        """Angular配列バリデーター生成"""
        validators = []
        
        if rule.required:
            validators.append(AngularValidator(
                validator_name="required",
                validator_function="Validators.required",
                import_statement="import { Validators } from '@angular/forms';",
                error_message="この項目は必須です"
            ))
        
        # 配列の長さチェックはカスタムバリデーターで実装
        if rule.min_items is not None or rule.max_items is not None:
            params = []
            if rule.min_items is not None:
                params.append(f"min: {rule.min_items}")
            if rule.max_items is not None:
                params.append(f"max: {rule.max_items}")
            
            param_str = "{" + ", ".join(params) + "}"
            validators.append(AngularValidator(
                validator_name="arraysize",
                validator_function=f"CustomValidators.arraySize({param_str})",
                import_statement="import { CustomValidators } from '../validators/custom-validators';",
                error_message=f"配列の要素数は{rule.min_items}以上{rule.max_items}以下にしてください"
            ))
        
        return validators
    
    def _get_custom_error_message(self, custom_validator: str) -> str:
        """カスタムバリデーターのエラーメッセージ取得"""
        error_messages = {
            "JIS_X0213_WITH_ALPHANUMERIC_SYMBOL": "JIS X 0213文字と英数記号のみ入力可能です",
            "ALPHANUMERIC_PATTERN": "英数字のみ入力してください",
            "ALL_STRING_VALIDATION": "文字列の形式が正しくありません"
        }
        return error_messages.get(custom_validator, "入力値が正しくありません")