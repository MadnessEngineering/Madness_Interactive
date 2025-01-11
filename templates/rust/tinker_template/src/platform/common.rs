use std::sync::Arc;
use tao::window::Window;
use wry::WebView;
use super::PlatformError;

/// Common window configuration across platforms
#[derive(Debug, Clone)]
pub struct WindowConfig {
    pub title: String,
    pub width: u32,
    pub height: u32,
    pub visible: bool,
    pub transparent: bool,
    pub decorations: bool,
}

impl Default for WindowConfig {
    fn default() -> Self {
        Self {
            title: "Tinker".to_string(),
            width: 1024,
            height: 768,
            visible: false,
            transparent: true,
            decorations: true,
        }
    }
}

/// Common WebView configuration across platforms
#[derive(Debug, Clone)]
pub struct WebViewConfig {
    pub transparent: bool,
    pub visible: bool,
    pub init_script: Option<String>,
}

impl Default for WebViewConfig {
    fn default() -> Self {
        Self {
            transparent: true,
            visible: false,
            init_script: Some(include_str!("../../assets/js/init.js").to_string()),
        }
    }
}

/// Platform-agnostic window handle
#[derive(Clone)]
pub struct WindowHandle {
    window: Arc<Window>,
}

impl WindowHandle {
    pub fn new(window: Window) -> Self {
        Self {
            window: Arc::new(window),
        }
    }

    pub fn get_window(&self) -> &Window {
        &self.window
    }

    pub fn set_visible(&self, visible: bool) {
        self.window.set_visible(visible);
    }

    pub fn set_title(&self, title: &str) {
        self.window.set_title(title);
    }
}

/// Platform-agnostic WebView handle
pub struct WebViewHandle {
    webview: WebView,
}

impl WebViewHandle {
    pub fn new(webview: WebView) -> Self {
        Self { webview }
    }

    pub fn evaluate_script(&self, script: &str) -> Result<(), PlatformError> {
        self.webview
            .evaluate_script(script)
            .map_err(|e| PlatformError::Other(e.to_string()))
    }

    pub fn get_window(&self) -> Option<&Window> {
        self.webview.window().as_window()
    }
}

/// Utility functions for platform-specific operations
pub mod utils {
    use super::*;
    use std::env::consts::OS;

    pub fn get_platform() -> &'static str {
        OS
    }

    pub fn is_macos() -> bool {
        OS == "macos"
    }

    pub fn is_windows() -> bool {
        OS == "windows"
    }

    pub fn is_linux() -> bool {
        OS == "linux"
    }

    pub fn get_default_window_config() -> WindowConfig {
        WindowConfig::default()
    }

    pub fn get_default_webview_config() -> WebViewConfig {
        WebViewConfig::default()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_window_config_default() {
        let config = WindowConfig::default();
        assert_eq!(config.title, "Tinker");
        assert_eq!(config.width, 1024);
        assert_eq!(config.height, 768);
        assert!(!config.visible);
        assert!(config.transparent);
        assert!(config.decorations);
    }

    #[test]
    fn test_webview_config_default() {
        let config = WebViewConfig::default();
        assert!(config.transparent);
        assert!(!config.visible);
        assert!(config.init_script.is_some());
    }

    #[test]
    fn test_platform_detection() {
        let platform = utils::get_platform();
        assert!(!platform.is_empty());
        
        // At least one of these should be true
        assert!(utils::is_macos() || utils::is_windows() || utils::is_linux());
    }
} 
