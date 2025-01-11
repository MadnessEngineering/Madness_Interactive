use std::path::PathBuf;

#[derive(Debug)]
pub struct Args {
    pub headless: bool,
    pub config: Option<PathBuf>,
}

impl Args {
    pub fn parse() -> Self {
        Self {
            headless: false,
            config: None,
        }
    }
} 
