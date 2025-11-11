// client.js
document.addEventListener('DOMContentLoaded', () => {
    const subtitleEl = document.getElementById('subtitle');
    const mouthEl = document.getElementById('mouth');

    const ws = new WebSocket(`ws://${location.host}/ws`);

    ws.onopen = () => {
        console.log('WebSocket connection established');
        subtitleEl.textContent = 'Ready';
        subtitleEl.classList.add('visible');
    };

    ws.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            handleWebSocketMessage(data);
        } catch (error) {
            console.error('Error parsing WebSocket message:', error);
        }
    };

    ws.onclose = () => {
        console.log('WebSocket connection closed');
        subtitleEl.textContent = 'Disconnected';
    };

    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        subtitleEl.textContent = 'Error';
    };

    function handleWebSocketMessage(data) {
        switch (data.type) {
            case 'utter_start':
                subtitleEl.textContent = data.subtitle || '...';
                subtitleEl.classList.add('visible');
                mouthEl.classList.add('visible');
                break;
            case 'mouth':
                // value は 0.0 (closed) to 1.0 (open)
                const scaleY = Math.max(0, Math.min(1, data.value));
                mouthEl.style.transform = `scaleY(${scaleY})`;
                break;
            case 'utter_end':
                subtitleEl.classList.remove('visible');
                mouthEl.classList.remove('visible');
                mouthEl.style.transform = 'scaleY(0)';
                break;
            default:
                console.warn('Unknown message type:', data.type);
        }
    }
});
