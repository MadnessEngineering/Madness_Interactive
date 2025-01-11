pub mod api;
pub mod browser;
pub mod event;
pub mod platform;
pub mod templates;

// Re-export common types
pub use platform::{
    PlatformWindow,
    PlatformWebView,
    WindowTheme,
    PlatformError,
    common::{
        WindowConfig,
        WebViewConfig,
        WindowHandle,
        WebViewHandle,
    },
};

// Version information
pub const VERSION: &str = env!("CARGO_PKG_VERSION");
pub const NAME: &str = env!("CARGO_PKG_NAME");

// Feature flags
#[cfg(feature = "transparent")]
pub const TRANSPARENT_WINDOWS: bool = true;
#[cfg(not(feature = "transparent"))]
pub const TRANSPARENT_WINDOWS: bool = false;

/// Initialize the browser with default configuration
pub fn init() -> Result<browser::BrowserEngine, Box<dyn std::error::Error>> {
    let config = platform::common::utils::get_default_window_config();
    browser::BrowserEngine::new(config)
}

/// Initialize the browser with custom configuration
pub fn init_with_config(config: WindowConfig) -> Result<browser::BrowserEngine, Box<dyn std::error::Error>> {
    browser::BrowserEngine::new(config)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_version() {
        assert!(!VERSION.is_empty());
        assert!(!NAME.is_empty());
    }

    #[test]
    fn test_init() {
        let result = init();
        assert!(result.is_ok());
    }

    #[test]
    fn test_init_with_config() {
        let config = WindowConfig::default();
        let result = init_with_config(config);
        assert!(result.is_ok());
    }
}
