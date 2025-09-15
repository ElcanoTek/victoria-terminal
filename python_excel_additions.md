# Python Environment Setup and Excel Manipulation Capabilities

## Overview
This document outlines the additional capabilities to be added to Victoria for Python environment management and advanced Excel manipulation beyond the existing DuckDB SQL querying capabilities.

## Python Environment Management

### Core Capabilities
Victoria should be able to:
1. **Set up Python virtual environments** for isolated package management
2. **Install and manage Python packages** (pandas, openpyxl, xlsxwriter, etc.)
3. **Execute Python scripts** for complex data transformations
4. **Handle Python dependencies** and version management

### Python Environment Tools
Add the following tools to the allowed_tools list:
- `python_exec` - Execute Python code in a managed environment
- `pip_install` - Install Python packages
- `venv_create` - Create virtual environments
- `venv_activate` - Activate virtual environments

### Python Environment Instructions for VICTORIA.md

```markdown
## Python Environment & Advanced Analytics

Victoria has comprehensive Python capabilities for advanced data analysis, machine learning, and complex Excel manipulations that go beyond SQL querying.

### Python Environment Setup

**Creating Virtual Environments:**
```bash
# Create a new virtual environment for a project
python3 -m venv ~/venvs/adtech_analysis
source ~/venvs/adtech_analysis/bin/activate
```

**Installing Essential Packages:**
```bash
# Core data analysis packages
pip install pandas numpy matplotlib seaborn plotly
# Excel manipulation packages
pip install openpyxl xlsxwriter xlrd
# Machine learning packages
pip install scikit-learn scipy statsmodels
# Additional utilities
pip install jupyter ipython requests beautifulsoup4
```

### Python-Based Excel Manipulation

While DuckDB provides excellent SQL querying of Excel files, Python offers advanced manipulation capabilities:

**Reading Excel Files with Multiple Sheets:**
```python
import pandas as pd

# Read all sheets from an Excel file
excel_file = pd.ExcelFile('data/campaign_data.xlsx')
sheet_names = excel_file.sheet_names

# Read specific sheets
performance_data = pd.read_excel('data/campaign_data.xlsx', sheet_name='Performance')
budget_data = pd.read_excel('data/campaign_data.xlsx', sheet_name='Budget')
```

**Advanced Excel Writing:**
```python
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.chart import LineChart, Reference

# Create formatted Excel reports
with pd.ExcelWriter('reports/campaign_analysis.xlsx', engine='openpyxl') as writer:
    # Write multiple dataframes to different sheets
    summary_df.to_excel(writer, sheet_name='Summary', index=False)
    detailed_df.to_excel(writer, sheet_name='Detailed Analysis', index=False)
    
    # Access workbook for formatting
    workbook = writer.book
    summary_sheet = writer.sheets['Summary']
    
    # Apply formatting
    for cell in summary_sheet[1]:  # Header row
        cell.font = Font(bold=True)
        cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
```

**Excel Formula Generation:**
```python
# Generate Excel formulas programmatically
def create_performance_formulas(sheet, start_row, end_row):
    # CTR formula
    sheet[f'E{start_row}'] = f'=D{start_row}/C{start_row}*100'
    # CPC formula  
    sheet[f'F{start_row}'] = f'=B{start_row}/D{start_row}'
    # Copy formulas down
    for row in range(start_row + 1, end_row + 1):
        sheet[f'E{row}'] = f'=D{row}/C{row}*100'
        sheet[f'F{row}'] = f'=B{row}/D{row}'
```

### Data Analysis Workflows

**Campaign Performance Analysis:**
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Load and analyze campaign data
df = pd.read_excel('data/campaign_performance.xlsx')

# Calculate key metrics
df['CTR'] = df['clicks'] / df['impressions'] * 100
df['CPC'] = df['spend'] / df['clicks']
df['CVR'] = df['conversions'] / df['clicks'] * 100

# Statistical analysis
correlation_matrix = df[['CTR', 'CPC', 'CVR', 'spend']].corr()

# Visualization
plt.figure(figsize=(12, 8))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm')
plt.title('Campaign Metrics Correlation Matrix')
plt.savefig('reports/correlation_analysis.png')
```

