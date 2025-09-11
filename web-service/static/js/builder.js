// API Builder JavaScript

let modelCounter = 0;

/**
 * モデル追加
 */
function addModel() {
    modelCounter++;
    
    const template = document.getElementById('model-template');
    const clone = template.content.cloneNode(true);
    
    // モデル番号設定
    clone.querySelector('.model-number').textContent = modelCounter;
    
    // コンテナに追加
    const container = document.getElementById('models-container');
    container.appendChild(clone);
    
    // メッセージ非表示
    updateNoModelsMessage();
    
    // アニメーション追加
    const newModel = container.lastElementChild;
    newModel.classList.add('fade-in');
    
    // 最初のフィールドを自動追加
    addField(newModel.querySelector('.btn-outline-success'));
    
    // フォーカス設定
    newModel.querySelector('.model-name').focus();
}

/**
 * モデル削除
 */
function removeModel(button) {
    const modelItem = button.closest('.model-item');
    modelItem.remove();
    updateNoModelsMessage();
    updateModelsJson();
}

/**
 * フィールド追加
 */
function addField(button) {
    const template = document.getElementById('field-template');
    const clone = template.content.cloneNode(true);
    
    const modelItem = button.closest('.model-item');
    const fieldsContainer = modelItem.querySelector('.fields-container');
    
    fieldsContainer.appendChild(clone);
    
    // 新しいフィールドにフォーカス
    const newField = fieldsContainer.lastElementChild;
    newField.classList.add('fade-in');
    newField.querySelector('.field-name').focus();
    
    // イベントリスナー追加
    addFieldEventListeners(newField);
}

/**
 * フィールド削除
 */
function removeField(button) {
    const fieldItem = button.closest('.field-item');
    fieldItem.remove();
    updateModelsJson();
}

/**
 * フィールドイベントリスナー追加
 */
function addFieldEventListeners(fieldElement) {
    const inputs = fieldElement.querySelectorAll('input, select');
    inputs.forEach(input => {
        input.addEventListener('change', updateModelsJson);
        input.addEventListener('input', updateModelsJson);
    });
}

/**
 * モデルなしメッセージ表示/非表示
 */
function updateNoModelsMessage() {
    const container = document.getElementById('models-container');
    const message = document.getElementById('no-models-message');
    const hasModels = container.children.length > 0;
    
    message.style.display = hasModels ? 'none' : 'block';
}

/**
 * モデルデータをJSONに変換
 */
function updateModelsJson() {
    const models = [];
    const modelItems = document.querySelectorAll('.model-item');
    
    modelItems.forEach(modelItem => {
        const modelName = modelItem.querySelector('.model-name').value.trim();
        const modelDescription = modelItem.querySelector('.model-description').value.trim();
        
        if (!modelName) return; // 空のモデル名はスキップ
        
        const fields = [];
        const fieldItems = modelItem.querySelectorAll('.field-item');
        
        fieldItems.forEach(fieldItem => {
            const fieldName = fieldItem.querySelector('.field-name').value.trim();
            const fieldType = fieldItem.querySelector('.field-type').value;
            const fieldRequired = fieldItem.querySelector('.field-required').checked;
            const fieldDescription = fieldItem.querySelector('.field-description').value.trim();
            
            if (!fieldName) return; // 空のフィールド名はスキップ
            
            const field = {
                name: fieldName,
                type: fieldType,
                required: fieldRequired,
                description: fieldDescription,
                validations: getFieldValidations(fieldType)
            };
            
            fields.push(field);
        });
        
        if (fields.length > 0) {
            models.push({
                name: modelName,
                description: modelDescription,
                fields: fields
            });
        }
    });
    
    document.getElementById('models_json').value = JSON.stringify(models);
}

/**
 * フィールドタイプに応じたバリデーション取得
 */
