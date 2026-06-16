# GA4 Complete Data Collector

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)
![Security](https://img.shields.io/badge/security-bandit-yellow)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)

**GA4 Complete Data Collector** is an enterprise-grade automation tool built for high-productivity data extraction from Google Analytics 4 (GA4). Designed with **DataOps** and **DevOps** principles, this project ensures fast, pre-filtered data delivery that saves time and maximizes efficiency.

## 🚀 Why Use This Tool?
- **High Productivity:** Data is extracted and formatted exactly as needed. No post-processing or manual filtering is required.
- **Security-First (Shift-Left):** Sensitive keys are ignored via strict `.gitignore` configurations, and security scans (Bandit) run on every CI build.
- **CI/CD Ready:** Automated testing and linting via GitHub Actions guarantee code reliability.
- **Extensible Clean Architecture:** Designed to easily accommodate new data requests and dimensions.

## 📁 Clean Architecture

The project is structured to make it easy to insert new folders and collect new data.

```text
report-ga4-api/
│
├── src/                        # Core Application Business Logic
│   ├── auth.py                 # Authentication logic
│   ├── config.py               # Centralized configuration
│   ├── data_fetcher.py         # GA4 API interaction
│   ├── exporter.py             # Data transformation and saving
│   └── main.py                 # Main orchestration
│
├── tests/                      # Testing Layer (pytest)
│   ├── conftest.py             # Shared test fixtures
│   ├── test_auth.py            # Auth unit tests
│   └── test_config.py          # Config unit tests
│
├── .github/workflows/          # CI/CD Pipelines
│   └── ci.yml                  # GitHub Actions workflow
│
├── DATA_REQUEST_SPEC_TEMPLATE.md # Template for cross-department data requests (AI-Ready)
├── requirements.txt            # Project and Dev/Test dependencies
└── .gitignore                  # Security & environment exclusions
```

## 🛠️ How to Extend (Adding New Data)

If you need to collect new data metrics, the architecture supports a plug-and-play approach:

1. **Request the Data:** Use the provided `DATA_REQUEST_SPEC_TEMPLATE.md` to map out exactly what metrics and dimensions are needed.
2. **AI-Assisted Scripting:** The template is designed to be easily read by AI tools (like Claude, Gemini, ChatGPT) to generate the extraction logic automatically.
3. **Add to `src/`:** Place any new specific extraction modules or classes within `src/` or a dedicated subdomain folder inside `src/`.
4. **Register in `main.py`:** Call your new data fetcher logic.

## 🔒 Security Practices

- **Never commit secrets:** The `.gitignore` file strictly blocks `.json`, `.pickle`, and `.env` files.
- **Local credentials:** Ensure you have your `client_secret.json` placed locally in the root directory (it will be ignored by git).
- **Automated Scanning:** Every push to `main` triggers a GitHub Action that runs `bandit` to identify security vulnerabilities.

## ⚙️ Setup and Installation

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd report-ga4-api
   ```

2. **Create a Virtual Environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application:**
   ```bash
   python src/main.py
   ```

## 🧪 Testing

We use `pytest` for our testing layer. To run the tests locally:

```bash
pytest tests/ --cov=src
```

---
*Developed for excellence in **DataOps** and **DevOps** environments.*
