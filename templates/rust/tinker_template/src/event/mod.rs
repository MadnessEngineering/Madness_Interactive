//! MQTT event system

use rumqttc::{Client, MqttOptions, QoS};
use serde::{Deserialize, Serialize};
use tracing::{info, error, debug};
use std::time::Duration;
use url::Url;
use serde_json::json;
use std::sync::mpsc::Sender;
use std::env;

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum BrowserCommand {
    Navigate { url: String },
    CreateTab { url: String },
    CloseTab { id: usize },
    SwitchTab { id: usize },
    RecordEvent { event: BrowserEvent },
    PlayEvent { event: BrowserEvent },
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum BrowserEvent {
    Navigation { url: String },
    PageLoaded { url: String },
    TitleChanged { title: String },
    TabCreated { id: usize, url: String },
    TabClosed { id: usize },
    TabActivated { id: usize },
    TabUrlChanged { id: usize, url: String },
    TabTitleChanged { id: usize, title: String },
    Error { message: String },
    CommandReceived { command: String },
    CommandExecuted { command: String, success: bool },
}

pub struct EventSystem {
    pub client: Option<Client>,
    pub options: MqttOptions,
    pub broker_url: String,
    client_id: String,
    command_sender: Option<Sender<BrowserCommand>>,
    last_reconnect_attempt: Option<std::time::Instant>,
}

impl EventSystem {
    pub fn new(broker_url: &str, client_id: &str) -> Self {
        info!("Creating new event system with broker: {}", broker_url);

        // Use environment variables or fallback to provided values
        let default_port = env::var("DEFAULT_BROKER_PORT")
            .unwrap_or_else(|_| "3003".to_string())
            .parse::<u16>()
            .unwrap_or(3003);

        let default_broker = env::var("DEFAULT_BROKER_URL")
            .unwrap_or_else(|_| "localhost".to_string());

        // Ensure URL has mqtt:// scheme
        let broker_url = if !broker_url.starts_with("mqtt://") {
            format!("mqtt://{}", broker_url)
        } else {
            broker_url.to_string()
        };

        // Parse the MQTT URL
        let url = match Url::parse(&broker_url) {
            Ok(url) => url,
            Err(e) => {
                error!("Failed to parse broker URL: {}", e);
                // Default to environment variable if URL is invalid
                Url::parse(&default_broker).unwrap_or_else(|_| {
                    Url::parse(&format!("mqtt://localhost:{}", default_port)).unwrap()
                })
            }
        };

        let host = url.host_str().unwrap_or("localhost");
        let port = url.port().unwrap_or(default_port);

        debug!("MQTT configuration - host: {}, port: {}", host, port);

        let mut options = MqttOptions::new(client_id, host, port);
        options.set_keep_alive(Duration::from_secs(5));
        options.set_clean_session(true);

        Self {
            client: None,
            options,
            broker_url: broker_url.to_string(),
            client_id: client_id.to_string(),
            command_sender: None,
            last_reconnect_attempt: None,
        }
    }

    pub fn connect(&mut self) -> Result<(), Box<dyn std::error::Error>> {
        debug!("Connecting to MQTT broker at {}", self.broker_url);
        let (client, mut connection) = Client::new(self.options.clone(), 10);

        // Store client first so we can publish the connection message
        self.client = Some(client);

        // Subscribe to command topic
        if let Some(ref mut client) = self.client {
            client.subscribe("browser/command", QoS::AtLeastOnce)?;
        }

        // Publish connection status
        let status = json!({
            "status": "connected",
            "client_id": self.options.client_id(),
            "timestamp": chrono::Utc::now().to_rfc3339(),
            "broker": self.broker_url
        });
        if let Some(ref mut client) = self.client {
            debug!("Publishing connection status");
            client.publish(
                "browser/connection",
                QoS::AtLeastOnce,
                false,
                serde_json::to_string(&status)?.as_bytes(),
            )?;
        }

        // Clone necessary fields for the event loop
        let mut event_system = self.clone();

        // Spawn a thread to handle incoming messages
        std::thread::spawn(move || {
            debug!("Starting MQTT event loop");
            for notification in connection.iter() {
                match notification {
                    Ok(rumqttc::Event::Incoming(rumqttc::Packet::Publish(msg))) => {
                        if let Err(e) = event_system.handle_incoming_message(&msg.topic, &msg.payload) {
                            error!("Failed to handle incoming message: {}", e);
                        }
                    }
                    Ok(event) => debug!("Received MQTT event: {:?}", event),
                    Err(e) => error!("MQTT error: {:?}", e),
                }
            }
        });

        Ok(())
    }

    fn try_reconnect(&mut self) -> bool {
        const RECONNECT_DELAY: Duration = Duration::from_secs(3);
        
        // Check if enough time has passed since last attempt
        if let Some(last_attempt) = self.last_reconnect_attempt {
            if last_attempt.elapsed() < RECONNECT_DELAY {
                return false;
            }
        }

        // Update last attempt time
        self.last_reconnect_attempt = Some(std::time::Instant::now());

        // Attempt reconnection
        match self.connect() {
            Ok(_) => {
                info!("Successfully reconnected to MQTT broker");
                true
            }
            Err(e) => {
                error!("Failed to reconnect to MQTT broker: {}. Will retry in {:?}", e, RECONNECT_DELAY);
                false
            }
        }
    }

    pub fn publish(&mut self, event: BrowserEvent) -> Result<(), Box<dyn std::error::Error>> {
        // If we're in test mode, just log and return success
        if cfg!(test) {
            debug!("Event published (test mode): {:?}", event);
            return Ok(());
        }

        // If no client, try to reconnect
        if self.client.is_none() && !self.try_reconnect() {
            debug!("Event not published (no broker connection): {:?}", event);
            return Ok(());
        }

        let topic = self.get_topic(&event);
        let payload = serde_json::to_string(&event)?;

        if let Some(ref mut client) = self.client {
            debug!("Publishing event to {}: {}", topic, payload);
            match client.publish(topic, QoS::AtLeastOnce, false, payload.as_bytes()) {
                Ok(_) => Ok(()),
                Err(e) => {
                    error!("Failed to publish event: {}. Will retry connection later.", e);
                    self.client = None;
                    Ok(())
                }
            }
        } else {
            debug!("Event not published (no broker): {:?}", event);
            Ok(())
        }
    }

    pub fn subscribe(&mut self, topic: &str) -> Result<(), Box<dyn std::error::Error>> {
        if let Some(ref mut client) = self.client {
            debug!("Subscribing to topic: {}", topic);
            client.subscribe(topic, QoS::AtLeastOnce)?;
            Ok(())
        } else {
            error!("Cannot subscribe: MQTT client not connected");
            Err("MQTT client not connected".into())
        }
    }

    pub fn set_command_sender(&mut self, sender: Sender<BrowserCommand>) {
        self.command_sender = Some(sender);
    }

    pub fn get_topic(&self, event: &BrowserEvent) -> &'static str {
        match event {
            BrowserEvent::Navigation { .. } => "browser/navigation",
            BrowserEvent::PageLoaded { .. } => "browser/page/loaded",
            BrowserEvent::TitleChanged { .. } => "browser/page/title",
            BrowserEvent::TabCreated { .. } => "browser/tabs/created",
            BrowserEvent::TabClosed { .. } => "browser/tabs/closed",
            BrowserEvent::TabActivated { .. } => "browser/tabs/activated",
            BrowserEvent::TabUrlChanged { .. } => "browser/tabs/url",
            BrowserEvent::TabTitleChanged { .. } => "browser/tabs/title",
            BrowserEvent::Error { .. } => "browser/error",
            BrowserEvent::CommandReceived { .. } => "browser/command/received",
            BrowserEvent::CommandExecuted { .. } => "browser/command/executed",
        }
    }

    fn handle_incoming_message(&mut self, topic: &str, payload: &[u8]) -> Result<(), Box<dyn std::error::Error>> {
        match topic {
            "browser/command" => {
                let command_str = String::from_utf8_lossy(payload);
                // Log that we received a command
                self.publish(BrowserEvent::CommandReceived {
                    command: command_str.to_string(),
                })?;

                // Parse and handle the command
                if let Ok(command) = serde_json::from_str::<BrowserCommand>(&command_str) {
                    if let Some(sender) = &self.command_sender {
                        match sender.send(command) {
                            Ok(_) => {
                                self.publish(BrowserEvent::CommandExecuted {
                                    command: command_str.to_string(),
                                    success: true,
                                })?;
                            }
                            Err(e) => {
                                self.publish(BrowserEvent::Error {
                                    message: format!("Failed to send command: {}", e),
                                })?;
                                self.publish(BrowserEvent::CommandExecuted {
                                    command: command_str.to_string(),
                                    success: false,
                                })?;
                            }
                        }
                    }
                } else {
                    self.publish(BrowserEvent::Error {
                        message: format!("Invalid command format: {}", command_str),
                    })?;
                    self.publish(BrowserEvent::CommandExecuted {
                        command: command_str.to_string(),
                        success: false,
                    })?;
                }
            }
            _ => debug!("Received message on unhandled topic: {}", topic),
        }
        Ok(())
    }

    pub fn get_command_sender(&self) -> Option<Sender<BrowserCommand>> {
        self.command_sender.clone()
    }
}

// Add Clone implementation for EventSystem
impl Clone for EventSystem {
    fn clone(&self) -> Self {
        Self {
            client: None, // New connection will be created in event loop
            options: self.options.clone(),
            broker_url: self.broker_url.clone(),
            client_id: self.client_id.clone(),
            command_sender: self.command_sender.clone(),
            last_reconnect_attempt: self.last_reconnect_attempt.clone(),
        }
    }
}
