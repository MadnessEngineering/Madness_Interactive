use std::fs::File;
use std::io::{self, BufWriter, BufReader};
use std::time::{Duration, Instant};
use serde::{Serialize, Deserialize};
use crate::event::BrowserEvent;
use tracing::{debug, error};

#[derive(Serialize, Deserialize)]
struct EventRecord {
    timestamp_ms: u64,
    event: BrowserEvent,
}

#[derive(Default)]
pub struct EventRecorder {
    events: Vec<EventRecord>,
    start_time: Option<Instant>,
    save_path: Option<String>,
    is_recording: bool,
}

impl EventRecorder {
    pub fn start(&mut self) {
        self.start_time = Some(Instant::now());
        self.events.clear();
        self.is_recording = true;
        debug!("Started recording events");
    }

    pub fn stop(&mut self) {
        self.is_recording = false;
        debug!("Stopped recording events");
    }

    pub fn set_save_path(&mut self, path: String) {
        self.save_path = Some(path);
    }

    pub fn record_event(&mut self, event: BrowserEvent) {
        if self.is_recording {
            if let Some(start) = self.start_time {
                let elapsed = start.elapsed();
                self.events.push(EventRecord {
                    timestamp_ms: elapsed.as_millis() as u64,
                    event,
                });
                debug!("Recorded event at {:?}", elapsed);
            }
        }
    }

    pub fn save(&self, path: &str) -> io::Result<()> {
        let file = File::create(path)?;
        let writer = BufWriter::new(file);
        serde_json::to_writer(writer, &self.events)?;
        debug!("Saved {} events to {}", self.events.len(), path);
        Ok(())
    }
}

#[derive(Default)]
pub struct EventPlayer {
    events: Vec<EventRecord>,
    start_time: Option<Instant>,
    current_index: usize,
    speed: f32,
    is_playing: bool,
}

impl EventPlayer {
    pub fn load(&mut self, path: &str) -> io::Result<()> {
        let file = File::open(path)?;
        let reader = BufReader::new(file);
        self.events = serde_json::from_reader(reader)?;
        self.current_index = 0;
        debug!("Loaded {} events from {}", self.events.len(), path);
        Ok(())
    }

    pub fn start(&mut self) {
        self.start_time = Some(Instant::now());
        self.current_index = 0;
        self.is_playing = true;
        debug!("Started event playback");
    }

    pub fn stop(&mut self) {
        self.is_playing = false;
        debug!("Stopped event playback");
    }

    pub fn set_speed(&mut self, speed: f32) {
        self.speed = speed.max(0.1).min(10.0);
        debug!("Set playback speed to {}", speed);
    }

    pub fn next_event(&mut self) -> Option<BrowserEvent> {
        if !self.is_playing {
            return None;
        }

        if let Some(start) = self.start_time {
            if self.current_index < self.events.len() {
                let record = &self.events[self.current_index];
                let elapsed = start.elapsed();
                let target_time = Duration::from_millis(
                    (record.timestamp_ms as f32 / self.speed) as u64
                );

                if elapsed >= target_time {
                    self.current_index += 1;
                    debug!("Playing event at {:?}", elapsed);
                    return Some(record.event.clone());
                }
            } else {
                self.stop();
            }
        }
        None
    }

    pub fn play_event(&mut self, event: BrowserEvent) {
        if self.is_playing {
            if let Some(start) = self.start_time {
                let elapsed = start.elapsed();
                debug!("Playing event at {:?}: {:?}", elapsed, event);
            }
        }
    }
} 
