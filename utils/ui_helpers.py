"""
UI Helper Module

Provides reusable UI components and utilities for the Community Pulse dashboard,
including welcome modals, empty states, tooltips, and tutorial mode functionality.
"""

import streamlit as st
from typing import List, Dict, Any, Optional


def initialize_session_state():
    """Initialize session state variables for UI features."""
    if 'show_welcome' not in st.session_state:
        st.session_state['show_welcome'] = True
    if 'tutorial_mode' not in st.session_state:
        st.session_state['tutorial_mode'] = False
    if 'tutorial_step' not in st.session_state:
        st.session_state['tutorial_step'] = 0
    if 'show_whats_new' not in st.session_state:
        st.session_state['show_whats_new'] = False


def show_welcome_modal():
    """
    Display a welcome modal for first-time users.
    
    Shows onboarding information and quick start guide.
    Returns True if the modal should be shown, False otherwise.
    """
    if not st.session_state.get('show_welcome', False):
        return False
    
    with st.container():
        st.markdown("""
        <style>
        .welcome-modal {
            padding: 2rem;
            border-radius: 0.5rem;
            border-radius: 0.5rem;
            background: #f1f3f5;
            color: #333;
            margin-bottom: 2rem;
            border-left: 5px solid #1f77b4;
        }
        .welcome-title {
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 1rem;
        }
        .welcome-subtitle {
            font-size: 1.2rem;
            margin-bottom: 1rem;
            opacity: 0.9;
        }
        .feature-list {
            margin: 1rem 0;
        }
        .feature-item {
            margin: 0.5rem 0;
            padding-left: 1.5rem;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="welcome-modal">
            <div class="welcome-title">Welcome to Community Pulse</div>
            <div class="welcome-subtitle">
                Transform messy member data into actionable insights in minutes.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### What You Can Do")
            st.markdown("""
            - **Generate** realistic messy data
            - **Clean** automatically with AI-powered tools
            - **Visualize** insights with interactive charts
            - **Export** cleaned data in multiple formats
            """)
        
        with col2:
            1. Click **"Generate New Data"** in the sidebar
            2. Navigate to **"Data Preparation"** tab
            3. Click **"Run Cleaning Algorithms"**
            4. Explore insights in **"Analytics"**
            """)
        
        with col3:
            - Hover over **info icons** for help
            - Toggle between **raw** and **cleaned** views
            - Enable **Tutorial Mode** for step-by-step guidance
            - Check **What's New** for latest features
            """)
        
        st.divider()
        
        col_dismiss, col_tutorial, col_start = st.columns([1, 1, 1])
        
        with col_dismiss:
            if st.button("Dismiss", use_container_width=True):
                st.session_state['show_welcome'] = False
                st.rerun()
        
        with col_tutorial:
            if st.button("Start Tutorial", type="secondary", use_container_width=True):
                st.session_state['show_welcome'] = False
                st.session_state['tutorial_mode'] = True
                st.session_state['tutorial_step'] = 0
                st.rerun()
        
        with col_start:
            if st.button("Get Started", type="primary", use_container_width=True):
                st.session_state['show_welcome'] = False
                st.rerun()
    
    return True


def show_empty_state(
    icon: str = "",
    title: str = "No Data Available",
    message: str = "Get started by generating some data.",
    action_label: Optional[str] = None,
    action_callback: Optional[callable] = None
):
    """
    Display an empty state message with optional action button.
    
    Args:
        icon: Emoji icon to display
        title: Main title for empty state
        message: Descriptive message
        action_label: Optional label for action button
        action_callback: Optional callback function for action button
    """
    st.markdown(f"""
    <div style="
        text-align: center;
        padding: 4rem 2rem;
        background: #f8f9fa;
        border-radius: 0.5rem;
        margin: 2rem 0;
    ">
        <div style="font-size: 2rem; margin-bottom: 1rem; color: #ccc;">{icon}</div>
        <div style="font-size: 1.5rem; font-weight: bold; color: #333; margin-bottom: 0.5rem;">
            {title}
        </div>
        <div style="font-size: 1rem; color: #666; margin-bottom: 1.5rem;">
            {message}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if action_label and action_callback:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button(action_label, type="primary", use_container_width=True):
                action_callback()


def show_info_tooltip(text: str, tooltip: str) -> str:
    """
    Create inline text with a tooltip icon.
    
    Args:
        text: Main text to display
        tooltip: Tooltip content
        
    Returns:
        Markdown formatted string with tooltip
    """
    return f"{text} :gray[ⓘ]"


