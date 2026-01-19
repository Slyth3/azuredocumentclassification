# Document Processing System

An automated Azure-based document processing pipeline that leverages Azure Document Intelligence and OpenAI LLM for intelligent document classification and analysis.

## 📋 Overview

This project implements a serverless document processing system that:

1. **Ingests** PDF documents from Azure Blob Storage
2. **Extracts** content using Azure Document Intelligence (prebuilt-layout model)
3. **Classifies** documents using Azure OpenAI LLM (GPT-4)
4. **Publishes** results to Azure Event Hub for downstream consumption

The system is built as an Azure Function that automatically triggers on new document uploads, enabling a fully automated, scalable processing workflow.

## 🏗️ Architecture

### Components

- **Azure Functions** - Serverless compute for document processing orchestration
- **Azure Blob Storage** - Document ingestion and storage
- **Azure Document Intelligence** - OCR and document layout analysis
- **Azure OpenAI** - LLM-based document classification
- **Azure Event Hub** - Event streaming and results publishing

### Workflow

```
Document Upload → Blob Trigger → Document Intelligence → LLM Classification → Event Hub
     (Input)         (Function)       (Content Extraction)   (Document Type)     (Output)
```

## 📂 Project Structure

```
DocumentProcessingSystem/
├── function_app.py                 # Azure Function entry point with blob trigger
├── run_DocumentIntelligence.py     # Document Intelligence API integration
├── run_LLMClasscification.py       # Azure OpenAI classification logic
├── run_FabricEventHub.py           # Event Hub publisher
├── code_testing.ipynb              # Testing and development notebook
├── requirements.txt                # Python dependencies
├── host.json                       # Azure Functions configuration
├── local.settings.json             # Local environment settings
└── README.md                       # This file
```

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- Azure Functions Core Tools
- Azure CLI
- An Azure subscription with:
  - Storage Account (Blob Storage)
  - Document Intelligence resource
  - Azure OpenAI resource
  - Event Hub namespace

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd DocumentProcessingSystem
   ```

2. **Create a Python virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   
   Create or update `local.settings.json` with your Azure credentials:
   ```json
   {
     "IsEncrypted": false,
     "Values": {
       "AzureWebJobsStorage": "DefaultEndpointsProtocol=https;...",
       "Eventhub_endpoint": "your-eventhub-namespace.servicebus.windows.net",
       "Eventhub_name": "your-eventhub-name",
       "docintelligenceendpoint": "https://your-region.api.cognitive.microsoft.com/",
       "docintelligencekey": "your-document-intelligence-key",
       "openai_endpoint": "https://your-resource.openai.azure.com/",
       "openai_key": "your-openai-key",
       "rgdocumentprocessinb772_STORAGE": "your-blob-storage-connection-string"
     }
   }
   ```

### Local Development

1. **Start the Azure Functions runtime**
   ```bash
   func start
   ```

2. **Upload a test document**
   
   Upload a PDF to the `document-processing-dropzone/Input/` blob container

3. **Monitor execution**
   
   Check the function logs in the terminal for processing status

## 📝 Configuration

### Document Intelligence Settings

- **Model**: `prebuilt-layout` (for general document layout analysis)
- **API Version**: `2024-11-30`
- **Poll Interval**: 2 seconds (configurable in `function_app.py`)
- **Max Wait**: 60 seconds

### Document Classification Types

Supported document classifications (defined in `run_LLMClasscification.py`):
- Medical Aid / Medical Scheme Certificate
- Employee Tax Certificate
- Retirement Annuity Certificate
- Investment Income Certificate
- Medical Expenses
- Travel Log Book
- Other

### LLM Configuration

- **Model**: `gpt-4.1`
- **API Version**: `2024-12-01-preview`
- **Provider**: Azure OpenAI

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `azure-functions` | Azure Functions SDK |
| `azure-storage-blob` | Blob Storage integration |
| `azure-eventhub` | Event Hub integration |
| `azure-identity` | Azure authentication |
| `requests` | HTTP client for Document Intelligence API |
| `openai` | Azure OpenAI SDK |
| `cryptography` | Encryption utilities |

## 🔄 Processing Flow

### 1. Blob Trigger
- Monitors the `document-processing-dropzone/Input/` container
- Automatically triggers on PDF upload

### 2. Document Intelligence
- Converts PDF to base64 encoding
- Posts to Document Intelligence API for layout analysis
- Polls for completion (up to 60 seconds)
- Extracts structured content and metadata

### 3. LLM Classification
- Processes extracted text content
- Uses Azure OpenAI to classify document type
- Generates confidence scores and reasoning

### 4. Event Hub Publishing
- Packages results with document metadata
- Publishes to Event Hub for downstream processing
- Enables real-time data consumption and analytics

## 🧪 Testing

Use `code_testing.ipynb` for:
- Unit testing individual components
- Testing API endpoints
- Debugging extraction and classification logic
- Manual workflow validation

## ⚙️ Deployment

### Deploy to Azure

1. **Create Azure Functions resource**
   ```bash
   az functionapp create --resource-group <rg-name> \
     --consumption-plan-location <region> \
     --runtime python --runtime-version 3.11 \
     --functions-version 4 \
     --name <function-app-name>
   ```

2. **Deploy the function**
   ```bash
   func azure functionapp publish <function-app-name>
   ```

3. **Configure application settings**
   ```bash
   az functionapp config appsettings set \
     --name <function-app-name> \
     --resource-group <rg-name> \
     --settings <setting-key>=<setting-value>
   ```

## 📊 Monitoring & Logging

- Azure Functions integrated logging
- Document Intelligence API response tracking
- Event Hub message publishing verification
- Application Insights integration (optional)

## 🛠️ Known Limitations & Future Enhancements

### Current Limitations
- ✋ Embeddings for large documents not yet implemented
- ✋ Document Intelligence SDK migration in progress
- ✋ No chunking strategy for documents exceeding 2 MB item limits

### Planned Enhancements
- [ ] Implement document chunking for large files
- [ ] Add vector embeddings for semantic search
- [ ] Migrate to Document Intelligence Python SDK
- [ ] Add retry logic with exponential backoff
- [ ] Implement dead-letter handling for failed documents
- [ ] Add comprehensive error tracking and alerting

## 🔐 Security Considerations

- Use Azure Key Vault for sensitive credentials (recommended)
- Enable managed identities for Azure service authentication
- Restrict blob container access with appropriate RBAC
- Validate input documents before processing
- Monitor and audit Event Hub consumers

## 📝 Environment Variables Reference

| Variable | Description | Required |
|----------|-------------|----------|
| `Eventhub_endpoint` | Event Hub namespace endpoint | ✓ |
| `Eventhub_name` | Event Hub instance name | ✓ |
| `docintelligenceendpoint` | Document Intelligence API endpoint | ✓ |
| `docintelligencekey` | Document Intelligence API key | ✓ |
| `openai_endpoint` | Azure OpenAI API endpoint | ✓ |
| `openai_key` | Azure OpenAI API key | ✓ |
| `AzureWebJobsStorage` | Blob Storage connection string | ✓ |
| `rgdocumentprocessinb772_STORAGE` | Blob Storage connection for function trigger | ✓ |

## 🤝 Contributing

Contributions are welcome! Please:
1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## 📄 License

[Add your license here]

## 📞 Support

For issues or questions, please open an issue in the repository or contact the development team.

---

**Last Updated**: January 2026
