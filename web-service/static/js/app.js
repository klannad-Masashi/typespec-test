// TypeSpec Generator Web Service JavaScript

/**
 * システム状態確認
 */
async function checkSystemStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        const statusElement = document.getElementById('status-info');
        if (!statusElement) return;
        
        let statusHtml = '';
        
        if (data.error) {
            statusHtml = `<span class="badge bg-danger">エラー: ${data.error}</span>`;
        } else {
            const typespecStatus = data.typespec_running ? 
                '<span class="badge bg-success">稼働中</span>' : 
                '<span class="badge bg-danger">停止中</span>';
            const generatorStatus = data.generator_running ? 
                '<span class="badge bg-success">稼働中</span>' : 
                '<span class="badge bg-danger">停止中</span>';
                
            statusHtml = `
                <div class="row">
                    <div class="col-md-4">
                        <strong>TypeSpec:</strong> ${typespecStatus}
                    </div>
                    <div class="col-md-4">
                        <strong>Generator:</strong> ${generatorStatus}
                    </div>
                    <div class="col-md-4">
                        <small class="text-muted">Workspace: ${data.workspace_path}</small>
                    </div>
                </div>
            `;
        }
        
        statusElement.innerHTML = statusHtml;
    } catch (error) {
        console.error('ステータス確認エラー:', error);
        const statusElement = document.getElementById('status-info');
        if (statusElement) {
            statusElement.innerHTML = '<span class="badge bg-warning">ステータス確認失敗</span>';
        }
    }
}

/**
 * TypeSpecコンパイル実行
 */
async function compileApi(apiName) {
    const button = event.target;
    const originalText = button.textContent;
    
    try {
        // ボタン状態変更
        button.disabled = true;
        button.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>コンパイル中...';
        
        const response = await fetch(`/api/compile/${apiName}`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        // 結果表示
        showResultModal('TypeSpecコンパイル結果', data);
        
    } catch (error) {
        console.error('コンパイルエラー:', error);
        showResultModal('TypeSpecコンパイル結果', {
            status: 'error',
            message: `コンパイルエラー: ${error.message}`
        });
    } finally {
        // ボタン状態復元
        button.disabled = false;
        button.textContent = originalText;
    }
}

/**
 * Spring Boot生成実行
 */
async function generateSpring(apiName) {
    const button = event.target;
    const originalText = button.textContent;
    
    try {
        // ボタン状態変更
        button.disabled = true;
        button.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>生成中...';
        
        const response = await fetch(`/api/generate-spring/${apiName}`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        // 結果表示
        showResultModal('Spring Boot生成結果', data);
        
    } catch (error) {
        console.error('Spring生成エラー:', error);
        showResultModal('Spring Boot生成結果', {
            status: 'error',
            message: `Spring生成エラー: ${error.message}`
        });
    } finally {
        // ボタン状態復元
        button.disabled = false;
        button.textContent = originalText;
    }
}

/**
 * 結果モーダル表示
 */
function showResultModal(title, data) {
    const modal = new bootstrap.Modal(document.getElementById('resultModal'));
    const titleElement = document.getElementById('resultModalTitle');
    const contentElement = document.getElementById('resultContent');
    
    titleElement.textContent = title;
    
    let contentHtml = '';
    
    if (data.status === 'success') {
        contentHtml = `
            <div class="alert alert-success">
                <h6>成功</h6>
                <p>${data.message}</p>
            </div>
        `;
        
        if (data.output) {
            contentHtml += `
                <div class="mt-3">
                    <h6>出力:</h6>
                    <div class="code-block">${escapeHtml(data.output)}</div>
                </div>
            `;
        }
        
        if (data.spring_output) {
            contentHtml += `
                <div class="mt-3">
                    <h6>Spring Boot出力:</h6>
                    <div class="code-block">${escapeHtml(data.spring_output)}</div>
                </div>
            `;
        }
        
        if (data.junit_output) {
            contentHtml += `
                <div class="mt-3">
                    <h6>JUnit出力:</h6>
                    <div class="code-block">${escapeHtml(data.junit_output)}</div>
                </div>
            `;
        }
    } else {
        contentHtml = `
            <div class="alert alert-danger">
                <h6>エラー</h6>
                <p>${escapeHtml(data.message || 'unknown error')}</p>
            </div>
        `;
    }
    
    contentElement.innerHTML = contentHtml;
    modal.show();
}

/**
 * HTMLエスケープ
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * API名バリデーション
 */
function validateApiName(name) {
    const pattern = /^[a-z][a-z0-9-]*$/;
    return pattern.test(name);
}

/**
 * フォームバリデーション表示
 */
function showValidationError(element, message) {
    element.classList.add('is-invalid');
    
    let feedback = element.parentNode.querySelector('.invalid-feedback');
    if (!feedback) {
        feedback = document.createElement('div');
        feedback.className = 'invalid-feedback';
        element.parentNode.appendChild(feedback);
    }
    
    feedback.textContent = message;
}

/**
 * フォームバリデーションクリア
 */
function clearValidationError(element) {
    element.classList.remove('is-invalid');
    
    const feedback = element.parentNode.querySelector('.invalid-feedback');
    if (feedback) {
        feedback.remove();
    }
}