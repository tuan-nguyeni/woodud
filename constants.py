# constants.py

# Column names
COLUMN_RESPONSIBLE = "Zuständiger Bearbeiter"
COLUMN_GOODS_QUANTITY = "Rückgemeldete Gutmenge in Lagereinheit"
COLUMN_REMARKS = "Bemerkungen"

# Specific values
VALUE_RESPONSIBLE_TMM = "tmm"
VALUE_CONTAINS_BDE = "BDE:"

# UI labels and titles
LABEL_DATA_QUALITY_DASHBOARD = 'Data Quality Dashboard'
LABEL_FULL_DATA_VIEW = 'Full Data View'
LABEL_DATA_ERROR = 'Data Error'
LABEL_BAD_DATA_COUNT_BY = 'Bad Data Count by {}'
LABEL_SELECT_FILES = 'Drag and Drop or Select Files'
LABEL_LOADING_TYPE_DEFAULT = "default"

# Chart titles
TITLE_DATA_QUALITY_OVER_TIME = 'Data Quality Over Time (With Dummy Data)'
TITLE_DATA_QUALITY = 'Data Quality for {} (%)'

# Error messages
ERROR_REQUIRED_COLUMNS_NOT_FOUND = "Required columns not found."
ERROR_PROCESSING_FILE = "There was an error processing this file."

# Other constants
DATE_FORMAT = "%d %b %Y"
PLOT_BACKGROUND_COLOR = "lavender"
PLOT_FONT_COLOR = "darkblue"
PLOT_FONT_FAMILY = "Arial"
PLOT_AXIS_RANGE = [0, 100]
PLOT_BAR_COLOR = "darkblue"

# Dashboard layout styles
UPLOAD_STYLE = {
    'width': '100%',
    'height': '60px',
    'lineHeight': '60px',
    'borderWidth': '1px',
    'borderStyle': 'dashed',
    'borderRadius': '5px',
    'textAlign': 'center',
    'margin': '10px'
}
