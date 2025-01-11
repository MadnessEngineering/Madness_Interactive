use std::sync::Arc;
use url::Url;
use crate::browser::error::{NavigationError, BrowserResult};

/// Represents a parsed and validated URL with additional metadata
#[derive(Debug, Clone)]
pub struct ParsedUrl {
    url: Url,
    is_secure: bool,
    is_search: bool,
    original_input: String,
}

impl ParsedUrl {
    /// Create a new ParsedUrl from a string input
    pub fn new(input: &str) -> BrowserResult<Self> {
        // First, try to parse as-is
        let url = match Url::parse(input) {
            Ok(url) => url,
            Err(_) => {
                // If that fails, try adding https://
                if !input.starts_with("http://") && !input.starts_with("https://") {
                    match Url::parse(&format!("https://{}", input)) {
                        Ok(url) => url,
                        Err(_) => {
                            // If still fails, treat as search query
                            let search_url = format!(
                                "https://www.google.com/search?q={}",
                                urlencoding::encode(input)
                            );
                            Url::parse(&search_url)
                                .map_err(|e| NavigationError::InvalidUrl(e.to_string()))?
                        }
                    }
                } else {
                    return Err(NavigationError::InvalidUrl(format!("Invalid URL: {}", input)).into());
                }
            }
        };

        Ok(Self {
            is_secure: url.scheme() == "https",
            is_search: url.host_str() == Some("www.google.com") && url.path() == "/search",
            original_input: input.to_string(),
            url,
        })
    }

    /// Get the final URL
    pub fn url(&self) -> &Url {
        &self.url
    }

    /// Get the original input
    pub fn original_input(&self) -> &str {
        &self.original_input
    }

    /// Check if the URL is secure (https)
    pub fn is_secure(&self) -> bool {
        self.is_secure
    }

    /// Check if this is a search query
    pub fn is_search(&self) -> bool {
        self.is_search
    }

    /// Get the display URL (with appropriate formatting)
    pub fn display_url(&self) -> String {
        if self.is_search {
            format!("🔍 {}", self.original_input)
        } else {
            self.url.to_string()
        }
    }
}

/// Manages URL parsing and validation
#[derive(Clone)]
pub struct UrlManager {
    search_engine: Arc<String>,
}

impl UrlManager {
    pub fn new() -> Self {
        Self {
            search_engine: Arc::new("https://www.google.com/search?q=".to_string()),
        }
    }

    /// Set a custom search engine URL
    pub fn set_search_engine(&mut self, url: String) -> BrowserResult<()> {
        // Validate the search engine URL
        if !url.contains("{}") {
            return Err(NavigationError::InvalidUrl(
                "Search engine URL must contain {} placeholder for query".to_string()
            ).into());
        }

        // Test the URL with a dummy query
        let test_url = url.replace("{}", "test");
        Url::parse(&test_url)
            .map_err(|e| NavigationError::InvalidUrl(format!("Invalid search engine URL: {}", e)))?;

        self.search_engine = Arc::new(url);
        Ok(())
    }

    /// Parse and validate a URL or search query
    pub fn parse_input(&self, input: &str) -> BrowserResult<ParsedUrl> {
        ParsedUrl::new(input)
    }

    /// Convert a string to a search URL if needed
    pub fn to_search_url(&self, query: &str) -> String {
        self.search_engine
            .replace("{}", &urlencoding::encode(query))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_valid_url_parsing() {
        let url = ParsedUrl::new("https://example.com").unwrap();
        assert!(url.is_secure());
        assert!(!url.is_search());
        assert_eq!(url.original_input(), "https://example.com");
    }

    #[test]
    fn test_url_without_scheme() {
        let url = ParsedUrl::new("example.com").unwrap();
        assert!(url.is_secure());
        assert!(!url.is_search());
        assert_eq!(url.url().scheme(), "https");
    }

    #[test]
    fn test_search_query() {
        let url = ParsedUrl::new("rust programming").unwrap();
        assert!(url.is_secure());
        assert!(url.is_search());
        assert_eq!(url.original_input(), "rust programming");
        assert!(url.display_url().starts_with("🔍"));
    }

    #[test]
    fn test_invalid_url() {
        let result = ParsedUrl::new("http:invalid");
        assert!(result.is_err());
    }

    #[test]
    fn test_custom_search_engine() {
        let mut manager = UrlManager::new();
        
        // Valid search engine URL
        assert!(manager.set_search_engine("https://duckduckgo.com/?q={}".to_string()).is_ok());
        
        // Invalid search engine URL (missing placeholder)
        assert!(manager.set_search_engine("https://invalid.com".to_string()).is_err());
    }
} 
