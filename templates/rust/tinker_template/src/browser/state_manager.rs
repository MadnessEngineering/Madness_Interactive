use std::sync::{Arc, RwLock};
use serde::{Serialize, Deserialize};
use crate::browser::error::{StateError, BrowserResult};

/// Represents the current state of a browser window
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum WindowState {
    Initializing,
    Ready,
    Loading,
    Error(String),
}

/// Represents the current state of a browser tab
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum TabState {
    Loading,
    Ready,
    Error(String),
}

/// Represents the overall browser state
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BrowserState {
    window_state: WindowState,
    active_tab: Option<usize>,
    tab_states: Vec<(usize, TabState)>,
    is_incognito: bool,
}

impl Default for BrowserState {
    fn default() -> Self {
        Self {
            window_state: WindowState::Initializing,
            active_tab: None,
            tab_states: Vec::new(),
            is_incognito: false,
        }
    }
}

/// Manages the browser's state
pub struct StateManager {
    state: Arc<RwLock<BrowserState>>,
}

impl StateManager {
    pub fn new() -> Self {
        Self {
            state: Arc::new(RwLock::new(BrowserState::default())),
        }
    }

    /// Get a snapshot of the current state
    pub fn get_state(&self) -> BrowserResult<BrowserState> {
        self.state
            .read()
            .map(|state| state.clone())
            .map_err(|e| StateError::LockFailed(e.to_string()).into())
    }

    /// Update the window state
    pub fn set_window_state(&self, new_state: WindowState) -> BrowserResult<()> {
        let mut state = self.state
            .write()
            .map_err(|e| StateError::LockFailed(e.to_string()))?;

        // Validate state transition
        let transition_valid = match (&state.window_state, &new_state) {
            (WindowState::Initializing, WindowState::Ready) => true,
            (WindowState::Ready, WindowState::Loading) => true,
            (WindowState::Loading, WindowState::Ready) => true,
            (_, WindowState::Error(_)) => true,
            _ => false,
        };

        if !transition_valid {
            return Err(StateError::InvalidTransition {
                from: format!("{:?}", state.window_state),
                to: format!("{:?}", new_state),
            }.into());
        }

        state.window_state = new_state;
        Ok(())
    }

    /// Update the state of a specific tab
    pub fn set_tab_state(&self, tab_id: usize, new_state: TabState) -> BrowserResult<()> {
        let mut state = self.state
            .write()
            .map_err(|e| StateError::LockFailed(e.to_string()))?;

        if let Some(tab_state) = state.tab_states.iter_mut().find(|(id, _)| *id == tab_id) {
            tab_state.1 = new_state;
            Ok(())
        } else {
            state.tab_states.push((tab_id, new_state));
            Ok(())
        }
    }

    /// Set the active tab
    pub fn set_active_tab(&self, tab_id: usize) -> BrowserResult<()> {
        let mut state = self.state
            .write()
            .map_err(|e| StateError::LockFailed(e.to_string()))?;

        if state.tab_states.iter().any(|(id, _)| *id == tab_id) {
            state.active_tab = Some(tab_id);
            Ok(())
        } else {
            Err(StateError::InvalidState(format!("Tab {} not found", tab_id)).into())
        }
    }

    /// Get the active tab ID
    pub fn get_active_tab(&self) -> BrowserResult<Option<usize>> {
        self.state
            .read()
            .map(|state| state.active_tab)
            .map_err(|e| StateError::LockFailed(e.to_string()).into())
    }

    /// Set incognito mode
    pub fn set_incognito(&self, enabled: bool) -> BrowserResult<()> {
        let mut state = self.state
            .write()
            .map_err(|e| StateError::LockFailed(e.to_string()))?;
        
        state.is_incognito = enabled;
        Ok(())
    }

    /// Check if incognito mode is enabled
    pub fn is_incognito(&self) -> BrowserResult<bool> {
        self.state
            .read()
            .map(|state| state.is_incognito)
            .map_err(|e| StateError::LockFailed(e.to_string()).into())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_state_manager_creation() {
        let manager = StateManager::new();
        let state = manager.get_state().unwrap();
        assert_eq!(state.window_state, WindowState::Initializing);
        assert_eq!(state.active_tab, None);
        assert!(state.tab_states.is_empty());
        assert!(!state.is_incognito);
    }

    #[test]
    fn test_window_state_transition() {
        let manager = StateManager::new();
        
        // Valid transitions
        assert!(manager.set_window_state(WindowState::Ready).is_ok());
        assert!(manager.set_window_state(WindowState::Loading).is_ok());
        assert!(manager.set_window_state(WindowState::Ready).is_ok());
        assert!(manager.set_window_state(WindowState::Error("test".to_string())).is_ok());

        // Invalid transition
        let manager = StateManager::new();
        assert!(manager.set_window_state(WindowState::Loading).is_err());
    }

    #[test]
    fn test_tab_state_management() {
        let manager = StateManager::new();
        
        // Add a tab
        assert!(manager.set_tab_state(1, TabState::Loading).is_ok());
        
        // Update tab state
        assert!(manager.set_tab_state(1, TabState::Ready).is_ok());
        
        // Set active tab
        assert!(manager.set_active_tab(1).is_ok());
        assert_eq!(manager.get_active_tab().unwrap(), Some(1));
        
        // Invalid tab
        assert!(manager.set_active_tab(2).is_err());
    }

    #[test]
    fn test_incognito_mode() {
        let manager = StateManager::new();
        
        assert!(!manager.is_incognito().unwrap());
        assert!(manager.set_incognito(true).is_ok());
        assert!(manager.is_incognito().unwrap());
    }
} 
