//! HTTP API server

use std::net::SocketAddr;
use axum::{
    routing::get,
    Router,
    Json,
};
use tracing::info;

pub async fn start_api_server() -> Result<(), Box<dyn std::error::Error>> {
    let app = Router::new()
        .route("/health", get(health_check));

    let addr = SocketAddr::from(([127, 0, 0, 1], 3003));
    info!("API server listening on {}", addr);

    axum::Server::bind(&addr)
        .serve(app.into_make_service())
        .await?;

    Ok(())
}

async fn health_check() -> Json<serde_json::Value> {
    Json(serde_json::json!({
        "status": "ok",
        "version": env!("CARGO_PKG_VERSION")
    }))
}
