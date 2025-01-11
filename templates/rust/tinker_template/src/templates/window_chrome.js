// IPC setup
window.ipc = {
    postMessage: (msg) => window.ipc.external.invoke(JSON.stringify(msg)),
    handleMessage: (msg) =>
    {
        console.log('Message from Rust:', msg);
        try
        {
            const data = JSON.parse(msg);
            switch (data.type)
            {
                case 'navigate':
                    navigateToUrl(data.url);
                    break;
                case 'updateTitle':
                    document.title = data.title;
                    break;
                case 'loadingStateChanged':
                    updateLoadingState(data.isLoading);
                    break;
                case 'navigationStateChanged':
                    updateNavigationState(data.canGoBack, data.canGoForward);
                    break;
                default:
                    console.warn('Unknown message type:', data.type);
            }
        } catch (e)
        {
            console.error('Failed to parse message:', e);
        }
    }
};

// Navigation functions
function navigateToUrl(url)
{
    const urlInput = document.getElementById('url-input');
    urlInput.value = url;
    updateLoadingState(true);

    window.ipc.postMessage({
        type: 'navigate',
        url: url
    });
}

function updateLoadingState(isLoading)
{
    const content = document.getElementById('content');
    if (isLoading)
    {
        content.classList.add('loading');
    } else
    {
        content.classList.remove('loading');
    }
}

function updateNavigationState(canGoBack, canGoForward)
{
    const backButton = document.getElementById('back-button');
    const forwardButton = document.getElementById('forward-button');

    backButton.disabled = !canGoBack;
    forwardButton.disabled = !canGoForward;
}

// Event listeners
document.getElementById('url-input').addEventListener('keypress', (e) =>
{
    if (e.key === 'Enter')
    {
        let url = e.target.value.trim();
        if (!url.startsWith('http://') && !url.startsWith('https://'))
        {
            // Check if it's a URL-like input
            if (url.includes('.') && !url.includes(' '))
            {
                url = 'https://' + url;
            } else
            {
                // Treat as search query
                url = `https://www.google.com/search?q=${encodeURIComponent(url)}`;
            }
        }
        navigateToUrl(url);
    }
});

document.getElementById('back-button').addEventListener('click', () =>
{
    window.ipc.postMessage({
        type: 'navigate_back'
    });
});

document.getElementById('forward-button').addEventListener('click', () =>
{
    window.ipc.postMessage({
        type: 'navigate_forward'
    });
});

document.getElementById('reload-button').addEventListener('click', () =>
{
    window.ipc.postMessage({
        type: 'reload'
    });
});

document.getElementById('settings-button').addEventListener('click', () =>
{
    window.ipc.postMessage({
        type: 'open_settings'
    });
});

// Initialize loading indicator
updateLoadingState(false); 
