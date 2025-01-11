use std::collections::VecDeque;
use chrono::{DateTime, Local};
use crate::event::BrowserEvent;

const MAX_EVENTS: usize = 1000;

#[derive(Debug)]
pub struct EventEntry {
    pub timestamp: DateTime<Local>,
    pub event: BrowserEvent,
}

#[derive(Default)]
pub struct EventViewer {
    events: VecDeque<EventEntry>,
    max_events: usize,
}

impl EventViewer {
    pub fn new() -> Self {
        EventViewer {
            events: VecDeque::with_capacity(MAX_EVENTS),
            max_events: MAX_EVENTS,
        }
    }

    pub fn add_event(&mut self, event: BrowserEvent) {
        let entry = EventEntry {
            timestamp: Local::now(),
            event,
        };

        if self.events.len() >= MAX_EVENTS {
            self.events.pop_front();
        }
        self.events.push_back(entry);
    }

    pub fn get_events(&self) -> &VecDeque<EventEntry> {
        &self.events
    }

    pub fn clear(&mut self) {
        self.events.clear();
    }

    pub fn get_recent_events(&self, count: usize) -> Vec<&EventEntry> {
        self.events.iter().rev().take(count).collect()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_event_addition() {
        let mut viewer = EventViewer::new();
        let event = BrowserEvent::Navigation {
            url: "https://example.com".to_string(),
        };
        viewer.add_event(event);
        assert_eq!(viewer.events.len(), 1);
    }

    #[test]
    fn test_max_events() {
        let mut viewer = EventViewer::new();
        for i in 0..MAX_EVENTS + 10 {
            viewer.add_event(BrowserEvent::Navigation {
                url: format!("https://example{}.com", i),
            });
        }
        assert_eq!(viewer.events.len(), MAX_EVENTS);
    }
} 
