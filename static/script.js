// Upload Handling
const uploadForm = document.getElementById('upload-form');
if (uploadForm) {
    uploadForm.onsubmit = async function(e) {
        e.preventDefault();
        const formData = new FormData(uploadForm);
        const statusDiv = document.getElementById('upload-status');
        
        statusDiv.innerHTML = '<div class="text-info">Processing document... this may take a moment.</div>';
        
        try {
            const response = await fetch('/upload', { method: 'POST', body: formData });
            const result = await response.json();
            if (response.ok) {
                statusDiv.innerHTML = `<div class="text-success">${result.message}</div>`;
                uploadForm.reset();
            } else {
                statusDiv.innerHTML = `<div class="text-danger">Error: ${result.error}</div>`;
            }
        } catch (err) {
            statusDiv.innerHTML = '<div class="text-danger">Network Error</div>';
        }
    };
}

// Chat Handling
async function sendMessage() {
    const input = document.getElementById('user-input');
    const chatBox = document.getElementById('chat-box');
    const query = input.value.trim();

    if (!query) return;

    // Add User Message
    chatBox.innerHTML += `
        <div class="chat-message user-message mb-3">
            <div class="p-3 rounded">${query}</div>
        </div>`;
    input.value = '';
    chatBox.scrollTop = chatBox.scrollHeight;

    // Add Loading Spinner
    const loadingId = 'loading-' + Date.now();
    chatBox.innerHTML += `
        <div class="chat-message bot-message mb-3" id="${loadingId}">
            <div class="p-3 bg-light rounded">Thinking...</div>
        </div>`;

    try {
        const response = await fetch('/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: query })
        });
        const data = await response.json();
        
        // Remove loading
        document.getElementById(loadingId).remove();

        // Format Sources
        let sourceHtml = '';
        if (data.sources && data.sources.length > 0) {
            sourceHtml = `<div class="sources-small">Sources: ${data.sources.join(', ')}</div>`;
        }

        // Add Bot Response
        chatBox.innerHTML += `
            <div class="chat-message bot-message mb-3">
                <div class="p-3 bg-light rounded">
                    ${data.answer.replace(/\n/g, '<br>')}
                    ${sourceHtml}
                </div>
            </div>`;

    } catch (err) {
        document.getElementById(loadingId).innerHTML = '<div class="text-danger">Error communicating with AI.</div>';
    }
    chatBox.scrollTop = chatBox.scrollHeight;
}