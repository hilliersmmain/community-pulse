"""
Demo script to showcase enhanced chart features.
This script generates visualizations showing the improvements.
"""

import pandas as pd
import plotly.io as pio
from utils.data_generator import generate_messy_data
from utils.cleaner import DataCleaner
from utils.visualizer import plot_attendance_trend, plot_role_distribution, plot_attendance_histogram
import os

# Create output directory
os.makedirs('demo_outputs', exist_ok=True)

print("🎨 Generating demo visualizations...")

# Generate sample data
print("\n1. Generating sample data...")
df = generate_messy_data(num_records=200, messiness_level='medium')
print(f"   ✓ Generated {len(df)} records")

# Clean the data
print("\n2. Cleaning data...")
cleaner = DataCleaner(df)
clean_df = cleaner.clean_all()
print(f"   ✓ Cleaned to {len(clean_df)} records")

# Generate enhanced visualizations
print("\n3. Creating enhanced visualizations...")

# Attendance Trend with trend line and annotations
fig1 = plot_attendance_trend(clean_df, data_state="cleaned")
pio.write_image(fig1, 'demo_outputs/attendance_trend_enhanced.png', width=1200, height=600, scale=2)
print("   ✓ Created enhanced attendance trend chart")

# Role Distribution with counts and percentages
fig2 = plot_role_distribution(clean_df, data_state="cleaned")
pio.write_image(fig2, 'demo_outputs/role_distribution_enhanced.png', width=1200, height=600, scale=2)
print("   ✓ Created enhanced role distribution chart")

# Attendance Histogram with statistical annotations
fig3 = plot_attendance_histogram(clean_df, data_state="cleaned")
pio.write_image(fig3, 'demo_outputs/attendance_histogram_enhanced.png', width=1200, height=600, scale=2)
print("   ✓ Created enhanced attendance histogram chart")

# Create comparison: raw vs cleaned
print("\n4. Creating before/after comparison...")
fig4_raw = plot_attendance_trend(df, data_state="raw")
fig4_clean = plot_attendance_trend(clean_df, data_state="cleaned")
pio.write_image(fig4_raw, 'demo_outputs/comparison_raw.png', width=1200, height=600, scale=2)
pio.write_image(fig4_clean, 'demo_outputs/comparison_cleaned.png', width=1200, height=600, scale=2)
print("   ✓ Created before/after comparison charts")

print("\n" + "="*60)
print("✅ Demo visualizations created successfully!")
print("="*60)
print("\n📁 Output location: demo_outputs/")
print("\nEnhanced Features Demonstrated:")
print("  • Statistical annotations (mean, median, std dev)")
print("  • Trend lines on time series charts")
print("  • Rich tooltips with cumulative data")
print("  • Counts + percentages on pie charts")
print("  • Data state indicators (raw vs cleaned)")
print("  • Export-ready PNG format")
print("  • Mean/median reference lines on histograms")
print("\n🎯 All visualizations are interactive when viewed in the app!")
