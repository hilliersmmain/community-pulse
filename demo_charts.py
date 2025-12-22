"""
Demo script to showcase enhanced chart features.
This script generates visualizations showing the improvements.

Requirements:
    - kaleido: Required for static image export
    - Install with: pip install kaleido

Raises:
    ImportError: If kaleido is not installed
    RuntimeError: If visualization generation fails
"""

import pandas as pd
import sys
import os

# Check for kaleido before importing plotly.io
try:
    import plotly.io as pio
except ImportError as e:
    print("❌ Error: Missing required dependencies")
    print(f"   {e}")
    sys.exit(1)

# Try to import kaleido to verify it's available
try:
    import kaleido
except ImportError:
    print("❌ Error: kaleido package is not installed")
    print("   This package is required for exporting charts as images.")
    print("   Install it with: pip install kaleido")
    print("   Or: pip install -r requirements.txt")
    sys.exit(1)

from utils.data_generator import generate_messy_data
from utils.cleaner import DataCleaner
from utils.visualizer import plot_attendance_trend, plot_role_distribution, plot_attendance_histogram

# Create output directory
output_dir = 'demo_outputs'
try:
    os.makedirs(output_dir, exist_ok=True)
except OSError as e:
    print(f"❌ Error: Could not create output directory: {e}")
    sys.exit(1)

print("🎨 Generating demo visualizations...")

# Generate sample data
print("\n1. Generating sample data...")
try:
    df = generate_messy_data(num_records=200, messiness_level='medium')
    print(f"   ✓ Generated {len(df)} records")
except Exception as e:
    print(f"   ❌ Error generating sample data: {e}")
    sys.exit(1)

# Clean the data
print("\n2. Cleaning data...")
try:
    cleaner = DataCleaner(df)
    clean_df = cleaner.clean_all()
    print(f"   ✓ Cleaned to {len(clean_df)} records")
except Exception as e:
    print(f"   ❌ Error cleaning data: {e}")
    sys.exit(1)

# Generate enhanced visualizations
print("\n3. Creating enhanced visualizations...")

try:
    # Attendance Trend with trend line and annotations
    fig1 = plot_attendance_trend(clean_df, data_state="cleaned")
    pio.write_image(fig1, f'{output_dir}/attendance_trend_enhanced.png', width=1200, height=600, scale=2)
    print("   ✓ Created enhanced attendance trend chart")

    # Role Distribution with counts and percentages
    fig2 = plot_role_distribution(clean_df, data_state="cleaned")
    pio.write_image(fig2, f'{output_dir}/role_distribution_enhanced.png', width=1200, height=600, scale=2)
    print("   ✓ Created enhanced role distribution chart")

    # Attendance Histogram with statistical annotations
    fig3 = plot_attendance_histogram(clean_df, data_state="cleaned")
    pio.write_image(fig3, f'{output_dir}/attendance_histogram_enhanced.png', width=1200, height=600, scale=2)
    print("   ✓ Created enhanced attendance histogram chart")
except Exception as e:
    print(f"   ❌ Error creating visualizations: {e}")
    sys.exit(1)

# Create comparison: raw vs cleaned
print("\n4. Creating before/after comparison...")
try:
    fig4_raw = plot_attendance_trend(df, data_state="raw")
    fig4_clean = plot_attendance_trend(clean_df, data_state="cleaned")
    pio.write_image(fig4_raw, f'{output_dir}/comparison_raw.png', width=1200, height=600, scale=2)
    pio.write_image(fig4_clean, f'{output_dir}/comparison_cleaned.png', width=1200, height=600, scale=2)
    print("   ✓ Created before/after comparison charts")
except Exception as e:
    print(f"   ❌ Error creating comparison charts: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("✅ Demo visualizations created successfully!")
print("="*60)
print(f"\n📁 Output location: {output_dir}/")
print("\nGenerated files:")
print(f"  • {output_dir}/attendance_trend_enhanced.png")
print(f"  • {output_dir}/role_distribution_enhanced.png")
print(f"  • {output_dir}/attendance_histogram_enhanced.png")
print(f"  • {output_dir}/comparison_raw.png")
print(f"  • {output_dir}/comparison_cleaned.png")
print("\nEnhanced Features Demonstrated:")
print("  • Statistical annotations (mean, median, std dev)")
print("  • Trend lines on time series charts")
print("  • Rich tooltips with cumulative data")
print("  • Counts + percentages on pie charts")
print("  • Data state indicators (raw vs cleaned)")
print("  • Export-ready PNG format (1200x600, 2x scale)")
print("  • Mean/median reference lines on histograms")
print("\n🎯 All visualizations are interactive when viewed in the app!")
print("\n💡 Tip: Open the Streamlit app to interact with live versions of these charts.")
