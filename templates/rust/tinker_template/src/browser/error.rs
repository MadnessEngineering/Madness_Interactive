use std::fmt;
use thiserror::Error;
use crate::platform::PlatformError;

#[derive(Debug, Error)]
pub enum BrowserError {
    #[error("Window error: {0}")]
    Window(#[from] WindowError),

    #[error("Tab error: {0}")]
    Tab(#[from] TabError),

    #[error("Navigation error: {0}")]
    Navigation(#[from] NavigationError),

    #[error("State error: {0}")]
    State(#[from] StateError),

    #[error("JavaScript error: {0}")]
    JavaScript(#[from] JavaScriptError),

    #[error("Platform error: {0}")]
    Platform(#[from] PlatformError),

    #[error("Other error: {0}")]
    Other(String),
}

#[derive(Debug, Error)]
pub enum WindowError {
    #[error("Failed to create window: {0}")]
    Creation(String),

    #[error("Failed to update window: {0}")]
    Update(String),

    #[error("Window not found: {0}")]
    NotFound(String),

    #[error("Invalid window state: {0}")]
    InvalidState(String),
}

#[derive(Debug, Error)]
pub enum TabError {
    #[error("Failed to create tab: {0}")]
    Creation(String),

    #[error("Failed to update tab: {0}")]
    Update(String),

    #[error("Tab not found: {id}")]
    NotFound { id: usize },

    #[error("Cannot close last tab")]
    CannotCloseLast,

    #[error("Invalid tab state: {0}")]
    InvalidState(String),
}

#[derive(Debug, Error)]
pub enum NavigationError {
    #[error("Invalid URL: {0}")]
    InvalidUrl(String),

    #[error("Navigation failed: {0}")]
    Failed(String),

    #[error("Navigation timeout")]
    Timeout,

    #[error("Navigation cancelled")]
    Cancelled,
}

#[derive(Debug, Error)]
pub enum StateError {
    #[error("State lock failed: {0}")]
    LockFailed(String),

    #[error("Invalid state transition: {from} -> {to}")]
    InvalidTransition {
        from: String,
        to: String,
    },

    #[error("State not initialized")]
    NotInitialized,
}

#[derive(Debug, Error)]
pub enum JavaScriptError {
    #[error("Script execution failed: {0}")]
    ExecutionFailed(String),

    #[error("Invalid script: {0}")]
    InvalidScript(String),

    #[error("Script timeout")]
    Timeout,

    #[error("Context error: {0}")]
    ContextError(String),
}

// Result type alias for browser operations
pub type BrowserResult<T> = Result<T, BrowserError>;

// Implement conversion from string errors
impl From<String> for BrowserError {
    fn from(error: String) -> Self {
        BrowserError::Other(error)
    }
}

impl From<&str> for BrowserError {
    fn from(error: &str) -> Self {
        BrowserError::Other(error.to_string())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_browser_error_conversion() {
        let err: BrowserError = "test error".into();
        assert!(matches!(err, BrowserError::Other(_)));
    }

    #[test]
    fn test_window_error() {
        let err = WindowError::Creation("failed to create window".to_string());
        let browser_err: BrowserError = err.into();
        assert!(matches!(browser_err, BrowserError::Window(_)));
    }

    #[test]
    fn test_tab_error() {
        let err = TabError::NotFound { id: 1 };
        let browser_err: BrowserError = err.into();
        assert!(matches!(browser_err, BrowserError::Tab(_)));
    }

    #[test]
    fn test_navigation_error() {
        let err = NavigationError::InvalidUrl("invalid url".to_string());
        let browser_err: BrowserError = err.into();
        assert!(matches!(browser_err, BrowserError::Navigation(_)));
    }
} 
