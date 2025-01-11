use std::sync::{Arc, RwLock};
use crate::{
    platform::{
        PlatformWindow,
        WindowConfig,
        WindowHandle,
        WindowTheme,
        common::utils as platform_utils,
    },
    browser::error::{WindowError, BrowserResult},
};

/// Manages window creation and lifecycle
pub struct WindowManager {
    windows: Arc<RwLock<Vec<WindowHandle>>>,
    config: WindowConfig,
}

impl WindowManager {
    pub fn new(config: WindowConfig) -> Self {
        Self {
            windows: Arc::new(RwLock::new(Vec::new())),
            config,
        }
    }

    /// Create a new window with the current configuration
    pub fn create_window(&self) -> BrowserResult<WindowHandle> {
        let window = if platform_utils::is_macos() {
            use crate::platform::macos::MacOSWindow;
            let window = MacOSWindow::new()
                .map_err(|e| WindowError::Creation(e.to_string()))?;
            window.create_window()
                .map_err(|e| WindowError::Creation(e.to_string()))?
        } else {
            return Err(WindowError::Creation("Unsupported platform".to_string()).into());
        };

        let handle = WindowHandle::new(window);
        
        if let Ok(mut windows) = self.windows.write() {
            windows.push(handle.clone());
        } else {
            return Err(WindowError::Creation("Failed to acquire write lock".to_string()).into());
        }

        Ok(handle)
    }

    /// Get a window by its index
    pub fn get_window(&self, index: usize) -> BrowserResult<WindowHandle> {
        if let Ok(windows) = self.windows.read() {
            windows.get(index)
                .cloned()
                .ok_or_else(|| WindowError::NotFound(format!("Window index {} not found", index)).into())
        } else {
            Err(WindowError::NotFound("Failed to acquire read lock".to_string()).into())
        }
    }

    /// Set the theme for all windows
    pub fn set_theme(&self, theme: WindowTheme) -> BrowserResult<()> {
        if let Ok(windows) = self.windows.read() {
            for window in windows.iter() {
                // This is a placeholder until we implement proper theme handling
                window.set_title(&format!("Theme: {:?}", theme));
            }
            Ok(())
        } else {
            Err(WindowError::Update("Failed to acquire read lock".to_string()).into())
        }
    }

    /// Show all windows
    pub fn show_all(&self) -> BrowserResult<()> {
        if let Ok(windows) = self.windows.read() {
            for window in windows.iter() {
                window.set_visible(true);
            }
            Ok(())
        } else {
            Err(WindowError::Update("Failed to acquire read lock".to_string()).into())
        }
    }

    /// Hide all windows
    pub fn hide_all(&self) -> BrowserResult<()> {
        if let Ok(windows) = self.windows.read() {
            for window in windows.iter() {
                window.set_visible(false);
            }
            Ok(())
        } else {
            Err(WindowError::Update("Failed to acquire read lock".to_string()).into())
        }
    }

    /// Get the current window configuration
    pub fn get_config(&self) -> WindowConfig {
        self.config.clone()
    }

    /// Update the window configuration
    pub fn update_config(&mut self, config: WindowConfig) {
        self.config = config;
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn create_test_config() -> WindowConfig {
        WindowConfig {
            title: "Test Window".to_string(),
            width: 800,
            height: 600,
            visible: false,
            transparent: true,
            decorations: true,
        }
    }

    #[test]
    fn test_window_manager_creation() {
        let config = create_test_config();
        let manager = WindowManager::new(config.clone());
        assert_eq!(manager.get_config().title, "Test Window");
    }

    #[test]
    fn test_config_update() {
        let config = create_test_config();
        let mut manager = WindowManager::new(config);
        
        let new_config = WindowConfig {
            title: "Updated Window".to_string(),
            ..create_test_config()
        };
        
        manager.update_config(new_config);
        assert_eq!(manager.get_config().title, "Updated Window");
    }

    #[test]
    #[cfg_attr(not(target_os = "macos"), ignore)]
    fn test_window_creation() {
        let config = create_test_config();
        let manager = WindowManager::new(config);
        
        let result = manager.create_window();
        if platform_utils::is_macos() {
            assert!(result.is_ok());
        } else {
            assert!(result.is_err());
        }
    }
} 
