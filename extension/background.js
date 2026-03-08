const WS_URL = "ws://localhost:8765";
let socket = null;
let reconnectTimer = null;

function connect() {
    socket = new WebSocket(WS_URL);

    socket.onopen = () => {
        if (reconnectTimer) { clearTimeout(reconnectTimer); reconnectTimer = null; }
    };

    socket.onmessage = (event) => {
        handleCommand(event.data.trim());
    };

    socket.onclose = () => {
        reconnectTimer = setTimeout(connect, 3000);
    };
}

async function handleCommand(cmd) {
    if (cmd === "open_youtube") {
        const tabs = await chrome.tabs.query({ url: "*://*.youtube.com/*" });
        if (tabs.length > 0) {
            chrome.tabs.update(tabs[0].id, { active: true });
            chrome.windows.update(tabs[0].windowId, { focused: true });
        } else {
            chrome.tabs.create({ url: "https://m.youtube.com" });
        }
        return;
    }

    const tabs = await chrome.tabs.query({ url: "*://*.youtube.com/*", active: true });
    let tab = tabs[0];
    if (!tab) {
        const allYt = await chrome.tabs.query({ url: "*://*.youtube.com/*" });
        tab = allYt[0];
    }
    if (!tab) return;

    if (cmd === "next_track") {
        chrome.scripting.executeScript({
            target: { tabId: tab.id },
            func: () => {
                const btn = document.querySelector('button[aria-label="Vidéo suivante"]');
                if (btn) btn.click();
            }
        });
    }

    if (cmd === "prev_track") {
        chrome.scripting.executeScript({
            target: { tabId: tab.id },
            func: () => {
                const btn = document.querySelector('button[aria-label="Vidéo précédente"]');
                if (btn) btn.click();
            }
        });
    }

    if (cmd === "toggle_repeat") {
        chrome.scripting.executeScript({
            target: { tabId: tab.id },
            func: () => {
                const btn = document.querySelector('button[aria-label="Playlist en boucle"]') ||
                            document.querySelector('button[aria-label="Lire en boucle"]') ||
                            document.querySelector('button[aria-label="Désactiver la lecture en boucle"]');
                if (btn) btn.click();
            }
        });
    }

    if (cmd === "toggle_shuffle") {
        chrome.scripting.executeScript({
            target: { tabId: tab.id },
            func: () => {
                const btn = document.querySelector('button[aria-label="Playlist en mode aléatoire"]');
                if (btn) btn.click();
            }
        });
    }
}

connect();
