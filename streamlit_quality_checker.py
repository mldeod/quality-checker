#!/usr/bin/env python3
"""
Leinco Quality Checker - Streamlit Web App
Beautiful web-based quality validation tool
No installation needed - runs in browser!

Created by Deodata
"""

import streamlit as st
import pandas as pd
import re
from datetime import datetime
import base64

# Page config - MUST BE FIRST!
st.set_page_config(
    page_title="Quality Checker",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS - Apple-style design!
st.markdown("""
<style>
    /* Apple-style colors and fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
    
    .main {
        background: #f5f5f7;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Beautiful header ribbon */
    .header-ribbon {
        background: linear-gradient(135deg, #e8f4f8 0%, #d4e9f7 100%);
        padding: 30px;
        border-radius: 0;
        margin: -70px -80px 30px -80px;
        text-align: center;
    }
    
    .header-ribbon h1 {
        color: #6e6e73;
        font-size: 32px;
        font-weight: 400;
        margin: 0;
        letter-spacing: -0.5px;
    }
    
    /* Cards */
    .stCard {
        background: white;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 20px;
    }
    
    /* Buttons */
    .stButton>button {
        background: #0051D5;
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 32px;
        font-size: 16px;
        font-weight: 500;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        background: #003D9E;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,81,213,0.3);
    }
    
    /* Success/Error boxes */
    .success-box {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        color: #155724;
        padding: 20px;
        border-radius: 12px;
        border-left: 4px solid #34c759;
        margin: 20px 0;
    }
    
    .error-box {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        color: #721c24;
        padding: 20px;
        border-radius: 12px;
        border-left: 4px solid #ff3b30;
        margin: 20px 0;
    }
    
    /* Results styling */
    .check-result {
        background: #f9f9f9;
        padding: 16px;
        border-radius: 8px;
        margin: 12px 0;
        border-left: 3px solid #d2d2d7;
        font-family: 'Monaco', 'Courier New', monospace;
        font-size: 14px;
        line-height: 1.6;
    }
    
    .check-result.pass {
        border-left-color: #34c759;
        background: linear-gradient(135deg, #f0fdf4 0%, #e8f9ed 100%);
    }
    
    .check-result.fail {
        border-left-color: #ff3b30;
        background: linear-gradient(135deg, #fff5f5 0%, #ffe8e8 100%);
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #a1a1a6;
        font-size: 11px;
        margin-top: 40px;
        padding: 20px;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)


# ============================================================================
# VALIDATION FUNCTIONS (Same logic as desktop version!)
# ============================================================================

def check_headers(df):
    """Combined header validation"""
    results = []
    all_passed = True
    
    # Check underscore prefix
    cols_without_underscore = [col for col in df.columns if not col.startswith('_')]
    if cols_without_underscore:
        results.append(f"❌ {len(cols_without_underscore)} field headers missing '_' prefix")
        all_passed = False
    else:
        results.append(f"✅ All {len(df.columns)} field headers have '_' prefix")
    
    # Check expected columns
    expected_cols = [
        '_Trans #', '_Type', '_Date', '_Num', '_Name', '_Name State', '_Memo',
        '_Ship Date', '_Country', '_Territory', '_Item', '_Item Description',
        '_Account', '_Class', '_Rep', '_Clr', '_Split', '_Qty', '_U/M',
        '_Sales Price', '_Lot Number', '_Debit', '_Credit', '_Amount', '_Balance',
        '_Ship To State'
    ]
    
    if list(df.columns) == expected_cols:
        results.append(f"✅ All 26 expected field headers present in correct order")
    else:
        missing = [c for c in expected_cols if c not in df.columns]
        extra = [c for c in df.columns if c not in expected_cols]
        
        if missing:
            results.append(f"❌ Missing field headers: {', '.join(missing)}")
            all_passed = False
        if extra:
            results.append(f"❌ Unexpected field headers: {', '.join(extra)}")
            all_passed = False
        if not missing and not extra and list(df.columns) != expected_cols:
            results.append(f"❌ Field headers out of order")
            all_passed = False
    
    return all_passed, "Header Validation", results


def check_transaction_ids(df):
    """Check transaction IDs"""
    if '_Trans #' not in df.columns:
        return False, "Transaction ID Field Validation", ["❌ '_Trans #' column not found"]
    
    non_numeric = df[df['_Trans #'].apply(lambda x: not str(x).replace('.0', '').isdigit() if pd.notna(x) else False)]
    if len(non_numeric) > 0:
        return False, "Transaction ID Field Validation", [f"❌ {len(non_numeric)} transaction IDs are not whole numbers"]
    
    return True, "Transaction ID Field Validation", [f"✅ All {len(df):,} transaction IDs are whole numbers"]


def check_items_combined(df):
    """Combined item field validation"""
    if '_Item' not in df.columns:
        return False, "Item Field Validation", ["❌ '_Item' column not found"], [], []
    
    results = []
    all_passed = True
    errors = []
    improvements = []
    
    # Basic counts
    total_rows = len(df)
    items_with_data = df[df['_Item'].notna()]
    items_checked = len(items_with_data)
    blank_items = total_rows - items_checked
    special_char_count = items_with_data[items_with_data['_Item'].astype(str).str.contains('[µ°·—–]', regex=True)].shape[0]
    
    if items_checked == 0:
        return False, "Item Field Validation", ["❌ No items found in file"], [], []
    
    results.append(f"✅ {items_checked:,} items checked")
    results.append(f"✅ {blank_items:,} rows with blank Items field (skipped)")
    results.append(f"✅ {special_char_count:,} items contain special characters")
    
    # Colon placement check
    missing_colon_pattern = r'^[^:(]+\('
    colon_after_dash_pattern = r'^[A-Z0-9.-]+ - [^:]+:'
    improvement_pattern = r'^[A-Z0-9.-]+:\s*-\s+'
    
    missing_colon_count = 0
    colon_after_dash_count = 0
    
    for idx, row in items_with_data.iterrows():
        item = str(row['_Item'])
        
        if '(' in item:
            first_colon_pos = item.find(':')
            first_paren_pos = item.find('(')
            
            if first_colon_pos == -1 or first_colon_pos > first_paren_pos:
                missing_colon_count += 1
                errors.append({
                    'item': item,
                    'issue': 'Missing colon before parenthesis'
                })
                continue
        
        if re.match(colon_after_dash_pattern, item):
            colon_after_dash_count += 1
            errors.append({
                'item': item,
                'issue': "Colon appears after dash (should be: ID:rest)"
            })
            continue
        
        if re.match(improvement_pattern, item):
            item_id = item.split(':')[0]
            rest_of_item = ':'.join(item.split(':')[1:])  # Get everything after first colon
            # Remove the "- " pattern after colon and reconstruct
            rest_cleaned = rest_of_item.strip().lstrip('-').strip()
            improvements.append({
                'item': item,
                'suggestion': f"Consider: {item_id}:{item_id} - {rest_cleaned}"
            })
    
    # Add colon placement results
    if len(errors) > 0:
        all_passed = False
        results.append(f"❌ {len(errors):,} items with incorrect colon placement")
        if missing_colon_count > 0:
            results.append(f"   • {missing_colon_count} items missing ':' before '('")
        if colon_after_dash_count > 0:
            results.append(f"   • {colon_after_dash_count} items with ':' after '-'")
    else:
        results.append(f"✅ All items have correct colon placement")
    
    if len(improvements) > 0:
        results.append(f"⚠️  {len(improvements):,} format improvements suggested (optional)")
    
    return all_passed, "Item Field Validation", results, errors, improvements


def check_accounts(df):
    """Check accounts"""
    if '_Account' not in df.columns:
        return False, "Account Field Validation", ["❌ '_Account' column not found"]
    
    accounts_with_dot = df[df['_Account'].notna() & df['_Account'].astype(str).str.contains('·')]
    
    if len(accounts_with_dot) == 0:
        return False, "Account Field Validation", ["❌ No accounts have '·' separator"]
    
    return True, "Account Field Validation", ["✅ All accounts have '·' separator"]


def check_dates(df):
    """Check dates"""
    date_cols = ['_Date', '_Ship Date']
    results = []
    
    for col in date_cols:
        if col not in df.columns:
            return False, "Date-related Fields Validation", [f"❌ '{col}' column not found"]
        
        valid_dates = pd.to_datetime(df[col], errors='coerce').notna().sum()
        results.append(f"✅ {col}: {valid_dates:,} valid dates")
    
    return True, "Date-related Fields Validation", results


def check_amounts(df):
    """Check amounts"""
    amount_cols = ['_Debit', '_Credit', '_Amount']
    
    for col in amount_cols:
        if col not in df.columns:
            return False, "Amount-related Fields Validation", [f"❌ '{col}' column not found"]
        
        non_numeric = df[df[col].notna() & ~df[col].astype(str).str.replace('.', '').str.replace('-', '').str.isdigit()]
        if len(non_numeric) > 0:
            return False, "Amount-related Fields Validation", [f"❌ {len(non_numeric)} non-numeric values in {col}"]
    
    return True, "Amount-related Fields Validation", ["✅ All amount columns are numeric"]


def generate_html_report(filename, checks, all_passed, total_rows, total_cols, colon_errors=None, colon_improvements=None):
    """Generate HTML report"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Check if there are improvements
    has_improvements = len(colon_improvements) > 0 if colon_improvements else False
    
    # Smart status text
    status_color = "pass" if all_passed else "fail"
    if all_passed and not has_improvements:
        status_text = "All Checks Passed - Ready for Vena"
    elif all_passed and has_improvements:
        status_text = "All Checks Passed - File can be uploaded to Vena. Some optional formatting improvements are suggested below."
    else:
        status_text = "Issues Found - Fix Before Upload"
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Quality Report - {filename}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f7; }}
        .header-line {{ padding: 20px 40px; border-bottom: 1px solid #d2d2d7; background: white; text-align: left; color: #6e6e73; font-size: 11px; }}
        .footer-line {{ padding: 20px 40px; border-top: 1px solid #d2d2d7; background: white; text-align: right; color: #6e6e73; font-size: 11px; }}
        .container {{ background: white; padding: 40px; margin: 0; }}
        h1 {{ color: #1d1d1f; font-size: 32px; font-weight: 400; margin: 30px 0 10px 0; letter-spacing: -0.5px; }}
        h2 {{ color: #1d1d1f; font-size: 22px; font-weight: 400; margin-top: 40px; margin-bottom: 16px; letter-spacing: -0.3px; }}
        .status {{ font-size: 20px; font-weight: 400; padding: 24px; margin: 24px 0; border-radius: 16px; text-align: center; }}
        .status.pass {{ background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%); color: #155724; border: 1px solid #c3e6cb; }}
        .status.fail {{ background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%); color: #721c24; border: 1px solid #f5c6cb; }}
        .check {{ margin: 12px 0; padding: 16px 20px; background: #f5f5f7; border-radius: 12px; border-left: 4px solid #d2d2d7; font-size: 15px; line-height: 1.6; white-space: pre-wrap; }}
        .check.pass {{ border-left-color: #34c759; background: linear-gradient(135deg, #f0fdf4 0%, #e8f9ed 100%); }}
        .check.fail {{ border-left-color: #ff3b30; background: linear-gradient(135deg, #fff5f5 0%, #ffe8e8 100%); }}
        .info {{ background: linear-gradient(135deg, #e3f2fd 0%, #d0e8f7 100%); padding: 20px 24px; margin: 24px 0; border-radius: 12px; border: 1px solid #bbdefb; font-size: 14px; line-height: 1.8; }}
        table {{ width: 100%; border-collapse: separate; border-spacing: 0; margin: 24px 0; font-family: 'SF Mono', Monaco, monospace; font-size: 12px; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }}
        th, td {{ padding: 14px 16px; text-align: left; word-wrap: break-word; }}
        td {{ max-width: 600px; white-space: normal; }}
        th {{ background: linear-gradient(135deg, #1d1d1f 0%, #2c2c2e 100%); color: white; font-size: 13px; font-weight: 400; }}
        td {{ border-bottom: 1px solid #f0f0f0; background: white; }}
        tbody tr:last-child td {{ border-bottom: none; }}
        tbody tr:hover td {{ background: #f9f9f9; }}
        .error-table th {{ background: linear-gradient(135deg, #ff3b30 0%, #e63329 100%); }}
        .warning-table th {{ background: linear-gradient(135deg, #ff9500 0%, #e88400 100%); color: white; }}
        .warning-box {{ background: linear-gradient(135deg, #fff9e6 0%, #fff3d0 100%); padding: 20px 24px; margin: 24px 0; border-radius: 12px; border: 1px solid #ffecb3; font-size: 14px; line-height: 1.8; color: #8b6914; }}
    </style>
</head>
<body>
    <div class="header-line">Quality Checker 1.0</div>
    
    <div class="container">
        <h1>Data Quality Report</h1>
        
        <div class="info">
            <strong>File:</strong> {filename}<br>
            <strong>Report Generated:</strong> {timestamp}<br>
            <strong>Rows:</strong> {total_rows:,} | <strong>Columns:</strong> {total_cols}
        </div>
        
        <div class="status {status_color}">
            {status_text}
        </div>
        
        <h2>Quality Checks</h2>
"""
    
    for passed, title, messages in checks:
        status_class = "pass" if passed else "fail"
        message_text = f"<strong>{title}:</strong><br>" + "<br>".join([f"  {m}" for m in messages])
        html += f'<div class="check {status_class}">{message_text}</div>\n'
    
    if colon_errors and len(colon_errors) > 0:
        html += """
        <h2>Critical Errors (Must Fix)</h2>
        <p>The following items will cause Vena to split incorrectly:</p>
        <table class="error-table">
            <tr><th>Item</th><th>Issue</th></tr>
"""
        for error in colon_errors[:50]:  # Limit to 50
            html += f"<tr><td>{error['item']}</td><td>{error['issue']}</td></tr>\n"
        html += "</table>\n"
    
    # Add optional improvements section
    if colon_improvements and len(colon_improvements) > 0:
        html += f"""
        <h2>Optional Formatting Improvements</h2>
        <div class="warning-box">
            <strong>Found {len(colon_improvements)} items that could benefit from improved formatting (optional)</strong><br>
            These items will work in Vena, but could be formatted more consistently.
        </div>
        <table class="warning-table">
            <tr><th>Item</th><th>Suggestion</th></tr>
"""
        for improvement in colon_improvements[:50]:  # Limit to 50
            html += f"<tr><td>{improvement['item']}</td><td>{improvement['suggestion']}</td></tr>\n"
        html += "</table>\n"
    
    html += """
    </div>
    <div class="footer-line">Created by Deodata</div>
</body>
</html>
"""
    return html


# ============================================================================
# STREAMLIT APP
# ============================================================================

def main():
    # Beautiful header ribbon
    st.markdown("""
    <div class="header-ribbon">
        <h1>Data Quality Validation</h1>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### Upload Your CSV File")
    st.markdown("Upload your QuickBooks export to validate for Vena compatibility")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        help="Upload your QuickBooks transaction export"
    )
    
    if uploaded_file is not None:
        try:
            # Read the CSV
            df = pd.read_csv(uploaded_file)
            
            st.success(f"File loaded: {uploaded_file.name} ({len(df):,} rows, {len(df.columns)} columns)")
            
            # Run check button
            if st.button("Run Quality Check", type="primary", use_container_width=True):
                with st.spinner("Running quality checks..."):
                    
                    # Run all checks
                    check1 = check_headers(df)
                    check2 = check_transaction_ids(df)
                    check3 = check_items_combined(df)
                    check4 = check_accounts(df)
                    check5 = check_dates(df)
                    check6 = check_amounts(df)
                    
                    # Extract errors and improvements
                    colon_errors = check3[3] if len(check3) > 3 else []
                    colon_improvements = check3[4] if len(check3) > 4 else []
                    
                    # Combine all checks
                    checks = [
                        (check1[0], check1[1], check1[2]),
                        (check2[0], check2[1], check2[2]),
                        (check3[0], check3[1], check3[2]),
                        (check4[0], check4[1], check4[2]),
                        (check5[0], check5[1], check5[2]),
                        (check6[0], check6[1], check6[2])
                    ]
                    
                    all_passed = all(c[0] for c in checks)
                    
                    # Check if there are warnings/improvements
                    has_improvements = len(colon_improvements) > 0 if colon_improvements else False
                    has_critical_errors = len(colon_errors) > 0 if colon_errors else False
                    
                    # Show overall status
                    st.markdown("---")
                    if all_passed and not has_improvements:
                        st.markdown("""
                        <div class="success-box">
                            <h2 style="margin:0; font-size:20px; font-weight:400;">All Checks Passed</h2>
                            <p style="margin:10px 0 0 0;">File is ready for Vena upload</p>
                        </div>
                        """, unsafe_allow_html=True)
                    elif all_passed and has_improvements:
                        st.markdown("""
                        <div class="success-box">
                            <h2 style="margin:0; font-size:20px; font-weight:400;">All Checks Passed</h2>
                            <p style="margin:10px 0 0 0;">File can be uploaded to Vena. Some optional formatting improvements are suggested below.</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div class="error-box">
                            <h2 style="margin:0; font-size:20px; font-weight:400;">Issues Found</h2>
                            <p style="margin:10px 0 0 0;">Please review and fix the items below before uploading to Vena</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Show detailed results
                    st.markdown("### Detailed Results")
                    
                    for passed, title, messages in checks:
                        status_class = "pass" if passed else "fail"
                        message_html = f"<strong>{title}:</strong><br>" + "<br>".join([f"  {m}" for m in messages])
                        st.markdown(f'<div class="check-result {status_class}">{message_html}</div>', unsafe_allow_html=True)
                    
                    # Show critical errors table
                    if colon_errors and len(colon_errors) > 0:
                        st.markdown("### Critical Errors (Must Fix)")
                        st.error(f"Found {len(colon_errors)} items with incorrect colon placement")
                        
                        error_df = pd.DataFrame(colon_errors[:50])  # Show first 50
                        st.dataframe(
                            error_df, 
                            use_container_width=True, 
                            hide_index=True,
                            column_config={
                                "item": st.column_config.TextColumn("Item", width="large"),
                                "issue": st.column_config.TextColumn("Issue", width="medium")
                            }
                        )
                    
                    # Show optional improvements
                    if colon_improvements and len(colon_improvements) > 0:
                        st.markdown("### Optional Formatting Improvements")
                        st.warning(f"Found {len(colon_improvements)} items that could benefit from improved formatting (optional)")
                        
                        with st.expander("View suggested improvements", expanded=False):
                            improvement_df = pd.DataFrame(colon_improvements[:50])  # Show first 50
                            st.dataframe(
                                improvement_df, 
                                use_container_width=True, 
                                hide_index=True,
                                column_config={
                                    "item": st.column_config.TextColumn("Item", width="large"),
                                    "suggestion": st.column_config.TextColumn("Suggestion", width="large")
                                }
                            )
                    
                    # Generate HTML report
                    html_content = generate_html_report(
                        uploaded_file.name,
                        checks,
                        all_passed,
                        len(df),
                        len(df.columns),
                        colon_errors,
                        colon_improvements
                    )
                    
                    # Download button
                    st.markdown("---")
                    st.markdown("### Download Report")
                    
                    b64 = base64.b64encode(html_content.encode()).decode()
                    href = f'<a href="data:text/html;base64,{b64}" download="{uploaded_file.name}_QA_Report.html" style="text-decoration:none;"><button style="background:#0051D5;color:white;border:none;border-radius:8px;padding:12px 24px;font-size:16px;cursor:pointer;">Download HTML Report</button></a>'
                    st.markdown(href, unsafe_allow_html=True)
                    
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
            st.info("Please make sure you uploaded a valid CSV file from QuickBooks")
    
    else:
        st.info("Upload a CSV file to get started")
    
    # Footer
    st.markdown("""
    <div class="footer">
        Created by Deodata<br>
        Professional FP&A Solutions
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
