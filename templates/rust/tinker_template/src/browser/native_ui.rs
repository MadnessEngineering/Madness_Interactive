use tao::window::{Window, WindowBuilder};
use tao::dpi::LogicalSize;
use std::sync::{Arc, Mutex};

pub struct NativeTabBar {
    height: u32,
    tabs: Arc<Mutex<Vec<TabInfo>>>,
}

struct TabInfo {
    id: usize,
    title: String,
    active: bool,
}

impl NativeTabBar {
    pub fn new(parent: &Window) -> Result<Self, Box<dyn std::error::Error>> {
        Ok(NativeTabBar {
            height: 40,
            tabs: Arc::new(Mutex::new(Vec::new())),
        })
    }

    pub fn add_tab(&mut self, id: usize, title: &str) {
        if let Ok(mut tabs) = self.tabs.lock() {
            tabs.push(TabInfo {
                id,
                title: title.to_string(),
                active: false,
            });
        }
    }

    pub fn remove_tab(&mut self, id: usize) {
        if let Ok(mut tabs) = self.tabs.lock() {
            if let Some(pos) = tabs.iter().position(|tab| tab.id == id) {
                tabs.remove(pos);
            }
        }
    }

    pub fn set_active_tab(&mut self, id: usize) {
        if let Ok(mut tabs) = self.tabs.lock() {
            for tab in tabs.iter_mut() {
                tab.active = tab.id == id;
            }
        }
    }

    pub fn get_height(&self) -> u32 {
        self.height
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use tao::window::WindowBuilder;

    // Helper function to create a window for testing
    #[cfg(not(target_os = "macos"))]
    fn create_test_window() -> Window {
        let event_loop = tao::event_loop::EventLoop::new();
        WindowBuilder::new()
            .with_title("Test Window")
            .build(&event_loop)
            .unwrap()
    }

    // Mock window for macOS tests
    #[cfg(target_os = "macos")]
    fn create_test_window() -> Window {
        // Create a mock window for testing
        let event_loop = tao::event_loop::EventLoop::new();
        WindowBuilder::new()
            .with_title("Test Window")
            .build(&event_loop)
            .unwrap()
    }

    #[test]
    #[cfg_attr(target_os = "macos", ignore = "Window creation must be on main thread")]
    fn test_native_tab_bar_creation() {
        let window = create_test_window();
        let tab_bar = NativeTabBar::new(&window);
        assert!(tab_bar.is_ok());
        
        let tab_bar = tab_bar.unwrap();
        assert_eq!(tab_bar.height, 40);
    }

    #[test]
    #[cfg_attr(target_os = "macos", ignore = "Window creation must be on main thread")]
    fn test_tab_management() {
        let window = create_test_window();
        let mut tab_bar = NativeTabBar::new(&window).unwrap();
        
        // Test adding a tab
        tab_bar.add_tab(1, "Test Tab");
        let tabs = tab_bar.tabs.lock().unwrap();
        assert_eq!(tabs.len(), 1);
        assert_eq!(tabs[0].id, 1);
        assert_eq!(tabs[0].title, "Test Tab");
        drop(tabs);

        // Test setting active tab
        tab_bar.set_active_tab(1);
        let tabs = tab_bar.tabs.lock().unwrap();
        assert!(tabs[0].active);
        drop(tabs);

        // Test removing a tab
        tab_bar.remove_tab(1);
        let tabs = tab_bar.tabs.lock().unwrap();
        assert_eq!(tabs.len(), 0);
    }

    #[test]
    #[cfg_attr(target_os = "macos", ignore = "Window creation must be on main thread")]
    fn test_multiple_tabs() {
        let window = create_test_window();
        let mut tab_bar = NativeTabBar::new(&window).unwrap();
        
        // Add multiple tabs
        tab_bar.add_tab(1, "Tab 1");
        tab_bar.add_tab(2, "Tab 2");
        tab_bar.add_tab(3, "Tab 3");

        let tabs = tab_bar.tabs.lock().unwrap();
        assert_eq!(tabs.len(), 3);
        
        // Verify tab order
        assert_eq!(tabs[0].id, 1);
        assert_eq!(tabs[1].id, 2);
        assert_eq!(tabs[2].id, 3);
    }
} 
