// 共通モデル管理のためのJavaScript

let commonModelCounter = 0;

// 既存の共通モデルを読み込み
async function loadExistingCommonModels() {
    try {
        const response = await fetch('/api/common-models');
        const models = await response.json();
        
        const container = document.getElementById('existing-models-container');
        const loadingSpan = document.getElementById('loading-existing');
        
        if (models.length === 0) {
            container.innerHTML = '<div class="text-muted text-center py-3">既存の共通modelがありません。</div>';
        } else {
            let html = '<div class="row">';
            models.forEach(model => {
                html += `
                    <div class="col-md-6 col-lg-4 mb-3">
                        <div class="card border-success">
                            <div class="card-body">
                                <div class="d-flex justify-content-between align-items-start mb-2">
                                    <h6 class="card-title text-success mb-0">${model.name}</h6>
                                    <div class="btn-group-vertical btn-group-sm">
                                        <button type="button" class="btn btn-outline-primary btn-sm" onclick="editCommonModel(${model.id || 'null'}, '${model.name}', '${model.description || ''}')">
                                            編集
                                        </button>
                                        <button type="button" class="btn btn-outline-danger btn-sm" onclick="deleteCommonModel(${model.id || 'null'}, '${model.name}')">
                                            削除
                                        </button>
                                    </div>
                                </div>
                                <p class="card-text small text-muted">${model.description || 'No description'}</p>
                                <small class="text-muted">共通model</small>
                            </div>
                        </div>
                    </div>
                `;
            });
            html += '</div>';
            container.innerHTML = html;
        }
    } catch (error) {
        console.error('Failed to load existing common models:', error);
        document.getElementById('existing-models-container').innerHTML = 
            '<div class="text-danger text-center py-3">既存モデルの読み込みに失敗しました。</div>';
    }
}

// 新しい共通モデルを追加
function addCommonModel() {
    commonModelCounter++;
    
    const template = document.getElementById('common-model-template');
    const clone = template.content.cloneNode(true);
    
    // モデル番号を設定
    clone.querySelector('.common-model-number').textContent = commonModelCounter;
    
    // コンテナに追加
    const container = document.getElementById('common-models-container');
    const noModelsMessage = document.getElementById('no-common-models-message');
    
    container.appendChild(clone);
    noModelsMessage.style.display = 'none';
    
    // 送信ボタンを表示
    document.getElementById('submit-section').style.display = 'block';
    
    // フィールドタイプ変更イベントを追加
    const modelItem = container.lastElementChild;
    const typeSelects = modelItem.querySelectorAll('.common-field-type');
    typeSelects.forEach(select => {
        select.addEventListener('change', function() {
            toggleCommonFieldConstraints(this);
        });
    });
}

// 共通モデルを削除
function removeCommonModel(button) {
    const modelItem = button.closest('.common-model-item');
    modelItem.remove();
    
    // モデルが全て削除された場合の処理
    const container = document.getElementById('common-models-container');
    const noModelsMessage = document.getElementById('no-common-models-message');
    
    if (container.children.length === 0) {
        noModelsMessage.style.display = 'block';
        document.getElementById('submit-section').style.display = 'none';
    }
    
    // モデル番号を更新
    updateCommonModelNumbers();
}

// 共通フィールドを追加
function addCommonField(button) {
    const template = document.getElementById('common-field-template');
    const clone = template.content.cloneNode(true);
    
    // フィールドタイプ変更イベントを追加
    const typeSelect = clone.querySelector('.common-field-type');
    typeSelect.addEventListener('change', function() {
        toggleCommonFieldConstraints(this);
    });
    
    // モデルのフィールドコンテナに追加
    const modelItem = button.closest('.common-model-item');
    const fieldsContainer = modelItem.querySelector('.common-fields-container');
    fieldsContainer.appendChild(clone);
}

// 共通フィールドを削除
function removeCommonField(button) {
    const fieldItem = button.closest('.common-field-item');
    fieldItem.remove();
}

// フィールドタイプに応じて制限入力欄の表示/非表示を切り替え
function toggleCommonFieldConstraints(selectElement) {
    const fieldItem = selectElement.closest('.common-field-item');
    const constraintsDiv = fieldItem.querySelector('.common-field-constraints');
    const minLabel = fieldItem.querySelector('.common-constraint-min-label');
    const maxLabel = fieldItem.querySelector('.common-constraint-max-label');
    const minInput = fieldItem.querySelector('.common-field-min-value');
    const maxInput = fieldItem.querySelector('.common-field-max-value');
    
    const fieldType = selectElement.value;
    
    if (fieldType === 'integer' || fieldType === 'number') {
        constraintsDiv.style.display = 'block';
        minLabel.textContent = '最小値';
        maxLabel.textContent = '最大値';
        minInput.type = 'number';
        maxInput.type = 'number';
        minInput.placeholder = '最小値';
        maxInput.placeholder = '最大値';
    } else if (fieldType === 'string' || fieldType === 'text' || fieldType === 'email' || fieldType === 'url') {
        constraintsDiv.style.display = 'block';
        minLabel.textContent = '最小文字数';
        maxLabel.textContent = '最大文字数';
        minInput.type = 'number';
        maxInput.type = 'number';
        minInput.placeholder = '最小文字数';
        maxInput.placeholder = '最大文字数';
    } else {
        constraintsDiv.style.display = 'none';
    }
}

