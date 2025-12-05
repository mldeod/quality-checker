# 🎯 Leinco Quality Checker

**Professional data quality validation for Vena Solutions**

Beautiful web-based tool to check QuickBooks CSV exports before uploading to Vena.

---

## ✨ Features

- ✅ **No Installation Required** - Runs in your browser
- ✅ **Beautiful Interface** - Apple-style design
- ✅ **6 Comprehensive Checks** - Headers, IDs, Items, Accounts, Dates, Amounts
- ✅ **Instant Results** - See issues immediately
- ✅ **Downloadable Reports** - Professional HTML reports
- ✅ **Works Everywhere** - Desktop, tablet, mobile

---

## 🚀 Try It Live

**[Open Quality Checker →](https://YOUR_APP_URL_HERE.streamlit.app)**

---

## 📖 How To Use

1. **Upload** your QuickBooks CSV file
2. **Click** "Run Quality Check"
3. **Review** the results
4. **Download** the HTML report
5. **Fix** any issues found
6. **Upload** to Vena with confidence!

---

## 🔍 What Gets Checked

### 1. Header Validation
- All 26 expected field headers present
- Correct order
- Proper underscore prefix

### 2. Transaction ID Field
- All IDs are whole numbers
- No missing or invalid IDs

### 3. Item Field Validation
- Correct colon placement
- Special character handling
- Blank field tracking

### 4. Account Field
- Middle dot separator present

### 5. Date-related Fields
- Valid date format
- Both _Date and _Ship Date

### 6. Amount-related Fields
- All numeric values
- Proper formatting

---

## 🛠️ Run Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run streamlit_quality_checker.py
```

Opens at `http://localhost:8501`

---

## 📊 Screenshots

![Quality Checker Interface](screenshot.png)
*Beautiful, intuitive interface*

---

## 💼 About

Built by **El Dúo Dinámico** 🦸‍♂️🐝

Professional FP&A consulting specialized in Vena Solutions implementation.

---

## 📄 License

© 2025 Deodata Analytics. All rights reserved.

---

## 🤝 Support

Questions or issues? Contact us!

**Created with ❤️ for better data quality**