def show_tutorial_step(step: int) -> bool:
    """
    Display tutorial overlay for the current step.
    
    Args:
        step: Current tutorial step number
        
    Returns:
        True if tutorial is active, False otherwise
    """
    if not st.session_state.get('tutorial_mode', False):
        return False
    
    current_step = st.session_state.get('tutorial_step', 0)
    
    if current_step != step:
        return False
    
    tutorial_steps = {
        0: {
            "title": "Step 1: Generate Data",
            "message": "Use the sidebar controls to generate messy sample data. Adjust the number of records and messiness level to simulate real-world scenarios.",
            "highlight": "sidebar"
        },
        1: {
            "title": "Step 2: Review KPIs",
            "message": "Check the Key Performance Indicators to understand the current data quality. Red metrics indicate issues that need attention.",
            "highlight": "kpis"
        },
        2: {
            "title": "Step 3: Configure Cleaning",
            "message": "Go to the Data Cleaning Ops tab and configure which cleaning steps to apply. Each step targets specific data quality issues.",
            "highlight": "cleaning"
        },
        3: {
            "title": "Step 4: Run Cleaning",
            "message": "Click 'Run Cleaning Algorithms' to automatically fix data quality issues. Watch the execution log for details.",
            "highlight": "run"
        },
        4: {
            "title": "Step 5: View Analytics",
            "message": "Navigate to Analytics Dashboard to visualize insights from your cleaned data. Use filters to focus on specific segments.",
            "highlight": "analytics"
        }
    }
    
    if current_step >= len(tutorial_steps):
        st.session_state['tutorial_mode'] = False
        st.success("Tutorial completed! You're now ready to use Community Pulse effectively.")
        return False
    
    step_info = tutorial_steps[current_step]
    
    st.info(f"""
    **{step_info['title']}**
    
    {step_info['message']}
    """)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("Skip Tutorial"):
            st.session_state['tutorial_mode'] = False
            st.rerun()
    
    with col2:
        if current_step > 0:
            if st.button("Previous"):
                st.session_state['tutorial_step'] = current_step - 1
                st.rerun()
    
    with col3:
        if st.button("Next", type="primary"):
            st.session_state['tutorial_step'] = current_step + 1
            st.rerun()
    
    return True


def show_whats_new():
    """Display a "What's New" panel with recent updates."""
    if not st.session_state.get('show_whats_new', False):
        return
    
    with st.expander("What's New in Community Pulse", expanded=True):
        st.markdown("""
        ### Recent Updates
        
        #### Version 2.0 - UX Enhancement Update
        *Released: December 2025*
        
        **New Features:**
        - 👋 **Welcome Modal**: First-time user onboarding experience
        - 📭 **Empty States**: Helpful guidance when no data is available
        - 💡 **Enhanced Tooltips**: Comprehensive help for all features
        - 🎓 **Tutorial Mode**: Step-by-step guided tour
        - 📊 **Improved KPIs**: More context and clearer metrics
        
        **Improvements:**
        - ✨ Refined UI copy for better clarity
        - 🎯 Context-aware messages and prompts
        - 🔄 Better loading and error feedback
        - ♿ Enhanced accessibility features
        
        **Bug Fixes:**
        - Fixed tooltip display issues
        - Improved mobile responsiveness
        - Enhanced error handling
        
        ---
        
        #### Previous Updates
        
        **Version 1.5** - Interactive Analytics
        - Added before/after comparison charts
        - Enhanced chart export capabilities
        - Improved data state management
        
        **Version 1.0** - Initial Release
        - Core data cleaning pipeline
        - Health metrics dashboard
        - Basic visualizations
        """)
        
        if st.button("Got it!", key="dismiss_whats_new"):
            st.session_state['show_whats_new'] = False
            st.rerun()


def show_loading_message(message: str = "Processing your data..."):
    """
    Display a context-aware loading message.
    
    Args:
        message: Custom loading message
    """
    return st.spinner(f"{message}")


def show_success_message(message: str, icon: str = ""):
    """
    Display a success message with icon.
    
    Args:
        message: Success message to display
        icon: Emoji icon (default: checkmark)
    """
    st.success(f"{message}")


def show_error_message(message: str, details: Optional[str] = None):
    """
    Display a context-aware error message.
    
    Args:
        message: Main error message
        details: Optional detailed error information
    """
    st.error(f"{message}")
    if details:
        with st.expander("🔍 Error Details"):
            st.code(details)


def show_warning_message(message: str, context: Optional[str] = None):
    """
    Display a context-aware warning message.
    
    Args:
        message: Warning message
        context: Optional context or suggestion
    """
    st.warning(f"{message}")
    if context:
        st.info(f"Tip: {context}")


# Context-aware message templates
MESSAGES = {
    "no_data_generated": {
        "icon": "",
        "title": "No Data Generated Yet",
        "message": "Start by clicking 'Generate New Data' in the sidebar to create sample data for analysis.",
    },
    "no_data_cleaned": {
        "icon": "",
        "title": "Data Not Cleaned Yet",
        "message": "Navigate to the 'Data Preparation' tab and run the cleaning pipeline to process your data.",
    },
    "no_filters_selected": {
        "icon": "",
        "title": "No Filters Selected",
        "message": "Select at least one role from the filter dropdown to view analytics for specific segments.",
    },
    "empty_analytics": {
        "icon": "",
        "title": "No Analytics Available",
        "message": "Clean your data first to generate insights and visualizations.",
    },
    "cleaning_success": "Data cleaning completed successfully! {records_processed} records processed.",
    "data_generated": "Successfully generated {num_records} records with {messiness} messiness level.",
    "export_ready": "Your data is ready to export. Choose CSV or JSON format from the sidebar.",
    "loading_data": "Loading your data, please wait...",
    "processing_cleaning": "Running {step_count} cleaning operations...",
    "calculating_metrics": "Calculating data health metrics...",
    "rendering_charts": "Rendering interactive visualizations...",
}


def get_contextual_message(key: str, **kwargs) -> str:
    """
    Get a context-aware message template.
    
    Args:
        key: Message template key
        **kwargs: Template variables
        
    Returns:
        Formatted message string, or empty string if key not found
    """
    template = MESSAGES.get(key, "")
    if isinstance(template, str):
        return template.format(**kwargs)
    # For dictionary templates (empty states), return empty string
    # These are accessed directly via MESSAGES[key]
    return ""