// モデル番号を更新
function updateCommonModelNumbers() {
    const models = document.querySelectorAll('.common-model-item');
    models.forEach((model, index) => {
        model.querySelector('.common-model-number').textContent = index + 1;
    });
    commonModelCounter = models.length;
}

// フォーム送信時の処理
document.getElementById('commonModelsForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const models = [];
    const modelItems = document.querySelectorAll('.common-model-item');
    
    modelItems.forEach(item => {
        const name = item.querySelector('.common-model-name').value.trim();
        const description = item.querySelector('.common-model-description').value.trim();
        
        if (!name) {
            alert('モデル名は必須です');
            return;
        }
        
        const fields = [];
        const fieldItems = item.querySelectorAll('.common-field-item');
        
        fieldItems.forEach(fieldItem => {
            const fieldName = fieldItem.querySelector('.common-field-name').value.trim();
            const fieldType = fieldItem.querySelector('.common-field-type').value;
            const fieldRequired = fieldItem.querySelector('.common-field-required').checked;
            const fieldDescription = fieldItem.querySelector('.common-field-description').value.trim();
            const minValue = fieldItem.querySelector('.common-field-min-value').value;
            const maxValue = fieldItem.querySelector('.common-field-max-value').value;
            
            if (!fieldName) return;
            
            const validations = {};
            
            if (fieldType === 'integer' || fieldType === 'number') {
                if (minValue) validations.minimum = parseFloat(minValue);
                if (maxValue) validations.maximum = parseFloat(maxValue);
            } else if (fieldType === 'string' || fieldType === 'text' || fieldType === 'email' || fieldType === 'url') {
                if (minValue) validations.minLength = parseInt(minValue);
                if (maxValue) validations.maxLength = parseInt(maxValue);
            }
            
            fields.push({
                name: fieldName,
                type: fieldType,
                required: fieldRequired,
                description: fieldDescription,
                validations: validations
            });
        });
        
        models.push({
            name: name,
            description: description,
            fields: fields
        });
    });
    
    if (models.length === 0) {
        alert('少なくとも1つの共通modelを定義してください');
        return;
    }
    
    // JSONデータを設定
    document.getElementById('common_models_json').value = JSON.stringify(models);
    
    // フォームを送信
    submitCommonModels(models);
});

// 共通モデルを編集
function editCommonModel(modelId, modelName, modelDescription) {
    // 編集ページに遷移
    window.location.href = `/edit-common-model/${modelId}`;
}

// 共通モデルを削除
function deleteCommonModel(modelId, modelName) {
    if (confirm(`「${modelName}」を削除しますか？\nこの操作は取り消せません。`)) {
        deleteCommonModelRequest(modelId);
    }
}

// 共通モデル更新API呼び出し
async function updateCommonModel(modelId, modelData) {
    try {
        const response = await fetch(`/api/common-models/${modelId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(modelData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert('共通modelを更新しました');
            loadExistingCommonModels(); // 一覧を再読み込み
        } else {
            alert('更新に失敗しました: ' + (result.error || '不明なエラー'));
        }
    } catch (error) {
        console.error('Update failed:', error);
        alert('通信エラーが発生しました: ' + error.message);
    }
}

// 共通モデル削除API呼び出し
async function deleteCommonModelRequest(modelId) {
    try {
        const response = await fetch(`/api/common-models/${modelId}`, {
            method: 'DELETE',
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert('共通modelを削除しました');
            loadExistingCommonModels(); // 一覧を再読み込み
        } else {
            alert('削除に失敗しました: ' + (result.error || '不明なエラー'));
        }
    } catch (error) {
        console.error('Delete failed:', error);
        alert('通信エラーが発生しました: ' + error.message);
    }
}

// 共通モデルをサーバーに送信
async function submitCommonModels(models) {
    try {
        const response = await fetch('/api/common-models/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ models: models })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showResultModal('成功', `
                <div class="alert alert-success">
                    <h6>共通modelの追加が完了しました！</h6>
                    <p>${result.message}</p>
                    <p><strong>ファイル:</strong> ${result.file_path}</p>
                </div>
            `, true);
            
            // フォームをリセット
            setTimeout(() => {
                location.reload();
            }, 2000);
        } else {
            showResultModal('エラー', `
                <div class="alert alert-danger">
                    <h6>共通モデルの追加に失敗しました</h6>
                    <p>${result.error}</p>
                </div>
            `, false);
        }
    } catch (error) {
        console.error('Submit error:', error);
        showResultModal('エラー', `
            <div class="alert alert-danger">
                <h6>通信エラーが発生しました</h6>
                <p>${error.message}</p>
            </div>
        `, false);
    }
}

// 結果モーダルを表示
function showResultModal(title, content, success) {
    document.getElementById('resultModalTitle').textContent = title;
    document.getElementById('resultContent').innerHTML = content;
    
    const modal = new bootstrap.Modal(document.getElementById('resultModal'));
    modal.show();
}