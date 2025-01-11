pub const TAB_BAR_JS: &str = include_str!("tab_bar.js");
pub const TAB_BAR_HTML: &str = include_str!("tab_bar.html"); 
pub const WINDOW_CHROME_HTML: &str = include_str!("window_chrome.html");

// Add the JavaScript to the HTML
pub fn get_tab_bar_html() -> String {
    format!(
        r#"
        <!DOCTYPE html>
        <html>
        <head>
            <script type="text/javascript">
                {}
            </script>
            {}
        </head>
        <body>
            <div id="tab-bar">
                <div id="new-tab" onclick="createNewTab()">+</div>
            </div>
        </body>
        </html>
        "#,
        TAB_BAR_JS,
        TAB_BAR_HTML.split("<body>").next().unwrap_or("")
    )
} 

pub fn get_window_chrome() -> String {
    WINDOW_CHROME_HTML.to_string()
} 
