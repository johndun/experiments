# Project Architecture

## Overview

This repository (`experiments`) serves as a monorepo for various types of experiments, including web applications, Python packages, scripts, and more. The goal is to provide a structured but flexible environment for building, deploying, and sharing diverse projects, each isolated in its own directory, while leveraging common strategies for automation, documentation, and distribution.

## High-Level Architecture

- **Monorepo Structure:**
    Each experiment resides in a dedicated subfolder under the root. Experiments share the same repository but maintain independent dependencies, build processes, documentation, and distribution methods.
- **Deployment:**
    - **Web Applications:** Web-based experiments can be built and deployed as static sites under subpaths of the GitHub Pages site for this repo: `https://johndun.github.io/experiments/<experiment-folder>/`.
    - **Non-Web Experiments:** Non-web experiments (e.g., Python packages, scripts, CLI tools) are structured and distributed according to their specific needs (e.g., PyPI for Python packages, standalone scripts, or executables).
- **Routing:**
    Web experiments use appropriate routing configurations (`basename` or equivalent) for correct operation within their subpath.
- **CI/CD:**
    Automated GitHub Actions workflows handle building, testing, packaging, and deploying experiments, tailored to each experiment's specific requirements.

## Directory Structure

```bash
experiments/
├── .github/workflows/     # CI/CD configuration
├── docs/                  # Built static files for GitHub Pages (web deployment target)
└── experiments/
│   ├── task-tracker/      # Example web experiment (React app)
│   ├── data-processor/    # Example Python package experiment
│   └── .../               # Other experiments
└── memory-bank/
    ├── progress.md
    └── projectArchitecture.md
```

## Components

### 1. **Experiment Folders**

- Each experiment has its own directory under `/experiments`.
- Each contains necessary source code, dependencies, tests, documentation, and build configurations specific to the experiment type.
- Examples:
    - Web app: `/experiments/task-tracker`
    - Python package: `/experiments/data-processor`

### 2. **Deployment Artifacts**

- **Web Apps:** Built artifacts are output to `/docs/<experiment-name>` for GitHub Pages deployment.
- **Other Experiments:** Non-web experiments generate artifacts (e.g., wheels, executables, scripts) within their directories or under a shared `/dist` directory as needed.
- The root `/docs/index.html` acts as a landing page linking to web experiments; non-web experiments have clear documentation for accessing or distributing their artifacts.

### 3. **Routing and Hosting (Web Experiments Only)**

- Web apps configure `BrowserRouter`, `HashRouter`, or equivalent routers with the appropriate `basename`.
- Public paths are set correctly to ensure assets load from subpaths.

### 4. **Distribution (Non-Web Experiments)**

- Non-web experiments include clear instructions or automated workflows for distribution through platforms like PyPI, GitHub Releases, or direct script downloads.

### 5. **Shared Tooling**

- Root-level scripts and shared devDependencies are optionally managed for tasks like linting, formatting, testing, and packaging.

## Key Principles

- **Isolation:** Experiments are independent with no tight coupling.
- **Discoverability:** A root index or landing page links to web experiments; documentation clearly outlines distribution for non-web experiments.
- **Automation:** GitHub Actions manage builds, deploys, tests, packaging, and health checks, customized per experiment.
- **Reproducibility:** Each experiment provides clear instructions, dependencies, and build/run environments.
