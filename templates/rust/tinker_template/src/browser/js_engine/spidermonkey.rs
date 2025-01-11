use std::error::Error;
use super::{JsEngine, JsEngineType};

pub struct SpiderMonkeyEngine {
    // Placeholder for future implementation
}

impl SpiderMonkeyEngine {
    pub fn new() -> Result<Self, Box<dyn Error>> {
        Err("SpiderMonkey engine not yet implemented".into())
    }
}

impl JsEngine for SpiderMonkeyEngine {
    fn name(&self) -> &'static str {
        "SpiderMonkey"
    }

    fn engine_type(&self) -> JsEngineType {
        JsEngineType::SpiderMonkey
    }

    fn evaluate(&self, _script: &str) -> Result<String, Box<dyn Error>> {
        Err("SpiderMonkey engine not yet implemented".into())
    }

    fn set_global(&self, _name: &str, _value: &str) -> Result<(), Box<dyn Error>> {
        Err("SpiderMonkey engine not yet implemented".into())
    }

    fn get_global(&self, _name: &str) -> Result<String, Box<dyn Error>> {
        Err("SpiderMonkey engine not yet implemented".into())
    }
} 
