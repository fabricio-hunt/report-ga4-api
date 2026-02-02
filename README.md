# GA4 Complete Data Collector

## 📋 Description

Python script to collect complete Google Analytics 4 (GA4) data and automatically populate spreadsheets.

## 🎯 Data Collection Configuration

### 1. **Web Platform** - Sheet "Web Platform"
- **Source**: Main E-commerce Property - ID: `YOUR_PROPERTY_ID_HERE`
- **Filter**: `platform = 'web'`
- **Metrics**:
  - Total sessions (all channels) → Column F
  - Total revenue (all channels) → Column G

### 2. **Mobile App** - Sheet "Mobile App"
- **Source**: Main E-commerce Property - ID: `YOUR_PROPERTY_ID_HERE`
- **Filter**: `platform IN ('Android', 'iOS')`
- **Metrics**:
  - Active users → Column C
  - Sessions → Column D
  - Revenue → Column E

### 3. **Secondary Property** - Sheet "Secondary Property"
- **Source**: Secondary GA4 Property - ID: `YOUR_PROPERTY_ID_HERE`
- **Filter**: `sessionDefaultChannelGroup = 'Organic Search'`
- **Metrics**:
  - Organic sessions → Column C
  - Organic users → Column D
  - Engagement rate (%) → Column E
  - Organic revenue → Column F

## 📦 Requirements

### Python Libraries
```bash
pip install --upgrade google-analytics-data
pip install --upgrade google-auth-oauthlib
pip install --upgrade google-auth-httplib2
pip install pandas
pip install openpyxl
```

### OAuth Credentials File
You need the `client_secret.json` file from Google Cloud Console:

1. Go to: https://console.cloud.google.com/
2. Select your project
3. Navigate to **APIs & Services** > **Credentials**
4. Click **+ CREATE CREDENTIALS** > **OAuth 2.0 Client ID**
5. Application type: **Desktop app**
6. Download the JSON file and rename it to `client_secret.json`
7. Place the file in the same folder as the script

## 🚀 How to Use

### 1. Setup
```bash
# Place client_secret.json in the same folder as the script
ls -la
# You should see:
# - ga4_complete_data_collector.py
# - client_secret.json
```

### 2. Run the Script
```bash
python ga4_complete_data_collector.py
```

### 3. Authentication (first time only)
- A browser window will open automatically
- Sign in with your Google account that has access to the GA4 properties
- Authorize access
- Credentials will be saved in `token.pickle` for future use

### 4. Output
The script will generate an Excel file with 3 sheets:
```
📁 ga4_reports/
   └── GA4_Complete_Report_2026_YYYYMMDD_HHMMSS.xlsx
       ├── Sheet: Web Platform
       ├── Sheet: Mobile App
       └── Sheet: Secondary Property
```

## 📊 Generated Excel Format

### Sheet: Web Platform
| Month | Year | Total Sessions (All Channels) | Total Revenue (All Channels) |
|-------|------|-------------------------------|------------------------------|
| January | 2026 | 150,000 | $1,250,000.00 |
| February | 2026 | 145,000 | $1,180,000.00 |
| ... | ... | ... | ... |

### Sheet: Mobile App
| Month | Year | Active Users | Sessions | Revenue |
|-------|------|--------------|----------|---------|
| January | 2026 | 25,000 | 50,000 | $250,000.00 |
| February | 2026 | 26,500 | 52,000 | $265,000.00 |
| ... | ... | ... | ... | ... |

### Sheet: Secondary Property
| Month | Year | Organic Sessions | Organic Users | Engagement Rate (%) | Organic Revenue |
|-------|------|------------------|---------------|---------------------|-----------------|
| January | 2026 | 12,000 | 9,500 | 65.50% | $85,000.00 |
| February | 2026 | 13,500 | 10,200 | 68.75% | $92,000.00 |
| ... | ... | ... | ... | ... | ... |

## 🔧 Configuration

### Change the Analysis Period
Edit these lines in `ga4_complete_data_collector.py`:

```python
# Analysis periods
ANALYSIS_YEAR = '2026'
ANALYSIS_START = '2026-01-01'
ANALYSIS_END = '2026-12-31'
```

### Configure Property IDs
```python
PROPERTIES = {
    'main_property': 'YOUR_PROPERTY_ID_1',
    'secondary_property': 'YOUR_PROPERTY_ID_2'
}
```

## 📝 Logs

The script generates detailed logs in:
```
ga4_reports/ga4_complete_collector.log
```

You can monitor the collection progress in real-time in the terminal.

## ❗ Common Issues

### Error: "client_secret.json not found"
**Solution**: Download the OAuth credentials file from Google Cloud Console and place it in the script folder.

### Error: "Invalid credentials"
**Solution**: Delete the `token.pickle` file and run the script again. You'll need to re-authenticate.

### Error: "Property ID not found"
**Solution**: Verify that the property IDs are correct:
- Go to Google Analytics 4
- Navigate to **Admin** > **Property Settings**
- Copy the **Property ID**

### No Data Returned
**Possible causes**:
1. The authenticated account doesn't have access to the properties
2. The selected period has no data
3. Filters are too restrictive

**Solution**: Check account permissions and the analysis period.

## 🔐 Security

⚠️ **IMPORTANT**:
- **DO NOT** share the `client_secret.json` file
- **DO NOT** share the `token.pickle` file
- Add to `.gitignore`:
```
client_secret.json
token.pickle
ga4_reports/
*.log
```

## 📞 Support

For questions about GA4 metrics, consult:
- [Official GA4 Documentation](https://developers.google.com/analytics/devguides/reporting/data/v1)
- [Metrics Reference](https://developers.google.com/analytics/devguides/reporting/data/v1/api-schema#metrics)
- [Dimensions Reference](https://developers.google.com/analytics/devguides/reporting/data/v1/api-schema#dimensions)

## 📄 License

This script is developed for internal use.

---

**Version**: 2.0  
**Date**: February 2026
