use std::error::Error;

mod v8;
mod spidermonkey;
mod javascriptcore;

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum JsEngineType {
    V8,
    SpiderMonkey,
    JavaScriptCore,
}

pub trait JsEngine: Send + Sync {
    fn name(&self) -> &'static str;
    fn engine_type(&self) -> JsEngineType;
    fn evaluate(&self, script: &str) -> Result<String, Box<dyn Error>>;
    fn set_global(&self, name: &str, value: &str) -> Result<(), Box<dyn Error>>;
    fn get_global(&self, name: &str) -> Result<String, Box<dyn Error>>;
}

pub struct JsEngineManager {
    active_engine: Box<dyn JsEngine>,
    engine_type: JsEngineType,
}

impl JsEngineManager {
    pub fn new(engine_type: JsEngineType) -> Result<Self, Box<dyn Error>> {
        let active_engine: Box<dyn JsEngine> = match engine_type {
            JsEngineType::V8 => Box::new(v8::V8Engine::new()?),
            JsEngineType::SpiderMonkey => Box::new(spidermonkey::SpiderMonkeyEngine::new()?),
            JsEngineType::JavaScriptCore => Box::new(javascriptcore::JavaScriptCoreEngine::new()?),
        };

        Ok(Self {
            active_engine,
            engine_type,
        })
    }

    pub fn evaluate(&self, script: &str) -> Result<String, Box<dyn Error>> {
        self.active_engine.evaluate(script)
    }

    pub fn set_global(&self, name: &str, value: &str) -> Result<(), Box<dyn Error>> {
        self.active_engine.set_global(name, value)
    }

    pub fn get_global(&self, name: &str) -> Result<String, Box<dyn Error>> {
        self.active_engine.get_global(name)
    }

    pub fn engine_type(&self) -> JsEngineType {
        self.engine_type
    }
} 
