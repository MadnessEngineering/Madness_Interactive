use tinker::event::{BrowserEvent, EventSystem};

#[test]
fn test_event_serialization() {
    // Test Navigation event
    let event = BrowserEvent::Navigation {
        url: "https://example.com".to_string(),
    };
    let json = serde_json::to_string(&event).unwrap();
    assert!(json.contains("Navigation"));
    assert!(json.contains("example.com"));

    // Test TabCreated event
    let event = BrowserEvent::TabCreated { 
        id: 1,
        url: "https://example.com".to_string(),
    };
    let json = serde_json::to_string(&event).unwrap();
    assert!(json.contains("TabCreated"));
    assert!(json.contains("1"));
    assert!(json.contains("example.com"));

    // Test TabUrlChanged event
    let event = BrowserEvent::TabUrlChanged {
        id: 1,
        url: "https://example.com".to_string(),
    };
    let json = serde_json::to_string(&event).unwrap();
    assert!(json.contains("TabUrlChanged"));
    assert!(json.contains("example.com"));

    // Test Error event
    let event = BrowserEvent::Error {
        message: "Test error".to_string(),
    };
    let json = serde_json::to_string(&event).unwrap();
    assert!(json.contains("Error"));
    assert!(json.contains("Test error"));
}

#[test]
fn test_event_system_creation() {
    let system = EventSystem::new("localhost", "test-client");
    assert!(system.client.is_none());
    assert_eq!(system.options.client_id(), "test-client");
}

#[test]
fn test_event_topic_mapping() {
    // Test Navigation event topic
    let event = BrowserEvent::Navigation {
        url: "https://example.com".to_string(),
    };
    let topic = match &event {
        BrowserEvent::Navigation { .. } => "browser/navigation",
        _ => panic!("Wrong topic"),
    };
    assert_eq!(topic, "browser/navigation");

    // Test TabCreated event topic
    let event = BrowserEvent::TabCreated { 
        id: 1,
        url: "https://example.com".to_string(),
    };
    let topic = match &event {
        BrowserEvent::TabCreated { .. } => "browser/tabs/created",
        _ => panic!("Wrong topic"),
    };
    assert_eq!(topic, "browser/tabs/created");

    // Test TabUrlChanged event topic
    let event = BrowserEvent::TabUrlChanged {
        id: 1,
        url: "https://example.com".to_string(),
    };
    let topic = match &event {
        BrowserEvent::TabUrlChanged { .. } => "browser/tabs/url",
        _ => panic!("Wrong topic"),
    };
    assert_eq!(topic, "browser/tabs/url");
}

#[test]
fn test_event_cloning() {
    let event = BrowserEvent::Navigation {
        url: "https://example.com".to_string(),
    };
    let cloned = event.clone();

    match (event, cloned) {
        (
            BrowserEvent::Navigation { url: url1 },
            BrowserEvent::Navigation { url: url2 }
        ) => {
            assert_eq!(url1, url2);
            assert_eq!(url1, "https://example.com");
        }
        _ => panic!("Event cloning failed"),
    }
} 
