# Data Quality Validator

A web-based data quality validation tool designed for financial planning and analysis (FP&A) professionals working with Vena Solutions.

## Overview

This application validates CSV exports from QuickBooks before uploading to Vena, identifying data quality issues that could cause import failures or data integrity problems.

## Features

- Header structure validation
- Transaction ID integrity checks
- Item field formatting verification
- Account separator validation
- Date field validation
- Amount field validation
- Detailed error reporting with actionable feedback
- Downloadable HTML reports

## Use Case

Organizations using Vena Solutions for financial consolidation often experience data upload failures due to formatting inconsistencies in source system exports. This tool pre-validates data files, reducing upload errors and saving time in the month-end close process.

## Requirements

- Python 3.8 or higher
- Streamlit 1.28.0+
- Pandas 2.0.0+

## Installation

### Local Development

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/data-quality-validator.git
cd data-quality-validator

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run streamlit_quality_checker.py
```

The application will open in your default browser at `http://localhost:8501`

### Cloud Deployment

This application is designed for deployment on Streamlit Cloud:

1. Fork or clone this repository to your GitHub account
2. Sign up for Streamlit Cloud at https://share.streamlit.io
3. Connect your GitHub repository
4. Deploy with one click

## Usage

1. Open the application in your browser
2. Upload your QuickBooks CSV export file
3. Click "Run Quality Check"
4. Review validation results
5. Download the HTML report for documentation
6. Address any critical errors before uploading to Vena

## Validation Checks

The tool performs the following validations:

- **Header Validation**: Verifies all 26 expected field headers are present in the correct order with proper underscore prefix
- **Transaction ID Field**: Confirms all transaction IDs are whole numbers
- **Item Field**: Validates colon placement and special character handling
- **Account Field**: Checks for middle dot separator compliance
- **Date Fields**: Validates format for _Date and _Ship Date columns
- **Amount Fields**: Ensures numeric formatting for _Debit, _Credit, and _Amount columns

## Output

The tool provides:

- Real-time validation results in the web interface
- Color-coded status indicators (green for pass, red for errors, yellow for warnings)
- Detailed error tables showing specific items requiring correction
- Optional formatting improvement suggestions
- Downloadable HTML reports for audit trail documentation

## Technical Details

Built with:
- Python 3.x
- Streamlit (web framework)
- Pandas (data processing)
- HTML/CSS (report generation)

## Support

For questions or issues, please open an issue in the GitHub repository.

## License

© 2025 Deodata Analytics. All rights reserved.

## About

Developed by Deodata, specialists in FP&A automation and Vena Solutions implementation.