function getFieldValidations(fieldType) {
    const validations = {};
    
    switch (fieldType) {
        case 'string':
        case 'text':
            validations.maxLength = 255;
            break;
        case 'email':
            validations.format = 'email';
            validations.maxLength = 255;
            break;
        case 'url':
            validations.format = 'uri';
            validations.maxLength = 2048;
            break;
        case 'integer':
            validations.minimum = -2147483648;
            validations.maximum = 2147483647;
            break;
        case 'number':
            break;
        case 'uuid':
            validations.pattern = '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$';
            break;
    }
    
    return validations;
}

/**
 * フォームバリデーション
 */
function validateForm() {
    let isValid = true;
    
    // API名バリデーション
    const apiNameInput = document.getElementById('api_name');
    const apiName = apiNameInput.value.trim();
    
    clearValidationError(apiNameInput);
    
    if (!apiName) {
        showValidationError(apiNameInput, 'API名は必須です');
        isValid = false;
    } else if (!validateApiName(apiName)) {
        showValidationError(apiNameInput, 'API名は英小文字とハイフンのみ使用可能です');
        isValid = false;
    }
    
    // モデル存在チェック
    const models = JSON.parse(document.getElementById('models_json').value || '[]');
    if (models.length === 0) {
        alert('少なくとも1つのモデルを定義してください');
        isValid = false;
    }
    
    // 各モデルのバリデーション
    models.forEach((model, modelIndex) => {
        if (!model.name) {
            alert(`モデル${modelIndex + 1}の名前が入力されていません`);
            isValid = false;
        }
        
        if (model.fields.length === 0) {
            alert(`モデル「${model.name}」にフィールドが定義されていません`);
            isValid = false;
        }
    });
    
    return isValid;
}

/**
 * フォーム送信処理
 */
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('apiForm');
    
    form.addEventListener('submit', function(e) {
        // フォーム送信前にJSONを更新
        updateModelsJson();
        
        // バリデーション実行
        if (!validateForm()) {
            e.preventDefault();
            return false;
        }
        
        // 送信ボタン無効化
        const submitButton = form.querySelector('button[type="submit"]');
        submitButton.disabled = true;
        submitButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>生成中...';
    });
    
    // API名入力時のリアルタイムバリデーション
    const apiNameInput = document.getElementById('api_name');
    apiNameInput.addEventListener('input', function() {
        clearValidationError(this);
        
        const value = this.value.trim();
        if (value && !validateApiName(value)) {
            showValidationError(this, 'API名は英小文字とハイフンのみ使用可能です');
        }
    });
    
    // 初期状態でメッセージ表示
    updateNoModelsMessage();
    
    // サンプルモデル追加（初回のみ）
    if (document.querySelectorAll('.model-item').length === 0) {
        addSampleModel();
    }
});

/**
 * サンプルモデル追加（初回表示用）
 */
function addSampleModel() {
    addModel();
    
    const modelItem = document.querySelector('.model-item');
    modelItem.querySelector('.model-name').value = 'User';
    modelItem.querySelector('.model-description').value = 'ユーザー情報';
    
    // サンプルフィールド追加
    const fieldsContainer = modelItem.querySelector('.fields-container');
    
    // IDフィールド
    const fieldItems = fieldsContainer.querySelectorAll('.field-item');
    if (fieldItems.length > 0) {
        const firstField = fieldItems[0];
        firstField.querySelector('.field-name').value = 'id';
        firstField.querySelector('.field-type').value = 'uuid';
        firstField.querySelector('.field-description').value = 'ユーザーID';
        addFieldEventListeners(firstField);
    }
    
    // 名前フィールド追加
    addField(modelItem.querySelector('.btn-outline-success'));
    const nameField = fieldsContainer.lastElementChild;
    nameField.querySelector('.field-name').value = 'name';
    nameField.querySelector('.field-type').value = 'string';
    nameField.querySelector('.field-description').value = 'ユーザー名';
    addFieldEventListeners(nameField);
    
    // メールフィールド追加
    addField(modelItem.querySelector('.btn-outline-success'));
    const emailField = fieldsContainer.lastElementChild;
    emailField.querySelector('.field-name').value = 'email';
    emailField.querySelector('.field-type').value = 'email';
    emailField.querySelector('.field-description').value = 'メールアドレス';
    addFieldEventListeners(emailField);
    
    updateModelsJson();
}