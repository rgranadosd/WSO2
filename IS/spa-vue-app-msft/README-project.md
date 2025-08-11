# WSO2 Project

This is a WSO2 project that includes the necessary directory structure for service development and deployment.

## Project Structure

```
WSO2/
├── IS/                                    # WSO2 Identity Server
│   └── spa-vue-app-msft/                 # Vue.js SPA Application for Microsoft
│       ├── LICENSE                        # Apache 2.0 License
│       ├── README.md                      # Application-specific documentation
│       ├── package.json                   # Node.js dependencies
│       ├── src/                           # Source code
│       ├── dist/                          # Build output
│       └── build.sh                       # Build script
├── .gitignore                             # Files ignored by Git
└── README.md                              # This file (project overview)
```

## Description

This project contains the configuration and structure necessary to work with WSO2 products, specifically the WSO2 Identity Server (IS) and a Vue.js Single Page Application configured for Microsoft authentication.

## Components

### WSO2 Identity Server (IS)
The IS directory contains WSO2 Identity Server configurations and related applications.

### Vue.js SPA Application (`IS/spa-vue-app-msft/`)
A modern Single Page Application built with Vue.js that integrates with WSO2 Identity Server for Microsoft authentication.

**Key Features:**
- Vue.js 3 with TypeScript
- WSO2 Identity Server integration
- Microsoft authentication support
- Modern build system with Webpack
- Responsive design

**For detailed information about the Vue.js application, see:**
- [Application README](IS/spa-vue-app-msft/README.md)
- [License Information](IS/spa-vue-app-msft/LICENSE)

## Requirements

- Java 8 or higher (for WSO2 Identity Server)
- Node.js 16+ (for Vue.js application)
- Maven 3.6+ or Gradle 6+
- Git

## Quick Start

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd WSO2
   ```

2. **Start the Vue.js application:**
   ```bash
   cd IS/spa-vue-app-msft
   npm install
   npm run dev
   ```

3. **For WSO2 Identity Server setup, refer to the specific documentation in the IS directory.**

## Configuration

Configuration files are located in the corresponding directories of each module. Make sure to review the specific documentation of each component.

## Contributing

1. Create a branch for your feature (`git checkout -b feature/new-feature`)
2. Make your changes
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## License

This project is under the Apache 2.0 License. See the [LICENSE](IS/spa-vue-app-msft/LICENSE) file in the Vue.js application directory for details.

## Contact

For more information about this project, consult the official WSO2 documentation or contact the development team.
