# MAIRA-∞ Project Documentation

A revolutionary desktop AI assistant with voice-reactive avatar, multi-LLM support, and comprehensive system integration capabilities.

## Quick Start

### Installation
```bash
# Clone the repository
.gitclone https://github.com/your-org/maira-infinity.git
cd maira-infinity

# Install dependencies
pip install -r requirements.txt

# Run MAIRA
python run_maira.py
# or
maira
```

### Basic Usage
- **Voice Input**: Click the microphone button or press `Ctrl+Space` to start voice input
- **Voice Commands**: Speak in English or Hinglish (Hindi-English mix)
- **Manual Input**: Use the chat interface for text-based interaction

### Configuration
Create `~/.maira/config.toml`:

```toml
[llm.keys]
anthropic = "sk-ant-your-key-here"
openai = "sk-your-openai-key"
google = "AI-your-google-key"

[voice]
stt_model = "small"
tts_voice = "en-IN-NeerjaNeural"

[tools]
search_api_key = "your-brave-key-here"  # Optional
```

## Key Features

### 🚀 Voice Interaction
- Real-time speech-to-text with English + Hinglish support
- Text-to-speech with multiple voice options
- Voice activity detection with intelligent silence handling
- Animated avatar with real-time lip-sync

### 🧠 Multi-LLM Support
- Claude, OpenAI, Google, and Ollama integration
- Automatic fallback between providers
- Tool-aware LLM routing
- Local Ollama support for offline usage

### 🎨 Voice-Reactive Avatar
- Real-time lip-sync based on speech
- Emotional states (idle, listening, thinking, speaking)
- Smooth animations and transitions
- Hinglish language support

### ⚡ Intelligent Tools
- Web search with Brave API integration
- Code execution (Python, shell commands)
- File system access (configurable permissions)
- System monitoring and control
- Learning mode with capability management

### 📊 System Dashboard
- Real-time system monitoring (CPU, memory, GPU)
- Network statistics and process monitoring
- Session management
- Activity logs and history
- Quick access tools

### 🔐 Permission System
- Risk-based tool permissions
- User confirmation for destructive actions
- Configurable capabilities
- Secure API key storage

## Architecture

### Core Systems
- **Event Bus**: Type-safe publish/subscribe communication
- **Conversation Orchestrator**: Manages LLM interactions and tool calls
- **Permission Gate**: Controls tool access based on risk levels
- **LLMRouter**: Routes requests across multiple providers
- **Voice Engine**: Handles STT/TTS with Hinglish support
- **Tool Registry**: Manages available capabilities

### UI Layer
- **Qt + QML**: Reactive user interface
- **ViewModels**: Bridge between QML and business logic
- **Components**: Modular UI elements

### Data Layer
- **SQLite Database**: Persistent conversation storage
- **Configuration System**: TOML-based settings
- **Session Management**: Active session tracking

## Technical Details

### Dependencies

Required:
```toml
PySide6>=6.7.0
qasync>=0.27.0
httpx>=0.24.0
pydantic>=2.0.0
anthropic>=0.25.0
openai>=1.30.0
google-generativeai>=0.5.0
ollama>=0.2.0
faster-whisper>=1.0.0
sounddevice>=0.4.6
numpy>=1.24.0
edge-tts>=6.1.0
psutil>=5.9.0
pynvml>=11.4.0
keyring>=24.0.0
sqlalchemy>=2.0.0
aiosqlite>=0.19.0
tomli-w>=1.0.0
playwright>=1.40.0
astral>=3.2.0
Pillow>=10.0.0
aiofiles>=23.0.0
```

Development:
```toml
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-qt>=4.2.0
ruff>=0.1.0
mypy>=1.5.0
black>=23.0.0
```

### File Structure

```
maira-infinity/
├── maira/
│   ├── __init__.py              # Package metadata
│   ├── __main__.py              # CLI entry point
│   ├── app.py                   # Qt application bootstrap
│   ├── startup.py               # Core system initialization
│   ├── core/                    # Core systems
│   │   ├── event_bus.py         # Event system
│   │   ├── orchestrator.py      # Conversation management
│   │   ├── permissions.py       # Security layer
│   │   └── session_manager.py   # Session tracking
│   ├── llm/                      # LLM integration
│   │   ├── router.py            # Multi-provider routing
│   │   ├── providers/           # Individual providers
│   │   └── base.py              # LLM interface
│   ├── voice/                    # Voice processing
│   │   ├── capture.py           # Audio capture
│   │   ├── stt.py               # Speech-to-text
│   │   └── tts.py               # Text-to-speech
│   ├── tools/                    # Tool system
│   │   ├── registry.py          # Tool management
│   │   ├── base.py              # Tool interfaces
│   │   └── web_search.py        # Web search tool
│   ├── infra/                    # Infrastructure
│   │   ├── config.py            # Configuration
│   │   └── db.py                # Database
│   └── ui/                       # UI components
│       ├── viewmodels/           # QML viewmodels
│       └── qml/                  # QML interface files
├── run_maira.py                  # Quick start script
├── pyproject.toml               # Project configuration
└── README.md                     # Project overview
```

