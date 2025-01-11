use tinker::browser::keyboard::{KeyCode, ModifiersState, KeyCommand, handle_keyboard_input};

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
