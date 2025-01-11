use std::error::Error;
use super::{JsEngine, JsEngineType};

pub struct JavaScriptCoreEngine {
    // Placeholder for future implementation
}

impl JavaScriptCoreEngine {
    pub fn new() -> Result<Self, Box<dyn Error>> {
        Err("JavaScriptCore engine not yet implemented".into())
    }
}

impl JsEngine for JavaScriptCoreEngine {
    fn name(&self) -> &'static str {
        "JavaScriptCore"
    }

    fn engine_type(&self) -> JsEngineType {
        JsEngineType::JavaScriptCore
    }

    fn evaluate(&self, _script: &str) -> Result<String, Box<dyn Error>> {
        Err("JavaScriptCore engine not yet implemented".into())
    }

    fn set_global(&self, _name: &str, _value: &str) -> Result<(), Box<dyn Error>> {
        Err("JavaScriptCore engine not yet implemented".into())
    }

    fn get_global(&self, _name: &str) -> Result<String, Box<dyn Error>> {
        Err("JavaScriptCore engine not yet implemented".into())
    }
} 