## Development

### Commands

**Run MAIRA:**
```bash
maira                    # Start normally
maira --dev             # Development mode
maira --debug           # Debug logging
maira --offline         # Offline mode (local LLM only)
```

**Code Quality:**
```bash
# Format code
black maira/

# Linting
ruff check maira/

# Type checking
mypy maira/

# Run tests
pytest tests/
```

### Database Schema

**Conversations Table:**
```sql
CREATE TABLE conversations (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    module TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Messages Table:**
```sql
CREATE TABLE messages (
    id TEXT PRIMARY KEY,
    conversation_id TEXT,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    tool_calls_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);
```

**Permissions Table:**
```sql
CREATE TABLE permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tool_name TEXT NOT NULL,
    scope TEXT DEFAULT 'general',
    tier TEXT NOT NULL,
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Troubleshooting

### Common Issues

#### "Application startup failed"
- **Solution**: Check that all dependencies are installed correctly
- **Verify**: `pip install -r requirements.txt`
- **Check**: Dependencies: PySide6, httpx, sounddevice, numpy, edge-tts

#### "Ollama not available"
- **Solution**: Install and start Ollama
- **Download**: https://ollama.ai/
- **Run**: `ollama serve`
- **Test**: `curl http://localhost:11434/api/tags`

#### Voice Input Not Working
- **Solution**: Check microphone permissions and hardware
- **Test**: Check system audio settings
- **Verify**: sounddevice installation

### Debug Mode
Run with `--debug` flag for detailed logging:
```bash
maira --debug
```

Log files are stored in `~/.maira/logs/maira.log`

## Performance Optimization

### Caching
- Conversation history is cached in memory for faster access
- Tool schemas are cached in the tool registry
- Permission checks use database caching

### Streaming
- LLM responses are streamed for better UX
- Audio processing uses efficient chunking
- Event bus handles concurrent operations

### Resource Management
- Automatic cleanup of inactive sessions
- Graceful shutdown of all subsystems
- Memory-efficient audio processing

## Security Considerations

### Permission System
- Tools have risk levels (LOW, MEDIUM, HIGH)
- User confirmation required for high-risk operations
- Configurable per-tool permissions

### API Key Storage
- Keys stored in `~/.maira/config.toml`
- Environment variables can override config file
- No keys hardcoded in source code

### Network Security
- HTTPS required for API calls
- API keys are stored encrypted when possible
- Network requests use timeouts and error handling

## Testing

### Unit Tests
- Test core systems (EventBus, PermissionGate)
- Test LLM providers and routing
- Test voice processing components
- Test tool registry and execution

### Integration Tests
- Test full conversation flow
- Test voice interaction end-to-end
- Test multi-provider fallback
- Test UI-QML integration

### Test Commands
```bash
pytest tests/ -v
pytest tests/unit/ -v
pytest tests/integration/ -v
```

## Contributing

### Code Standards
- Use black for formatting
- Follow PEP 8 style guide
- Add type hints for new code
- Write comprehensive docstrings

### Pull Request Process
1. Fork the repository
2. Create feature branch
3. Commit changes with descriptive messages
4. Run all tests
5. Update documentation if needed
6. Submit pull request

### Code Reviews
- All PRs require at least one approval
- Focus on code quality, security, and performance
- Consider backward compatibility

## Updates and Maintenance

### Version Management
- Semantic versioning (MAJOR.MINOR.PATCH)
- Breaking changes documented in changelog
- Dependency updates tested regularly

### Regular Maintenance
- Update dependencies quarterly
- Run security audits
- Monitor system performance
- Update documentation

## Support

### Troubleshooting
- Check log files for error details
- Verify system requirements
- Test components individually
- Use debug mode for detailed output

### Community
- GitHub issues for bug reports
- Discussion forums for general questions
- Documentation for API references

## License

MIT License. See LICENSE file for details.

## Acknowledgements

Special thanks to:
- Open source contributors
- Qt and PySide6 teams
- Faster-Whisper and Edge-TTS teams
- All beta testers and early adopters

---

*Version 12.7.3*  
*Last updated: 2026-10-06*  
*MAIRA Team*