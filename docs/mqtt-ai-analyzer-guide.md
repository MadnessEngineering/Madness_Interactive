# MQTT AI Analyzer - Quick Start Guide 🧠

## What It Does

Intelligently analyzes high-volume MQTT streams using AI-powered pattern detection. Instead of reacting to every message (8000+ per cycle!), it buffers, categorizes, aggregates, and surfaces only actionable insights.

## Repository

**Private Submodule:** `projects/python/mqtt-ai-analyzer`  
**GitHub:** https://github.com/MadTinker/mqtt-ai-analyzer  
**PR:** https://github.com/MadnessEngineering/Madness_Interactive/pull/8

## Quick Start

### 1. Clone with Submodules

```bash
# If cloning fresh
git clone --recursive https://github.com/MadnessEngineering/Madness_Interactive.git

# If already cloned, update submodules
git submodule update --init --recursive
```

### 2. Install Dependencies

```bash
cd projects/python/mqtt-ai-analyzer
pip install -r requirements.txt
# Or install in editable mode
pip install -e .
```

### 3. Configure

Copy and edit `config.yaml`:

```yaml
mqtt:
  broker: "your-mqtt-broker-ip"
  port: 1883
  topics:
    - "DVTLab/#"
    - "DVT/#"
    - "status/#"

ollama:
  model: "qwen3-14b"
  api_url: "http://192.168.100.42:1234"  # LM Studio
  api_type: "auto"  # Auto-detects Ollama or OpenAI API
  timeout: 60

analysis:
  window_seconds: 30  # Batch messages for 30 seconds
  min_messages_for_ai: 10  # Only run AI if >= 10 messages
```

### 4. Start LM Studio (or Ollama)

**LM Studio:**
- Load model: qwen3-14b (or any model)
- Start server on port 1234
- Enable network access if needed

**Ollama:**
```bash
ollama serve
ollama pull qwen3-14b
```

### 5. Run the Analyzer

```bash
# Direct run
python -m mqtt_ai_analyzer

# Or if installed
mqtt-ai-analyzer

# Test with sample data (no MQTT needed)
python test_sample_data.py
```

## Example Output

```
📊 Analysis Window: 30s
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 Message Statistics:
  gateway_stats: 14 messages, 14 unique topics
  deployments: 12 messages, 3 unique topics, ⚠️ 2 errors
  processing_logs: 23 messages, 2 unique topics

🤖 AI Insights:
  ⚠️  ANOMALY: Gateway FC9077... showing 26% fewer sensors
  ❌ ALERT: 2 deployment failures on Inventorium branches
  ✅ NORMAL: Data processing stable at ~8600 datapoints/cycle
  📊 TREND: Deployment frequency increased 3x this week
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Architecture

```
MQTT Stream → MessageBuffer → Categorizer → Aggregator → AI Analyzer → Output
                ↓                                          ↓
           (time window)                           (insights only!)
```

### Components

1. **MessageBuffer** - Time-windowed collection (prevents AI thrashing)
2. **Categorizer** - Pattern-based topic grouping (wildcards supported)
3. **Aggregator** - Statistical analysis (counts, trends, errors)
4. **AIAnalyzer** - LM Studio/Ollama integration (auto-detection)
5. **MQTTListener** - paho-mqtt wrapper with reconnection
6. **OutputHandler** - Rich/JSON/plain output formats

## Configuration Tips

### Topic Patterns

```yaml
patterns:
  ignore:
    - "*/alive"  # Skip heartbeat pings
  
  aggregate:
    gateway_stats: "DVTLab/gateway-stats/*"
    logs: "DVT/*/log"
    deployments: "status/*/Inventorium/*"
  
  alert:  # Always analyze these
    - "*/error"
    - "*/FAILED"
```

### AI Backend Selection

The analyzer auto-detects:
- **LM Studio**: Uses OpenAI-compatible `/v1/chat/completions`
- **Ollama**: Uses native `/api/generate`

Override with `api_type: "openai"` or `api_type: "ollama"`

### Performance Tuning

```yaml
analysis:
  window_seconds: 30      # Longer = more context, less frequent
  min_messages_for_ai: 10 # Skip AI for low-volume windows
  max_buffer_size: 10000  # Safety limit
```

## Environment Variables

Create `.env`:

```bash
MQTT_BROKER=192.168.1.100
MQTT_PORT=1883
MQTT_USERNAME=optional
MQTT_PASSWORD=optional
```

## Use Cases

- **IoT Monitoring**: Gateway health, sensor connectivity
- **Deployment Tracking**: CI/CD status, failure detection
- **Log Analysis**: Error aggregation, pattern detection
- **Anomaly Detection**: Statistical outliers, unusual patterns

## Lessons Learned

1. **Time-windowed buffering is CRITICAL** for high-volume streams
2. **Don't call AI for every message** - batch and aggregate first
3. **Python > Rust** for rapid AI integration (vs Swarmonomicon attempt)
4. **LM Studio works great** for local inference
5. **Pattern matching beats regex** for MQTT topics

## Next Steps

- [ ] Deploy on production MQTT broker
- [ ] Add Prometheus metrics export
- [ ] Create systemd service
- [ ] Build alerting rules
- [ ] Add historical trend analysis

---

**Status:** ✅ Tested and working  
**AI Backend:** LM Studio (qwen3-14b)  
**Created:** October 2025  
**Author:** Madness Interactive

MWAHAHAHA! 🧪⚡

