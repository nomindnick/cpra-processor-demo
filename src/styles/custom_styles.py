#!/usr/bin/env python3
"""
Custom styling for professional CPRA Processing Application.

Modern, sleek design with subtle colors and visual interest.
"""

def get_custom_css():
    """
    Return custom CSS for professional styling with visual appeal.
    
    Returns:
        str: CSS string for injection into Streamlit app
    """
    return """
    <style>
    /* Import professional fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Source+Sans+Pro:wght@400;600;700&display=swap');
    
    /* Root variables with enhanced colors */
    :root {
        --primary: #0066CC;
        --primary-dark: #0052A3;
        --primary-light: #E6F2FF;
        --accent: #00D4AA;
        --accent-light: #E6FFF9;
        --secondary: #6C757D;
        --success: #10B981;
        --warning: #F59E0B;
        --error: #EF4444;
        --dark: #1F2937;
        --light: #F9FAFB;
        --border: #E5E7EB;
        --gradient-1: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --gradient-2: linear-gradient(135deg, #0066CC 0%, #00D4AA 100%);
        --gradient-3: linear-gradient(135deg, #E6F2FF 0%, #FFFFFF 100%);
        --shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    }
    
    /* Global styles with subtle pattern background */
    .stApp {
        font-family: 'Inter', 'Source Sans Pro', -apple-system, BlinkMacSystemFont, sans-serif;
        background: #FFFFFF;
        background-image: 
            radial-gradient(circle at 20% 80%, rgba(0, 212, 170, 0.05) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(0, 102, 204, 0.05) 0%, transparent 50%),
            radial-gradient(circle at 40% 40%, rgba(102, 126, 234, 0.03) 0%, transparent 50%);
        background-attachment: fixed;
        min-height: 100vh;
    }
    
    /* Add decorative top bar */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: var(--gradient-2);
        z-index: 1000;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .viewerBadge_container__1QSob {display: none;}
    
    /* Main content area with subtle background */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
        background: rgba(255, 255, 255, 0.9);
        border-radius: 1rem;
        backdrop-filter: blur(10px);
    }
    
    /* Headers with gradient accent */
    h1 {
        color: var(--dark) !important;
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.025em !important;
        line-height: 1.2 !important;
        margin-bottom: 1.5rem !important;
        padding-bottom: 1rem !important;
        border-bottom: 3px solid transparent !important;
        border-image: var(--gradient-2) 1 !important;
        background: linear-gradient(135deg, var(--dark) 0%, var(--primary) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    h2 {
        color: var(--dark) !important;
        font-size: 1.875rem !important;
        font-weight: 600 !important;
        margin-top: 2rem !important;
        margin-bottom: 1rem !important;
        position: relative;
        padding-left: 1rem;
    }
    
    h2::before {
        content: '';
        position: absolute;
        left: 0;
        top: 50%;
        transform: translateY(-50%);
        width: 4px;
        height: 70%;
        background: var(--gradient-2);
        border-radius: 2px;
    }
    
    h3 {
        color: var(--primary) !important;
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        margin-top: 1.5rem !important;
        margin-bottom: 1rem !important;
    }
    
    /* Sidebar with gradient background */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #FAFBFF 0%, #F0F4FF 100%);
        border-right: 1px solid rgba(0, 102, 204, 0.1);
        width: 300px !important;
        box-shadow: 2px 0 10px rgba(0, 0, 0, 0.05);
    }
    
    section[data-testid="stSidebar"] .block-container {
        padding-top: 3rem;
        padding-left: 1.5rem;
        padding-right: 1.5rem;
    }
    
    /* Sidebar title with gradient */
    section[data-testid="stSidebar"] h1 {
        font-size: 1.5rem !important;
        background: var(--gradient-2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        border-bottom: 2px solid transparent !important;
        border-image: var(--gradient-2) 1 !important;
        padding-bottom: 0.5rem !important;
        margin-bottom: 1rem !important;
    }
    
    /* Buttons with gradient hover effect */
    .stButton > button {
        background: white;
        color: var(--dark);
        border: 2px solid var(--border);
        border-radius: 0.75rem;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 0.875rem;
        line-height: 1.25rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: var(--shadow);
        width: 100%;
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: var(--gradient-3);
        transition: left 0.3s;
        z-index: -1;
    }
    
    .stButton > button:hover {
        border-color: var(--primary);
        transform: translateY(-2px);
        box-shadow: var(--shadow-xl);
    }
    
    .stButton > button:hover::before {
        left: 0;
    }
    
    /* Primary buttons with gradient */
    .stButton > button[kind="primary"],
    div[data-testid="stButton"] > button[kind="primary"],
    button[kind="primary"] {
        background: var(--gradient-2);
        color: white !important;
        border: none;
        font-weight: 600;
        box-shadow: 0 4px 14px 0 rgba(0, 102, 204, 0.25);
    }
    
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 102, 204, 0.35);
    }
    
    /* Metrics with colored accents */
    div[data-testid="metric-container"] {
        background: white;
        border-radius: 1rem;
        padding: 1.5rem;
        border: 1px solid var(--border);
        box-shadow: var(--shadow);
        transition: all 0.3s;
        position: relative;
        overflow: hidden;
    }
    
    div[data-testid="metric-container"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: var(--gradient-2);
    }
    
    div[data-testid="metric-container"]:hover {
        box-shadow: var(--shadow-xl);
        transform: translateY(-4px);
        border-color: var(--primary-light);
    }
    
    div[data-testid="metric-container"] [data-testid="metric-label"] {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--secondary);
        font-weight: 600;
    }
    
    div[data-testid="metric-container"] [data-testid="metric-value"] {
        font-size: 2.25rem;
        font-weight: 700;
        background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1;
        margin-top: 0.5rem;
    }
    
    /* File uploader with accent */
    div[data-testid="stFileUploader"] {
        background: linear-gradient(135deg, var(--primary-light) 0%, white 100%);
        border: 2px dashed var(--primary);
        border-radius: 1rem;
        padding: 2.5rem;
        transition: all 0.3s;
        position: relative;
    }
    
    div[data-testid="stFileUploader"]::before {
        content: '📁';
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-size: 3rem;
        opacity: 0.1;
    }
    
    div[data-testid="stFileUploader"]:hover {
        border-color: var(--accent);
        background: linear-gradient(135deg, var(--accent-light) 0%, white 100%);
        transform: scale(1.01);
    }
    
    div[data-testid="stFileUploader"] label {
        font-weight: 600;
        color: var(--primary);
        margin-bottom: 0.5rem;
    }
    
    /* Text inputs and text areas with accent */
    .stTextInput > div > div > input,
    .stTextArea > label > div > div > textarea {
        background: white;
        border: 2px solid var(--border);
        border-radius: 0.75rem;
        padding: 0.75rem 1rem;
        font-size: 0.875rem;
        color: var(--dark);
        transition: all 0.2s;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > label > div > div > textarea:focus {
        border-color: var(--accent);
        outline: none;
        box-shadow: 0 0 0 4px rgba(0, 212, 170, 0.1);
        background: linear-gradient(180deg, white 0%, var(--accent-light) 100%);
    }
    
    /* Text area labels */
    .stTextArea label {
        font-weight: 600;
        color: var(--primary);
        margin-bottom: 0.5rem;
    }
    
    /* Progress bar with gradient */
    .stProgress > div > div > div > div {
        background: var(--gradient-2);
        border-radius: 1rem;
        box-shadow: 0 2px 4px rgba(0, 102, 204, 0.2);
    }
    
    .stProgress > div > div {
        background: linear-gradient(90deg, var(--primary-light) 0%, var(--accent-light) 100%);
        border-radius: 1rem;
        height: 0.75rem;
        overflow: hidden;
        box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    /* Tabs with colored active state */
    .stTabs [data-baseweb="tab-list"] {
        background: linear-gradient(180deg, white 0%, var(--light) 100%);
        border-radius: 0.75rem;
        padding: 0.375rem;
        gap: 0.5rem;
        border: 1px solid var(--border);
        box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: var(--secondary);
        border-radius: 0.5rem;
        padding: 0.625rem 1.25rem;
        font-weight: 600;
        font-size: 0.875rem;
        transition: all 0.2s;
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--gradient-2);
        color: white;
        box-shadow: 0 2px 8px rgba(0, 102, 204, 0.25);
    }
    
    /* Expanders with accent */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, white 0%, var(--primary-light) 100%);
        border: 1px solid var(--primary-light);
        border-radius: 0.75rem;
        padding: 1rem 1.25rem;
        font-weight: 600;
        color: var(--primary);
        transition: all 0.2s;
        box-shadow: var(--shadow);
    }
    
    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, white 0%, var(--accent-light) 100%);
        border-color: var(--accent);
        transform: translateX(4px);
    }
    
    /* Alerts with gradient borders */
    .stAlert > div {
        border-radius: 0.75rem;
        padding: 1rem 1.25rem;
        border-left: 5px solid;
        font-size: 0.875rem;
        box-shadow: var(--shadow);
    }
    
    /* Success with gradient */
    .stAlert[data-baseweb="notification"] > div[kind="success"],
    div[role="alert"][data-baseweb="notification"][kind="success"] {
        background: linear-gradient(135deg, #F0FDF4 0%, white 100%);
        border-left-color: var(--success);
        color: #166534;
    }
    
    /* Info with gradient */
    .stAlert[data-baseweb="notification"] > div[kind="info"],
    div[role="alert"][data-baseweb="notification"][kind="info"] {
        background: linear-gradient(135deg, var(--primary-light) 0%, white 100%);
        border-left-color: var(--primary);
        color: #1E40AF;
    }
    
    /* Warning with gradient */
    .stAlert[data-baseweb="notification"] > div[kind="warning"],
    div[role="alert"][data-baseweb="notification"][kind="warning"] {
        background: linear-gradient(135deg, #FFFBEB 0%, white 100%);
        border-left-color: var(--warning);
        color: #92400E;
    }
    
    /* Error with gradient */
    .stAlert[data-baseweb="notification"] > div[kind="error"],
    div[role="alert"][data-baseweb="notification"][kind="error"] {
        background: linear-gradient(135deg, #FEF2F2 0%, white 100%);
        border-left-color: var(--error);
        color: #991B1B;
    }
    
    /* Checkbox with accent */
    .stCheckbox {
        font-size: 0.875rem;
        color: var(--dark);
    }
    
    .stCheckbox > label > div[data-testid="stMarkdownContainer"] > p {
        font-weight: 500;
    }
    
    .stCheckbox input:checked + div {
        background-color: var(--accent) !important;
        border-color: var(--accent) !important;
    }
    
    /* Columns with better spacing */
    .row-widget.stHorizontal {
        gap: 2rem;
    }
    
    /* Divider with gradient */
    hr {
        margin: 2.5rem 0;
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--primary), transparent);
    }
    
    /* Custom card component with gradient border */
    .custom-card {
        background: white;
        border-radius: 1rem;
        padding: 2rem;
        border: 1px solid transparent;
        background-image: linear-gradient(white, white), var(--gradient-2);
        background-origin: border-box;
        background-clip: padding-box, border-box;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
        margin-bottom: 1.5rem;
        transition: all 0.3s;
    }
    
    .custom-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
    }
    
    /* Navigation buttons in sidebar with gradient hover */
    section[data-testid="stSidebar"] .stButton > button {
        background: rgba(255, 255, 255, 0.8);
        border: 1px solid transparent;
        color: var(--dark);
        text-align: left;
        padding: 0.875rem 1.25rem;
        margin-bottom: 0.5rem;
        box-shadow: none;
        backdrop-filter: blur(10px);
        font-weight: 500;
    }
    
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: linear-gradient(135deg, var(--primary-light) 0%, var(--accent-light) 100%);
        border-color: var(--primary-light);
        transform: translateX(4px);
        color: var(--primary);
    }
    
    section[data-testid="stSidebar"] .stButton > button:focus,
    section[data-testid="stSidebar"] .stButton > button:active {
        background: var(--gradient-2);
        color: white;
        border-color: transparent;
        box-shadow: 0 4px 12px rgba(0, 102, 204, 0.25);
    }
    
    /* Session info with accent */
    section[data-testid="stSidebar"] .stText {
        font-size: 0.875rem;
        color: var(--primary);
        font-family: 'Monaco', 'Courier New', monospace;
        background: rgba(0, 102, 204, 0.05);
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        display: inline-block;
    }
    
    /* Select boxes with accent */
    .stSelectbox > div > div {
        background: white;
        border: 2px solid var(--border);
        border-radius: 0.75rem;
        transition: all 0.2s;
    }
    
    .stSelectbox > div > div:hover {
        border-color: var(--accent);
    }
    
    /* Spinner with gradient */
    .stSpinner > div {
        border-color: transparent;
        border-top-color: var(--primary);
        border-right-color: var(--accent);
    }
    
    /* Make containers have subtle backgrounds */
    .element-container {
        margin-bottom: 1.25rem;
    }
    
    .block-container {
        padding-left: 2.5rem;
        padding-right: 2.5rem;
    }
    
    /* Add subtle animation to interactive elements */
    @keyframes pulse {
        0% {
            box-shadow: 0 0 0 0 rgba(0, 102, 204, 0.4);
        }
        70% {
            box-shadow: 0 0 0 10px rgba(0, 102, 204, 0);
        }
        100% {
            box-shadow: 0 0 0 0 rgba(0, 102, 204, 0);
        }
    }
    
    /* Apply pulse to primary buttons */
    .stButton > button[kind="primary"] {
        animation: pulse 2s infinite;
    }
    
    .stButton > button[kind="primary"]:hover {
        animation: none;
    }
    
    /* Add decorative elements */
    .main::before {
        content: '';
        position: fixed;
        top: 10%;
        right: -5%;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, var(--accent) 0%, transparent 70%);
        opacity: 0.05;
        border-radius: 50%;
        pointer-events: none;
    }
    
    .main::after {
        content: '';
        position: fixed;
        bottom: 10%;
        left: -5%;
        width: 400px;
        height: 400px;
        background: radial-gradient(circle, var(--primary) 0%, transparent 70%);
        opacity: 0.05;
        border-radius: 50%;
        pointer-events: none;
    }
    </style>
    """


def apply_custom_styling():
    """Apply custom CSS to Streamlit app."""
    import streamlit as st
    st.markdown(get_custom_css(), unsafe_allow_html=True)
    
    # Add custom header if needed
    st.markdown("""
        <div style="display: none;">
            <!-- This hidden div ensures our custom CSS is loaded -->
        </div>
    """, unsafe_allow_html=True)