**Time Series Analysis:**
```python
# Time series analysis for trend identification
df['date'] = pd.to_datetime(df['date'])
df.set_index('date', inplace=True)

# Rolling averages
df['CTR_7day'] = df['CTR'].rolling(window=7).mean()
df['spend_7day'] = df['spend'].rolling(window=7).sum()

# Seasonal decomposition
from statsmodels.tsa.seasonal import seasonal_decompose
decomposition = seasonal_decompose(df['CTR'], model='additive', period=7)
```

### Machine Learning for Campaign Optimization

**Predictive Modeling:**
```python
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

# Prepare features for CTR prediction
features = ['hour_of_day', 'day_of_week', 'device_type_encoded', 'placement_size']
X = df[features]
y = df['CTR']

# Train model
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Predictions and evaluation
predictions = model.predict(X_test)
r2 = r2_score(y_test, predictions)
```

**Anomaly Detection:**
```python
from sklearn.ensemble import IsolationForest

# Detect anomalous campaign performance
features_for_anomaly = ['CTR', 'CPC', 'CVR', 'spend']
isolation_forest = IsolationForest(contamination=0.1, random_state=42)
anomalies = isolation_forest.fit_predict(df[features_for_anomaly])
df['is_anomaly'] = anomalies == -1
```

### Best Practices for Python + Excel Workflows

1. **Data Validation**: Always validate Excel data before analysis
```python
# Check for missing values and data types
print(df.info())
print(df.describe())
print(df.isnull().sum())
```

2. **Memory Management**: For large Excel files, use chunking
```python
# Read large Excel files in chunks
chunk_size = 10000
for chunk in pd.read_excel('large_file.xlsx', chunksize=chunk_size):
    # Process chunk
    process_chunk(chunk)
```

3. **Error Handling**: Robust error handling for file operations
```python
try:
    df = pd.read_excel('data/campaign_data.xlsx')
except FileNotFoundError:
    print("Excel file not found. Please check the file path.")
except Exception as e:
    print(f"Error reading Excel file: {e}")
```

4. **Performance Optimization**: Use appropriate data types
```python
# Optimize data types for better performance
df['campaign_id'] = df['campaign_id'].astype('category')
df['date'] = pd.to_datetime(df['date'])
df['spend'] = pd.to_numeric(df['spend'], errors='coerce')
```
```

## MCP Configuration for Python Execution

### Python Execution MCP Server
Create a new MCP configuration for Python code execution:

```json
{
  "mcp": {
    "python_executor": {
      "type": "stdio", 
      "command": "uvx",
      "args": [
        "mcp-server-python-executor",
        "--venv-path", "${VICTORIA_HOME}/venvs/adtech",
        "--allowed-packages", "pandas,numpy,matplotlib,seaborn,plotly,openpyxl,xlsxwriter,scikit-learn,scipy,statsmodels"
      ]
    }
  }
}
```

### Additional Tools Configuration
Add to the allowed_tools list in crush.template.json:

```json
"allowed_tools": [
  "view",
  "ls", 
  "grep",
  "edit",
  "motherduck_query",
  "python_exec",
  "pip_install",
  "excel_read_advanced",
  "excel_write_formatted",
  "data_visualize",
  "ml_analyze"
]
```

## Implementation Priority

1. **Phase 1**: Basic Python execution capabilities
2. **Phase 2**: Advanced Excel manipulation tools
3. **Phase 3**: Machine learning and statistical analysis tools
4. **Phase 4**: Automated report generation and visualization

## Security Considerations

- Sandbox Python execution environment
- Restrict file system access to designated directories
- Limit package installation to approved libraries
- Monitor resource usage for long-running operations

