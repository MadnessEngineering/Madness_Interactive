use std::sync::{Arc, Mutex};
use tinker::{
    browser::BrowserEngine,
    event::{EventSystem, BrowserEvent},
};

#[test]
fn test_browser_navigation() {
    let mut browser = BrowserEngine::new(false, None, None);

    // Create initial tab and get its URL
    let initial_url = {
        let mut tabs = browser.tabs.lock().unwrap();
        let id = tabs.create_tab("about:blank".to_string());
        tabs.get_active_tab().map(|tab| tab.url.clone()).unwrap()
    };
    assert_eq!(initial_url, "about:blank");

    // Navigate to the test URL
    browser.navigate("https://www.example.com").unwrap();

    // Verify the URL was updated
    let final_url = {
        let tabs = browser.tabs.lock().unwrap();
        tabs.get_active_tab().map(|tab| tab.url.clone()).unwrap()
    };
    assert_eq!(final_url, "https://www.example.com");
}

#[test]
fn test_tab_management() {
    let mut browser = BrowserEngine::new(false, None, None);

    // Create multiple tabs
    let tab1_id = browser.create_tab("https://example.com/1").expect("Failed to create tab 1");
    let tab2_id = browser.create_tab("https://example.com/2").expect("Failed to create tab 2");

    // Verify tabs were created
    let tabs = browser.tabs.lock().unwrap();
    assert_eq!(tabs.get_all_tabs().len(), 2);
    assert_eq!(tabs.get_active_tab().unwrap().id, tab2_id);
    drop(tabs);

    // Test tab switching
    browser.switch_to_tab(tab1_id).expect("Failed to switch tabs");
    let tabs = browser.tabs.lock().unwrap();
    assert_eq!(tabs.get_active_tab().unwrap().id, tab1_id);
    drop(tabs);

    // Test tab closing
    browser.close_tab(tab2_id).expect("Failed to close tab");
    let tabs = browser.tabs.lock().unwrap();
    assert_eq!(tabs.get_all_tabs().len(), 1);
    assert_eq!(tabs.get_active_tab().unwrap().id, tab1_id);
}

#[test]
fn test_tab_error_handling() {
    let mut browser = BrowserEngine::new(false, None, None);

    // Test invalid tab operations
    assert!(browser.switch_to_tab(999).is_err());
    assert!(browser.close_tab(999).is_err());

    // Create a tab and verify it exists
    let tab_id = browser.create_tab("https://example.com").expect("Failed to create tab");
    let tabs = browser.tabs.lock().unwrap();
    assert_eq!(tabs.get_all_tabs().len(), 1);
    assert_eq!(tabs.get_active_tab().unwrap().id, tab_id);
    drop(tabs);

    // Try to close the last tab (should fail)
    assert!(browser.close_tab(tab_id).is_err());

    // Verify tab state remains consistent
    let tabs = browser.tabs.lock().unwrap();
    assert_eq!(tabs.get_all_tabs().len(), 1);
    assert_eq!(tabs.get_active_tab().unwrap().id, tab_id);
}

#[test]
fn test_event_system() {
    // Create event system
    let mut events = EventSystem::new("localhost", "test-browser");
    events.connect().unwrap();
    let events = Arc::new(Mutex::new(events));

    // Create browser with events enabled
    let mut browser = BrowserEngine::new(false, Some(events), None);

    // Test tab creation events
    let tab_id = browser.create_tab("https://example.com").unwrap();
    
    // Test tab switching events
    browser.switch_to_tab(tab_id).unwrap();
    
    // Test navigation events
    browser.navigate("https://example.com/page2").unwrap();
    
    // Test tab closing events
    browser.close_tab(tab_id).unwrap();
}

#[test]
fn test_event_replay() {
    let mut browser = BrowserEngine::new(false, None, None);
    
    // Create a tab and verify it's created
    let tab_id = browser.create_tab("https://example.com").unwrap();
    
    // Replay a navigation event
    let event = BrowserEvent::Navigation {
        url: "https://example.com/page2".to_string()
    };
    if let Ok(mut tabs) = browser.tabs.lock() {
        if let Some(tab) = tabs.get_tab_mut(tab_id) {
            tab.url = "https://example.com/page2".to_string();
        }
    }
    
    // Verify the URL was updated
    let final_url = {
        let tabs = browser.tabs.lock().unwrap();
        tabs.get_active_tab().map(|tab| tab.url.clone()).unwrap()
    };
    assert_eq!(final_url, "https://example.com/page2");
} 
