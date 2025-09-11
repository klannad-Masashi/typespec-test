// 共通モデル編集のためのJavaScript

// 新しい共通モデルを追加
function addCommonModel() {
    commonModelCounter++;
    
    const template = document.getElementById('common-model-template');
    const clone = template.content.cloneNode(true);
    
    // モデル番号を設定
    clone.querySelector('.common-model-number').textContent = commonModelCounter;
    
    // コンテナに追加
    const container = document.getElementById('common-models-container');
    container.appendChild(clone);
    
    // フィールドタイプ変更イベントを追加
    const modelItem = container.lastElementChild;
    const typeSelects = modelItem.querySelectorAll('.common-field-type');
    typeSelects.forEach(select => {
        select.addEventListener('change', function() {
            toggleCommonFieldConstraints(this);
        });
    });
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

// フォーム送信処理
document.getElementById('editCommonModelForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const modelItems = document.querySelectorAll('.common-model-item');
    let modelData = null;
    
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
        
        modelData = {
            name: name,
            description: description,
            fields: fields
        };
    });
    
    if (!modelData) {
        alert('モデルデータを入力してください');
        return;
    }
    
    // 更新APIを呼び出し
    updateCommonModel(modelData);
});

// 共通モデルを更新
async function updateCommonModel(modelData) {
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
            showResultModal('成功', `
                <div class="alert alert-success">
                    <h6>共通modelの更新が完了しました！</h6>
                    <p>${result.message}</p>
                </div>
            `, true);
            
            // 成功後は一覧に戻る
            setTimeout(() => {
                window.location.href = '/common-models';
            }, 2000);
        } else {
            showResultModal('エラー', `
                <div class="alert alert-danger">
                    <h6>共通modelの更新に失敗しました</h6>
                    <p>${result.error}</p>
                </div>
            `, false);
        }
    } catch (error) {
        console.error('Update error:', error);
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