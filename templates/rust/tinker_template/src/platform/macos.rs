use super::{PlatformWindow, PlatformWebView, WindowTheme, PlatformError};
use tao::{
    window::{Window, WindowBuilder},
    dpi::LogicalSize,
    platform::macos::WindowExtMacOS,
};
use wry::WebViewBuilder;

pub struct MacOSWindow {
    window: Window,
}

impl MacOSWindow {
    pub fn new() -> Result<Self, PlatformError> {
        let window = WindowBuilder::new()
            .with_title("Tinker")
            .with_inner_size(LogicalSize::new(1024, 768))
            .with_visible(false) // Start invisible for smoother initialization
            .with_titlebar_transparent(true)
            .with_fullsize_content_view(true)
            .build(&tao::event_loop::EventLoop::new())
            .map_err(|e| PlatformError::WindowCreation(e.to_string()))?;

        Ok(Self { window })
    }
}

impl PlatformWindow for MacOSWindow {
    fn create_window(&self) -> Result<Window, Box<dyn std::error::Error>> {
        // Clone the existing window configuration
        let window = WindowBuilder::new()
            .with_title("Tinker")
            .with_inner_size(LogicalSize::new(1024, 768))
            .with_visible(true)
            .with_titlebar_transparent(true)
            .with_fullsize_content_view(true)
            .build(&tao::event_loop::EventLoop::new())?;

        Ok(window)
    }

    fn set_theme(&self, theme: WindowTheme) {
        match theme {
            WindowTheme::Light => self.window.set_theme(Some(tao::window::Theme::Light)),
            WindowTheme::Dark => self.window.set_theme(Some(tao::window::Theme::Dark)),
            WindowTheme::System => self.window.set_theme(None),
        }
    }

    fn show(&self) {
        self.window.set_visible(true);
    }

    fn hide(&self) {
        self.window.set_visible(false);
    }
}

pub struct MacOSWebView {
    webview: wry::WebView,
}

impl MacOSWebView {
    pub fn new(window: &Window) -> Result<Self, PlatformError> {
        let webview = WebViewBuilder::new(window)
            .with_transparent(true)
            .with_initialization_script(include_str!("../../assets/js/init.js"))
            .build()
            .map_err(|e| PlatformError::WebViewCreation(e.to_string()))?;

        Ok(Self { webview })
    }
}

impl PlatformWebView for MacOSWebView {
    fn create_webview(&self) -> Result<wry::WebView, Box<dyn std::error::Error>> {
        // Clone the existing webview configuration
        let webview = WebViewBuilder::new(&self.webview.window())
            .with_transparent(true)
            .with_initialization_script(include_str!("../../assets/js/init.js"))
            .build()?;

        Ok(webview)
    }

    fn set_visibility(&self, visible: bool) {
        if let Some(window) = self.webview.window().as_window() {
            window.set_visible(visible);
        }
    }

    fn update_bounds(&self) {
        if let Some(window) = self.webview.window().as_window() {
            // Force a redraw of the WebView
            window.set_visible(false);
            window.set_visible(true);
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use tao::event_loop::EventLoop;

    #[test]
    #[ignore = "Window creation must be on main thread"]
    fn test_macos_window_creation() {
        let window = MacOSWindow::new();
        assert!(window.is_ok());
    }

    #[test]
    #[ignore = "Window creation must be on main thread"]
    fn test_macos_webview_creation() {
        let event_loop = EventLoop::new();
        let window = WindowBuilder::new()
            .build(&event_loop)
            .expect("Failed to create window");
        
        let webview = MacOSWebView::new(&window);
        assert!(webview.is_ok());
    }
} 
