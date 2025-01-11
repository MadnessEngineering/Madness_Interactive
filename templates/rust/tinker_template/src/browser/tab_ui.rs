use tao::window::Window;
use std::sync::mpsc::Sender;
use wry::{WebView, WebViewBuilder};
use std::sync::{Arc, Mutex};
use tracing::{debug, error};

#[derive(Clone)]
pub struct TabBar {
    webview: Arc<Mutex<WebView>>,
    cmd_tx: Sender<TabCommand>,
}

impl TabBar {
    pub fn new(window: &Window, cmd_tx: Sender<TabCommand>) -> Result<Self, String> {
        debug!("Creating new TabBar");
        
        let webview = WebViewBuilder::new(window)
            .with_bounds(wry::Rect {
                x: 0_i32,
                y: 0_i32,
                width: window.inner_size().width,
                height: 40,
            })
            .with_visible(true)
            .with_transparent(false)
            .with_initialization_script(include_str!("../templates/tab_bar.js"))
            .with_html(include_str!("../templates/tab_bar.html"))
            .map_err(|e| format!("Failed to create tab bar WebView: {}", e))?
            .build()
            .map_err(|e| format!("Failed to build tab bar WebView: {}", e))?;

        debug!("TabBar WebView created successfully");
        
        Ok(TabBar {
            webview: Arc::new(Mutex::new(webview)),
            cmd_tx,
        })
    }

    pub fn add_tab(&self, id: u32, title: &str, url: &str) {
        if let Ok(webview) = self.webview.lock() {
            let _ = webview.evaluate_script(&format!(
                "addTab({}, '{}', '{}');",
                id,
                title.replace('\'', "\\'"),
                url.replace('\'', "\\'")
            ));
        }
    }

    pub fn remove_tab(&self, id: u32) {
        if let Ok(webview) = self.webview.lock() {
            let _ = webview.evaluate_script(&format!("removeTab({});", id));
        }
    }

    pub fn set_active_tab(&self, id: u32) {
        if let Ok(webview) = self.webview.lock() {
            let _ = webview.evaluate_script(&format!("setActiveTab({});", id));
        }
    }

    pub fn update_bounds(&self, window: &Window) {
        if let Ok(view) = self.webview.lock() {
            view.set_bounds(wry::Rect {
                x: 0_i32,
                y: 0_i32,
                width: window.inner_size().width,
                height: 40,
            });
            view.set_visible(true);
        }
    }

    pub fn update_tab_url(&self, id: usize, url: &str) {
        if let Ok(view) = self.webview.lock() {
            let msg = serde_json::json!({
                "type": "updateUrl",
                "id": id,
                "url": url
            });
            if let Err(e) = view.evaluate_script(&format!("window.updateTabUrl({});", msg)) {
                error!("Failed to update tab URL: {}", e);
            }
        }
    }

    pub fn update_tab_title(&self, id: usize, title: &str) {
        if let Ok(view) = self.webview.lock() {
            let msg = serde_json::json!({
                "type": "updateTitle",
                "id": id,
                "title": title
            });
            if let Err(e) = view.evaluate_script(&format!("window.updateTabTitle({});", msg)) {
                error!("Failed to update tab title: {}", e);
            }
        }
    }
}

#[derive(Debug, serde::Deserialize)]
#[serde(tag = "type", rename_all = "snake_case")]
pub enum TabCommand {
    Create { url: String },
    Close { id: usize },
    Switch { id: usize },
    UpdateUrl { id: usize, url: String },
    UpdateTitle { id: usize, title: String },
} 
