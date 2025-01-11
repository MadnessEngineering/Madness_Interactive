#[cfg(target_os = "macos")]
pub mod macos;
#[cfg(target_os = "macos")]
pub use self::macos::*;

#[cfg(target_os = "windows")]
pub mod windows;
#[cfg(target_os = "windows")]
pub use self::windows::*;

#[cfg(target_os = "linux")]
pub mod linux;
#[cfg(target_os = "linux")]
pub use self::linux::*;

pub mod common;
pub use self::common::*;

/// Platform-specific window creation options
pub trait PlatformWindow {
    fn create_window(&self) -> Result<tao::window::Window, Box<dyn std::error::Error>>;
    fn set_theme(&self, theme: WindowTheme);
    fn show(&self);
    fn hide(&self);
}

/// Platform-specific WebView creation options
pub trait PlatformWebView {
    fn create_webview(&self) -> Result<wry::WebView, Box<dyn std::error::Error>>;
    fn set_visibility(&self, visible: bool);
    fn update_bounds(&self);
}

/// Common window themes across platforms
#[derive(Debug, Clone, Copy)]
pub enum WindowTheme {
    Light,
    Dark,
    System,
}

/// Common error type for platform operations
#[derive(Debug, thiserror::Error)]
pub enum PlatformError {
    #[error("Window creation failed: {0}")]
    WindowCreation(String),
    
    #[error("WebView creation failed: {0}")]
    WebViewCreation(String),
    
    #[error("Operation not supported on current platform")]
    Unsupported,
    
    #[error("Platform-specific error: {0}")]
    Other(String),
} 
