# Setup Guide

## Prerequisites
- Python 3.9+
- Google Cloud SDK with BigQuery access
- Required Python packages (see requirements.txt)

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd sop-demand-inventory-tracker
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## Configuration

### Environment Variables
Set Google Cloud credentials:
```bash
export GOOGLE_APPLICATION_CREDENTIALS=your/path/to/credentials.json
```

### Data Setup
1. Place your CSV files in the `data/raw/` directory
2. Ensure file naming matches the expected format:
   - `final_orders_perfect_integrity.csv`
   - `final_products_perfect_integrity.csv`
   - `final_inventory_perfect_integrity.csv`
   - `final_forecasts_perfect_integrity.csv`

## Running the Project

### Jupyter Notebooks
1. Start Jupyter:
```bash
jupyter notebook
```

2. Open and run `notebooks/sop_models_comprehensive.ipynb`

### Python Scripts
```bash
python -m src.visualization
```

## Testing
Run the test suite:
```bash
python -m pytest tests/
```

## Code Quality
Format code with Black:
```bash
black src/ tests/
```

Check code quality with flake8:
```bash
flake8 src/ tests/
```

## Troubleshooting

### Common Issues
1. **Import Errors**: Ensure you're in the correct virtual environment
2. **Data Loading**: Verify file paths and CSV formats
3. **Authentication**: Check Google Cloud credentials setup

### Support
For issues and questions, please refer to the documentation or create an issue in the repository.
