use tao::window::Window;
use std::sync::mpsc::Sender;
use tracing::debug;
use std::fmt;

#[derive(Debug)]
pub enum MenuCommand {
    NewTab,
    NewWindow,
    CloseTab,
    CloseWindow,
    ZoomIn,
    ZoomOut,
    ZoomReset,
    ToggleDevTools,
    StartRecording,
    StopRecording,
    RunTests,
    ViewTestReport,
    SwitchEngine(JsEngine),
    OpenJsConsole,
    OpenPerformanceMonitor,
    OpenDocumentation,
    ReportIssue,
    About,
}

#[derive(Debug)]
pub enum JsEngine {
    V8,
    SpiderMonkey,
    JavaScriptCore,
}

impl fmt::Display for JsEngine {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            JsEngine::V8 => write!(f, "V8"),
            JsEngine::SpiderMonkey => write!(f, "SpiderMonkey"),
            JsEngine::JavaScriptCore => write!(f, "JavaScriptCore"),
        }
    }
}

pub fn create_application_menu(_window: &Window, command_tx: Sender<MenuCommand>) -> Option<()> {
    // For now, we'll return None since we need to implement platform-specific menus
    // This will be implemented in a future update
    debug!("Menu system will be implemented in a future update");
    None
}
