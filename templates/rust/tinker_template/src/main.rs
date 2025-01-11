use clap::Parser;
use tracing::{debug, error, info};
use std::{sync::{Arc, Mutex}, env};

mod api;
mod browser;
mod event;
mod templates;

use crate::{
    browser::BrowserEngine,
    event::EventSystem,
};

#[derive(Parser, Debug)]
#[command(author, version, about = "A craftsperson's browser", long_about = None)]
struct Args {
    /// URL to load
    #[arg(short, long)]
    url: Option<String>,

    /// Run in headless mode
    #[arg(short = 'H', long)]
    headless: bool,

    /// Event broker URL
    #[arg(short, long)]
    broker_url: Option<String>,

    /// Number of tabs to open
    #[arg(long)]
    tabs: Option<usize>,

    /// Enable event recording
    #[arg(long)]
    record: bool,

    /// Path to save recorded events
    #[arg(long)]
    record_path: Option<String>,

    /// Path to replay events from
    #[arg(long)]
    replay: Option<String>,

    /// Speed multiplier for replay
    #[arg(long)]
    replay_speed: Option<f32>,

    /// Debug mode
    #[arg(long)]
    debug: bool,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Set default debug mode if not explicitly set in environment
    if env::var("DEBUG").is_err() {
        env::set_var("DEBUG", "TRUE");
    }

    // Initialize logging with more detailed format
    tracing_subscriber::fmt()
        .with_env_filter(tracing_subscriber::EnvFilter::from_default_env()
            .add_directive("tinker=debug".parse()?)
            .add_directive("wry=debug".parse()?))
        .with_file(true)
        .with_line_number(true)
        .with_thread_ids(true)
        .with_target(true)
        .init();

    info!("Starting Tinker Workshop...");

    // Parse command line arguments
    let args = Args::parse();

    // Initialize event system if broker URL is specified
    let events = if let Some(broker_url) = args.broker_url.as_ref() {
        let events = EventSystem::new(broker_url, "tinker-browser");
        Some(Arc::new(Mutex::new(events)))
    } else {
        None
    };

    // Create browser instance with default URL if none provided
    let mut browser = BrowserEngine::new(
        args.headless,
        events.clone(),
        args.url.or_else(|| Some("about:blank".to_string())),
    );

    // Connect to event system after browser is initialized
    if let Some(ref events) = events {
        if let Ok(mut events) = events.lock() {
            if let Err(e) = events.connect() {
                error!("Failed to connect to event broker: {}. Continuing without event system.", e);
            } else {
                // Subscribe to all browser events using wildcard
                if let Err(e) = events.subscribe("browser/#") {
                    error!("Failed to subscribe to events: {}. Continuing without event subscription.", e);
                } else {
                    info!("Connected to event broker and subscribed to events");
                }
            }
        }
    }

    // Start recording if enabled
    if args.record {
        if let Some(path) = args.record_path.as_deref() {
            browser.start_recording(path);
            info!("Recording will be saved to {}", path);
        } else {
            return Err("--record-path is required when --record is specified".into());
        }
    }

    // Start replay if enabled
    if let Some(path) = args.replay {
        if !std::path::Path::new(&path).exists() {
            error!("Replay file not found: {}", path);
            return Err("Replay file not found".into());
        }
        browser.load_recording(&path)?;
        if let Some(speed) = args.replay_speed {
            let _ = browser.set_replay_speed(speed);
        }
        let _ = browser.start_replay();
        info!("Replaying events from {}", path);
    }

    // Start event loop
    info!("Starting browser engine...");
    browser.run()?;

    Ok(())
}
