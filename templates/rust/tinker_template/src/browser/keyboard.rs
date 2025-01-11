use std::fmt::Debug;

#[derive(Debug)]
pub enum KeyCommand {
    Back,
    Forward,
    Refresh,
    NewTab,
    CloseTab,
    SwitchTab(usize),
    FocusAddressBar,
    StopLoading,
}

#[derive(Debug, Clone, Copy)]
pub enum KeyCode {
    ArrowLeft,
    ArrowRight,
    KeyT,
    KeyW,
    KeyR,
    KeyL,
    Escape,
    Digit1,
    Digit2,
    Digit3,
    Digit4,
    Digit5,
    Digit6,
    Digit7,
    Digit8,
    Digit9,
}

#[derive(Debug, Clone, Copy)]
pub struct ModifiersState {
    pub alt: bool,
    pub ctrl: bool,
    pub shift: bool,
    pub meta: bool,
}

impl ModifiersState {
    pub fn alt(&self) -> bool {
        self.alt
    }

    pub fn control(&self) -> bool {
        self.ctrl
    }

    pub const ALT: Self = Self {
        alt: true,
        ctrl: false,
        shift: false,
        meta: false,
    };

    pub const CONTROL: Self = Self {
        alt: false,
        ctrl: true,
        shift: false,
        meta: false,
    };
}

pub fn handle_keyboard_input(key: KeyCode, modifiers: ModifiersState) -> Option<KeyCommand> {
    match (key, modifiers.alt(), modifiers.control()) {
        // Navigation
        (KeyCode::ArrowLeft, true, false) => Some(KeyCommand::Back),
        (KeyCode::ArrowRight, true, false) => Some(KeyCommand::Forward),
        
        // Tab Management
        (KeyCode::KeyT, false, true) => Some(KeyCommand::NewTab),
        (KeyCode::KeyW, false, true) => Some(KeyCommand::CloseTab),
        
        // Numbers 1-9 for tab switching
        (KeyCode::Digit1, false, true) => Some(KeyCommand::SwitchTab(0)),
        (KeyCode::Digit2, false, true) => Some(KeyCommand::SwitchTab(1)),
        (KeyCode::Digit3, false, true) => Some(KeyCommand::SwitchTab(2)),
        (KeyCode::Digit4, false, true) => Some(KeyCommand::SwitchTab(3)),
        (KeyCode::Digit5, false, true) => Some(KeyCommand::SwitchTab(4)),
        (KeyCode::Digit6, false, true) => Some(KeyCommand::SwitchTab(5)),
        (KeyCode::Digit7, false, true) => Some(KeyCommand::SwitchTab(6)),
        (KeyCode::Digit8, false, true) => Some(KeyCommand::SwitchTab(7)),
        (KeyCode::Digit9, false, true) => Some(KeyCommand::SwitchTab(8)),
        
        // Page Controls
        (KeyCode::KeyR, false, true) => Some(KeyCommand::Refresh),
        (KeyCode::KeyL, false, true) => Some(KeyCommand::FocusAddressBar),
        (KeyCode::Escape, false, false) => Some(KeyCommand::StopLoading),
        
        _ => None,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_navigation_shortcuts() {
        let alt = ModifiersState::ALT;
        assert!(matches!(
            handle_keyboard_input(KeyCode::ArrowLeft, alt),
            Some(KeyCommand::Back)
        ));
        assert!(matches!(
            handle_keyboard_input(KeyCode::ArrowRight, alt),
            Some(KeyCommand::Forward)
        ));
    }

    #[test]
    fn test_tab_shortcuts() {
        let ctrl = ModifiersState::CONTROL;
        assert!(matches!(
            handle_keyboard_input(KeyCode::KeyT, ctrl),
            Some(KeyCommand::NewTab)
        ));
        assert!(matches!(
            handle_keyboard_input(KeyCode::KeyW, ctrl),
            Some(KeyCommand::CloseTab)
        ));
    }

    #[test]
    fn test_tab_switching() {
        let ctrl = ModifiersState::CONTROL;
        assert!(matches!(
            handle_keyboard_input(KeyCode::Digit1, ctrl),
            Some(KeyCommand::SwitchTab(0))
        ));
        assert!(matches!(
            handle_keyboard_input(KeyCode::Digit9, ctrl),
            Some(KeyCommand::SwitchTab(8))
        ));
    }
} 
