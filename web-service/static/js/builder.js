// API Builder JavaScript
console.log('builder.js loaded');

let modelCounter = 0;
let endpointCounter = 0;

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
    
    // フィールドタイプ選択時のイベントリスナー追加
    const typeSelect = fieldElement.querySelector('.field-type');
    if (typeSelect) {
        typeSelect.addEventListener('change', function() {
            toggleFieldConstraints(fieldElement);
        });
        // 初期状態でも制約表示チェック
        toggleFieldConstraints(fieldElement);
    }
}

/**
 * フィールド制約入力欄の表示・非表示切り替え
 */
function toggleFieldConstraints(fieldElement) {
    const typeSelect = fieldElement.querySelector('.field-type');
    const constraintsDiv = fieldElement.querySelector('.field-constraints');
    
    if (typeSelect && constraintsDiv) {
        const fieldType = typeSelect.value;
        const isNumeric = fieldType === 'integer' || fieldType === 'number';
        const isString = fieldType === 'string' || fieldType === 'text' || fieldType === 'email' || fieldType === 'url';
        
        const minLabel = constraintsDiv.querySelector('.constraint-min-label');
        const maxLabel = constraintsDiv.querySelector('.constraint-max-label');
        const minInput = constraintsDiv.querySelector('.field-min-value');
        const maxInput = constraintsDiv.querySelector('.field-max-value');
        
        if (isNumeric || isString) {
            constraintsDiv.style.display = 'block';
            
            // ラベルとプレースホルダーを型に応じて変更
            if (isNumeric) {
                minLabel.textContent = '最小値';
                maxLabel.textContent = '最大値';
                minInput.placeholder = '最小値';
                maxInput.placeholder = '最大値';
            } else if (isString) {
                minLabel.textContent = '最小文字数';
                maxLabel.textContent = '最大文字数';
                minInput.placeholder = '最小文字数';
                maxInput.placeholder = '最大文字数';
            }
        } else {
            constraintsDiv.style.display = 'none';
            // その他の型の場合は値をクリア
            if (minInput) minInput.value = '';
            if (maxInput) maxInput.value = '';
        }
    }
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
            const fieldMinValue = fieldItem.querySelector('.field-min-value')?.value;
            const fieldMaxValue = fieldItem.querySelector('.field-max-value')?.value;
            
            if (!fieldName) return; // 空のフィールド名はスキップ
            
            const field = {
                name: fieldName,
                type: fieldType,
                required: fieldRequired,
                description: fieldDescription,
                validations: getFieldValidations(fieldType, fieldMinValue, fieldMaxValue)
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
function getFieldValidations(fieldType, minValue = null, maxValue = null) {
    const validations = {};
    
    switch (fieldType) {
        case 'string':
        case 'text':
            // ユーザー入力値があれば使用、なければデフォルト値
            if (minValue !== null && minValue !== '') {
                validations.minLength = parseInt(minValue);
            }
            if (maxValue !== null && maxValue !== '') {
                validations.maxLength = parseInt(maxValue);
            } else {
                validations.maxLength = 255; // デフォルト値
            }
            break;
        case 'email':
            validations.format = 'email';
            // ユーザー入力値があれば使用、なければデフォルト値
            if (minValue !== null && minValue !== '') {
                validations.minLength = parseInt(minValue);
            }
            if (maxValue !== null && maxValue !== '') {
                validations.maxLength = parseInt(maxValue);
            } else {
                validations.maxLength = 255; // デフォルト値
            }
            break;
        case 'url':
            validations.format = 'uri';
            // ユーザー入力値があれば使用、なければデフォルト値
            if (minValue !== null && minValue !== '') {
                validations.minLength = parseInt(minValue);
            }
            if (maxValue !== null && maxValue !== '') {
                validations.maxLength = parseInt(maxValue);
            } else {
                validations.maxLength = 2048; // デフォルト値
            }
            break;
        case 'integer':
            // ユーザー入力値があれば使用、なければデフォルト値
            if (minValue !== null && minValue !== '') {
                validations.minimum = parseInt(minValue);
            } else {
                validations.minimum = -2147483648;
            }
            if (maxValue !== null && maxValue !== '') {
                validations.maximum = parseInt(maxValue);
            } else {
                validations.maximum = 2147483647;
            }
            break;
        case 'number':
            // ユーザー入力値があれば設定
            if (minValue !== null && minValue !== '') {
                validations.minimum = parseFloat(minValue);
            }
            if (maxValue !== null && maxValue !== '') {
                validations.maximum = parseFloat(maxValue);
            }
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
        updateEndpointsJson();
        
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
            hideApiRouteDisplay();
        } else {
            updateApiRouteDisplay(value);
            updateEndpointBasePaths(value);
        }
        
        // 空の場合もベースパス更新
        if (!value) {
            updateEndpointBasePaths('');
        }
    });
    
    // 初期状態でメッセージ表示
    updateNoModelsMessage();
    updateNoEndpointsMessage();
    
    // サンプルモデル追加（初回のみ）
    if (document.querySelectorAll('.model-item').length === 0) {
        addSampleModel();
    }
    
    // ページトップにスクロール
    window.scrollTo(0, 0);
    
    // 初期状態のベースパス表示更新
    const apiNameField = document.getElementById('api_name');
    const initialApiName = apiNameField ? apiNameField.value.trim() : '';
    updateEndpointBasePaths(initialApiName);
    
    // API名フィールドにフォーカス設定
    if (apiNameField) {
        apiNameField.focus();
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

/**
 * エンドポイント追加
 */
function addEndpoint() {
    endpointCounter++;
    
    const template = document.getElementById('endpoint-template');
    if (!template) {
        console.error('endpoint-template not found');
        return;
    }
    
    const clone = template.content.cloneNode(true);
    
    // エンドポイント番号設定
    clone.querySelector('.endpoint-number').textContent = endpointCounter;
    
    // コンテナに追加
    const container = document.getElementById('endpoints-container');
    if (!container) {
        console.error('endpoints-container not found');
        return;
    }
    
    container.appendChild(clone);
    
    // メッセージ非表示
    updateNoEndpointsMessage();
    
    // アニメーション追加
    const newEndpoint = container.lastElementChild;
    newEndpoint.classList.add('fade-in');
    
    // モデル一覧を更新
    updateEndpointModelOptions(newEndpoint);
    
    // ベースパスとフルパス初期設定
    const apiNameInput = document.getElementById('api_name');
    const apiName = apiNameInput ? apiNameInput.value.trim() : '';
    
    // 新しく追加されたエンドポイントのベースパスを設定
    const basePathElement = newEndpoint.querySelector('.endpoint-base-path');
    if (basePathElement) {
        const basePathText = apiName ? `/api/v1/${apiName}` : '/api/v1/[api名]';
        basePathElement.textContent = basePathText;
    }
    
    updateSingleFullPath(newEndpoint, apiName);
    
    // 相対パス入力のイベントリスナー追加
    const relativePathInput = newEndpoint.querySelector('.endpoint-relative-path');
    if (relativePathInput) {
        relativePathInput.addEventListener('input', function() {
            updateSingleFullPath(newEndpoint);
        });
    }
    
    // フォーカス設定
    newEndpoint.querySelector('.endpoint-method').focus();
    
    // イベントリスナー追加
    addEndpointEventListeners(newEndpoint);
}

/**
 * エンドポイント削除
 */
function removeEndpoint(button) {
    const endpointItem = button.closest('.endpoint-item');
    endpointItem.remove();
    updateNoEndpointsMessage();
    updateEndpointsJson();
}

/**
 * エンドポイントイベントリスナー追加
 */
function addEndpointEventListeners(endpointElement) {
    const inputs = endpointElement.querySelectorAll('input, select');
    inputs.forEach(input => {
        input.addEventListener('change', updateEndpointsJson);
        input.addEventListener('input', updateEndpointsJson);
    });
}

/**
 * エンドポイントなしメッセージ表示/非表示
 */
function updateNoEndpointsMessage() {
    const container = document.getElementById('endpoints-container');
    const message = document.getElementById('no-endpoints-message');
    const hasEndpoints = container.children.length > 0;
    
    message.style.display = hasEndpoints ? 'none' : 'block';
}

/**
 * エンドポイントのモデル選択肢を更新
 */
function updateEndpointModelOptions(endpointElement = null) {
    const models = JSON.parse(document.getElementById('models_json').value || '[]');
    
    // 特定のエンドポイントか、全エンドポイントか
    const endpoints = endpointElement ? [endpointElement] : document.querySelectorAll('.endpoint-item');
    
    endpoints.forEach(endpoint => {
        const requestSelect = endpoint.querySelector('.endpoint-request-model');
        const responseSelect = endpoint.querySelector('.endpoint-response-model');
        
        // 現在の選択値を保存
        const currentRequest = requestSelect.value;
        const currentResponse = responseSelect.value;
        
        // リクエストモデル選択肢更新
        requestSelect.innerHTML = '<option value="">なし</option>';
        models.forEach(model => {
            const option = document.createElement('option');
            option.value = model.name;
            option.textContent = model.name;
            requestSelect.appendChild(option);
        });
        
        // レスポンスモデル選択肢更新
        responseSelect.innerHTML = '<option value="">String (デフォルト)</option>';
        models.forEach(model => {
            const option = document.createElement('option');
            option.value = model.name;
            option.textContent = model.name;
            responseSelect.appendChild(option);
        });
        
        // 元の選択値を復元
        requestSelect.value = currentRequest;
        responseSelect.value = currentResponse;
    });
}

/**
 * エンドポイントデータをJSONに変換
 */
function updateEndpointsJson() {
    const endpoints = [];
    const endpointItems = document.querySelectorAll('.endpoint-item');
    
    endpointItems.forEach(endpointItem => {
        const method = endpointItem.querySelector('.endpoint-method').value;
        const relativePath = endpointItem.querySelector('.endpoint-relative-path').value.trim();
        const operationId = endpointItem.querySelector('.endpoint-operation-id').value.trim();
        
        // フルパスを生成
        const apiNameInput = document.getElementById('api_name');
        const apiName = apiNameInput ? apiNameInput.value.trim() : '';
        const fullPath = apiName && relativePath ? `/api/v1/${apiName}${relativePath}` : relativePath;
        const description = endpointItem.querySelector('.endpoint-description').value.trim();
        const requestModel = endpointItem.querySelector('.endpoint-request-model').value;
        const responseModel = endpointItem.querySelector('.endpoint-response-model').value;
        
        if (!method || !relativePath || !operationId) return; // 必須項目がない場合はスキップ
        
        // エラーレスポンス取得
        const errorResponses = [];
        const errorResponseItems = endpointItem.querySelectorAll('.error-response-item');
        
        errorResponseItems.forEach(errorItem => {
            const statusCode = errorItem.querySelector('.error-status-code').value;
            const errorDescription = errorItem.querySelector('.error-description').value.trim();
            const errorModel = errorItem.querySelector('.error-response-model').value;
            
            if (statusCode && errorDescription) {
                errorResponses.push({
                    statusCode: statusCode,
                    description: errorDescription,
                    model: errorModel || null
                });
            }
        });
        
        const endpoint = {
            method: method,
            path: fullPath,
            operationId: operationId,
            description: description,
            requestModel: requestModel || null,
            responseModel: responseModel || null,
            errorResponses: errorResponses
        };
        
        endpoints.push(endpoint);
    });
    
    document.getElementById('endpoints_json').value = JSON.stringify(endpoints);
}

/**
 * エンドポイントのベースパスを更新
 */
function updateEndpointBasePaths(apiName) {
    console.log('updateEndpointBasePaths called with:', apiName);
    const basePaths = document.querySelectorAll('.endpoint-base-path');
    console.log('Found base paths:', basePaths.length);
    const basePathText = apiName ? `/api/v1/${apiName}` : '/api/v1/[api名]';
    
    basePaths.forEach(basePathElement => {
        console.log('Updating base path to:', basePathText);
        basePathElement.textContent = basePathText;
    });
    
    // フルパスも更新
    updateAllFullPaths(apiName);
}

/**
 * 全エンドポイントのフルパスを更新
 */
function updateAllFullPaths(apiName) {
    const endpointItems = document.querySelectorAll('.endpoint-item');
    
    endpointItems.forEach(endpointItem => {
        updateSingleFullPath(endpointItem, apiName);
    });
}

/**
 * 単一エンドポイントのフルパス更新
 */
function updateSingleFullPath(endpointItem, apiName = null) {
    if (!apiName) {
        const apiNameInput = document.getElementById('api_name');
        apiName = apiNameInput ? apiNameInput.value.trim() : '';
    }
    
    const relativePathInput = endpointItem.querySelector('.endpoint-relative-path');
    const fullPathDisplay = endpointItem.querySelector('.endpoint-full-path');
    
    if (relativePathInput && fullPathDisplay) {
        const relativePath = relativePathInput.value.trim();
        const basePath = apiName ? `/api/v1/${apiName}` : '/api/v1/[api名]';
        const fullPath = relativePath ? basePath + relativePath : basePath;
        
        fullPathDisplay.textContent = fullPath;
    }
}

/**
 * 既存のupdateModelsJsonを拡張してエンドポイントのモデル選択肢も更新
 */
function extendUpdateModelsJson() {
    if (typeof updateModelsJson === 'function') {
        const originalUpdateModelsJson = updateModelsJson;
        updateModelsJson = function() {
            originalUpdateModelsJson();
            updateEndpointModelOptions();
            updateErrorResponseModelOptions();
        };
    }
}

/**
 * APIルート表示を更新
 */
function updateApiRouteDisplay(apiName) {
    const routeDisplay = document.getElementById('api-route-display');
    const routePattern = document.getElementById('api-route-pattern');
    
    if (!apiName) {
        hideApiRouteDisplay();
        return;
    }
    
    // ルートパターン生成
    const baseRoute = `/api/v1/${apiName}`;
    const exampleRoutes = [
        `${baseRoute}/users`,
        `${baseRoute}/users/{id}`,
        `${baseRoute}/orders`,
        `${baseRoute}/products`
    ];
    
    // HTML生成
    let html = `<div class="font-monospace"><strong>ベースパス:</strong> ${baseRoute}</div>`;
    html += `<div class="font-monospace mt-1"><strong>例:</strong></div>`;
    html += '<ul class="font-monospace mb-0 mt-1">';
    exampleRoutes.forEach(route => {
        html += `<li>${route}</li>`;
    });
    html += '</ul>';
    
    routePattern.innerHTML = html;
    routeDisplay.style.display = 'block';
}

/**
 * APIルート表示を非表示
 */
function hideApiRouteDisplay() {
    const routeDisplay = document.getElementById('api-route-display');
    if (routeDisplay) {
        routeDisplay.style.display = 'none';
    }
}

/**
 * エラーレスポンス追加
 */
function addErrorResponse(button) {
    console.log('addErrorResponse function called', button);
    const template = document.getElementById('error-response-template');
    if (!template) {
        console.error('error-response-template not found');
        return;
    }
    
    const clone = template.content.cloneNode(true);
    
    // エンドポイントのエラーレスポンスコンテナに追加
    const endpointItem = button.closest('.endpoint-item');
    const errorContainer = endpointItem.querySelector('.error-responses-container');
    errorContainer.appendChild(clone);
    
    // 新しく追加されたエラーレスポンスのモデル選択肢を更新
    updateErrorResponseModelOptions(errorContainer.lastElementChild);
    
    // イベントリスナー追加
    const newErrorResponse = errorContainer.lastElementChild;
    const inputs = newErrorResponse.querySelectorAll('input, select');
    inputs.forEach(input => {
        input.addEventListener('change', updateEndpointsJson);
        input.addEventListener('input', updateEndpointsJson);
    });
}

/**
 * エラーレスポンス削除
 */
function removeErrorResponse(button) {
    const errorResponseItem = button.closest('.error-response-item');
    errorResponseItem.remove();
    updateEndpointsJson();
}

/**
 * エラーレスポンスのモデル選択肢を更新
 */
function updateErrorResponseModelOptions(errorResponseElement = null) {
    const models = JSON.parse(document.getElementById('models_json').value || '[]');
    
    // 特定のエラーレスポンスか、全エラーレスポンスか
    const errorResponses = errorResponseElement ? [errorResponseElement] : document.querySelectorAll('.error-response-item');
    
    errorResponses.forEach(errorResponse => {
        const responseSelect = errorResponse.querySelector('.error-response-model');
        
        // 現在の選択値を保存
        const currentValue = responseSelect.value;
        
        // レスポンスモデル選択肢更新
        responseSelect.innerHTML = '<option value="">String (デフォルト)</option>';
        models.forEach(model => {
            const option = document.createElement('option');
            option.value = model.name;
            option.textContent = model.name;
            responseSelect.appendChild(option);
        });
        
        // 元の選択値を復元
        responseSelect.value = currentValue;
    });
}

// DOM読み込み完了後に実行
document.addEventListener('DOMContentLoaded', function() {
    extendUpdateModelsJson();
});