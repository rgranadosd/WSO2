# WSO2 Source Code Repository

This repository serves as a comprehensive collection of all source code related to WSO2 products and technologies. It contains a wide range of materials from demonstrations and small developments to video tutorials and proof-of-concept implementations.

## Repository Purpose

This repository is designed to be the central location for all WSO2-related source code, including:

- **Demos & Examples** - Working demonstrations of WSO2 capabilities
- **Small Developments** - Proof-of-concept implementations and utilities
- **Video Tutorials** - Source code accompanying video demonstrations
- **Integration Examples** - Code samples for various WSO2 integrations
- **Custom Extensions** - Tailored solutions and customizations
- **Learning Materials** - Educational code examples and tutorials

## Project Structure

```
WSO2/
├── IS/                                    # WSO2 Identity Server
│   └── spa-vue-app-msft/                 # Vue.js SPA Application for Microsoft
│       ├── README.md                      # Application-specific documentation
│       ├── LICENSE                        # Apache 2.0 License
│       ├── package.json                   # Node.js dependencies
│       ├── src/                           # Source code
│       ├── build.sh                       # Build script
│       └── start.sh                       # Start script
├── PoC_AI_Gateway/                        # AI Gateway Proof of Concept
│   ├── README.md                          # Project documentation
│   ├── package.json                       # Node.js dependencies
│   ├── config.yaml                        # Configuration file
│   ├── tesing.py                          # Streamlit application
│   ├── mcp-client.js                      # MCP client implementation
│   ├── mcp-http-proxy.js                  # HTTP proxy for MCP
│   ├── startgw.sh                         # Gateway start script
│   └── start_test.sh                      # Test start script
├── .gitignore                             # Files ignored by Git
└── README.md                              # This file (repository overview)
```

## Current Contents

### WSO2 Identity Server (IS)
- **Vue.js SPA Application** (`IS/spa-vue-app-msft/`)
  - Modern Single Page Application with Vue.js 3 and TypeScript
  - Integration with WSO2 Identity Server for Microsoft authentication
  - Complete authentication flow implementation
  - Production-ready build system with Webpack

### AI Gateway Proof of Concept (PoC_AI_Gateway)
- **Guardrails Testing Client** (`PoC_AI_Gateway/`)
  - Streamlit-based web interface for testing AI guardrails
  - Custom client designed specifically for guardrails validation
  - Support for multiple AI providers 

## Adding New WSO2 Projects

When adding new WSO2-related projects to this repository:

1. **Create a new directory** for your project under the appropriate WSO2 product folder
2. **Include proper documentation** (README.md) explaining the project purpose and setup
3. **Add license information** if different from the main Apache 2.0 license
4. **Update this main README.md** to include your new project in the structure
5. **Follow the established naming conventions** and directory structure

### Suggested Directory Structure for New Projects:
```
WSO2/
├── IS/                                    # Identity Server projects
├── APIM/                                  # API Manager projects
├── EI/                                    # Enterprise Integrator projects
├── ESB/                                   # Enterprise Service Bus projects
├── DSS/                                   # Data Services Server projects
├── CEP/                                   # Complex Event Processor projects
├── MB/                                    # Message Broker projects
├── AS/                                    # Application Server projects
├── BPS/                                   # Business Process Server projects
├── GREG/                                  # Governance Registry projects
├── DAS/                                   # Data Analytics Server projects
├── ML/                                    # Machine Learner projects
├── IOT/                                   # Internet of Things projects
├── DEMOS/                                 # General demonstration projects
├── TUTORIALS/                             # Learning and tutorial materials
└── VIDEOS/                                # Video tutorial source code
```

## Requirements

- **Java 8 or higher** (for WSO2 server components)
- **Node.js 16+** (for JavaScript/TypeScript applications)
- **Python 3.8+** (for AI Gateway and Streamlit applications)
- **Maven 3.6+ or Gradle 6+** (for Java-based projects)
- **Git** (for version control)

## Getting Started

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd WSO2
   ```

2. **Navigate to specific projects:**
   ```bash
   # For Vue.js application
   cd IS/spa-vue-app-msft
   
   # For AI Gateway application
   cd PoC_AI_Gateway
   
   # For other projects (when added)
   cd <PRODUCT>/<PROJECT_NAME>
   ```

3. **Follow project-specific setup instructions** in each project's README.md:
   - **Vue.js SPA**: See `IS/spa-vue-app-msft/README.md` for authentication setup
   - **AI Gateway**: See `PoC_AI_Gateway/README.md` for guardrails testing and LLM provider configuration

## Contributing

1. Create a branch for your new WSO2 project (`git checkout -b feature/new-wso2-project`)
2. Add your project with proper documentation
3. Update this main README.md to include your project
4. Commit your changes (`git commit -am 'Add new WSO2 project: Project Name'`)
5. Push to the branch (`git push origin feature/new-wso2-project`)
6. Create a Pull Request

## License

This repository is under the Apache 2.0 License. Individual projects may have their own licenses as specified in their respective directories.

## Contact

For more information about this repository or to contribute WSO2-related projects, please contact the development team or refer to the official WSO2 documentation.

---

**Note:** This repository is designed to grow organically as new WSO2 projects and demonstrations are developed. Each project should be self-contained with its own documentation and setup instructions.
