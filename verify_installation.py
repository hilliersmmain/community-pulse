#!/usr/bin/env python3
"""
Comprehensive verification script for Community Pulse application.

This script validates all major features are working correctly:
1. Data generation
2. Data cleaning pipeline
3. Metrics calculation
4. Visualization functions
5. File I/O operations
"""

import os
import sys
import tempfile
from io import StringIO

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from utils.data_generator import generate_messy_data
from utils.cleaner import DataCleaner
from utils.visualizer import (
    plot_attendance_trend,
    plot_role_distribution,
    plot_attendance_histogram,
    calculate_attendance_prediction
)
import pandas as pd

def test_data_generation():
    """Test data generation functionality."""
    print("=" * 60)
    print("TEST 1: Data Generation")
    print("=" * 60)
    
    df = generate_messy_data(num_records=100, save_path=None)
    
    assert len(df) > 0, "Generated dataframe is empty"
    # Account for ~10% duplicates added by generator
    assert len(df) >= 100, "Generated fewer records than expected"
    assert len(df) <= 120, "Generated too many records (expected ~110 with duplicates)"
    
    required_cols = ['Name', 'Email', 'Join_Date', 'Event_Attendance', 'Role']
    for col in required_cols:
        assert col in df.columns, f"Missing column: {col}"
    
    print(f"✓ Generated {len(df)} records with {len(df.columns)} columns")
    print(f"✓ All required columns present")
    print()
    
    return df

def test_data_cleaning(df):
    """Test data cleaning pipeline."""
    print("=" * 60)
    print("TEST 2: Data Cleaning Pipeline")
    print("=" * 60)
    
    cleaner = DataCleaner(df)
    initial_count = len(df)
    
    clean_df = cleaner.clean_all()
    final_count = len(clean_df)
    
    assert final_count > 0, "Cleaning removed all records"
    assert final_count <= initial_count, "Cleaning added records (impossible)"
    
    metrics = cleaner.get_cleaning_metrics()
    
    print(f"✓ Initial records: {initial_count}")
    print(f"✓ Final records: {final_count}")
    print(f"✓ Records removed: {initial_count - final_count}")
    print(f"✓ Data health score: {metrics['data_health_score']:.2f}%")
    print(f"✓ Duplicate rate: {metrics['duplicate_rate']:.2f}%")
    print(f"✓ Missing rate: {metrics['missing_rate']:.2f}%")
    print()
    
    return clean_df, metrics

def test_visualizations(clean_df):
    """Test visualization generation."""
    print("=" * 60)
    print("TEST 3: Visualizations")
    print("=" * 60)
    
    # Test attendance trend
    fig1 = plot_attendance_trend(clean_df)
    assert fig1.data is not None, "Attendance trend figure failed"
    print("✓ Attendance trend chart generated")
    
    # Test role distribution
    fig2 = plot_role_distribution(clean_df)
    assert fig2.data is not None, "Role distribution figure failed"
    print("✓ Role distribution chart generated")
    
    # Test attendance histogram
    fig3 = plot_attendance_histogram(clean_df)
    assert fig3.data is not None, "Attendance histogram failed"
    print("✓ Attendance histogram generated")
    
    # Test prediction
    prediction = calculate_attendance_prediction(clean_df)
    if prediction is not None:
        print(f"✓ Attendance prediction: {prediction:+.2f}% change")
    else:
        print("✓ Prediction (insufficient data - expected for small datasets)")
    
    print()

def test_file_operations():
    """Test file I/O operations."""
    print("=" * 60)
    print("TEST 4: File I/O Operations")
    print("=" * 60)
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as tmp:
        temp_path = tmp.name
    
    try:
        # Generate and save
        df = generate_messy_data(num_records=50, save_path=temp_path)
        assert os.path.exists(temp_path), "CSV file not created"
        print(f"✓ CSV file saved: {temp_path}")
        
        # Load and verify
        loaded_df = pd.read_csv(temp_path)
        assert len(loaded_df) == len(df), "Loaded data mismatch"
        print(f"✓ CSV file loaded: {len(loaded_df)} records")
        
        # Clean and export
        cleaner = DataCleaner(loaded_df)
        clean_df = cleaner.clean_all()
        
        clean_path = temp_path.replace('.csv', '_clean.csv')
        clean_df.to_csv(clean_path, index=False)
        assert os.path.exists(clean_path), "Clean CSV not created"
        print(f"✓ Cleaned CSV exported: {clean_path}")
        
    finally:
        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)
        clean_path = temp_path.replace('.csv', '_clean.csv')
        if os.path.exists(clean_path):
            os.remove(clean_path)
    
    print()

def test_edge_cases():
    """Test edge cases."""
    print("=" * 60)
    print("TEST 5: Edge Cases")
    print("=" * 60)
    
    # Test single record
    single_df = pd.DataFrame({
        'Name': ['John Doe'],
        'Email': ['john@test.com'],
        'Event_Attendance': [5],
        'Role': ['Member'],
        'Join_Date': [pd.Timestamp('2023-01-01')]
    })
    
    cleaner = DataCleaner(single_df)
    result = cleaner.clean_all()
    assert len(result) == 1, "Single record cleaning failed"
    print("✓ Single record handling works")
    
    # Test empty columns (should fail validation)
    try:
        invalid_df = pd.DataFrame({'Name': ['Test']})
        cleaner = DataCleaner(invalid_df)
        cleaner.validate_schema()
        assert False, "Should have failed schema validation"
    except ValueError:
        print("✓ Schema validation catches missing columns")
    
    # Test malformed dates
    date_df = pd.DataFrame({
        'Name': ['P1', 'P2', 'P3'],
        'Email': ['p1@test.com', 'p2@test.com', 'p3@test.com'],
        'Join_Date': ['not-a-date', '2023-01-01', None],
        'Event_Attendance': [1, 2, 3],
        'Role': ['Member', 'Member', 'Member']
    })
    
    fig = plot_attendance_trend(date_df)
    assert fig is not None, "Malformed dates crashed visualizer"
    print("✓ Malformed dates handled gracefully")
    
    print()

def test_fuzzy_matching():
    """Test fuzzy name matching."""
    print("=" * 60)
    print("TEST 6: Fuzzy Matching")
    print("=" * 60)
    
    # Create data with near-duplicate names
    fuzzy_df = pd.DataFrame({
        'Name': ['John Smith', 'Jon Smith', 'Jane Doe', 'Jane Do'],
        'Email': ['john1@test.com', 'john2@test.com', 'jane1@test.com', 'jane2@test.com'],
        'Event_Attendance': [5, 5, 10, 10],
        'Role': ['Member'] * 4
    })
    
    cleaner = DataCleaner(fuzzy_df)
    
    # Test fuzzy match function
    assert cleaner.fuzzy_match_names('John Smith', 'Jon Smith'), "Failed to match similar names"
    assert not cleaner.fuzzy_match_names('John Smith', 'Jane Doe'), "Incorrectly matched different names"
    print("✓ Fuzzy matching correctly identifies similar names")
    
    # Test fuzzy duplicate removal
    cleaner.standardize_names()
    cleaner.remove_fuzzy_duplicates()
    
    assert len(cleaner.clean_df) < len(fuzzy_df), "Fuzzy duplicates not removed"
    print(f"✓ Fuzzy duplicate removal reduced {len(fuzzy_df)} → {len(cleaner.clean_df)} records")
    
    print()

def main():
    """Run all verification tests."""
    print("\n" + "=" * 60)
    print("COMMUNITY PULSE - COMPREHENSIVE VERIFICATION")
    print("=" * 60)
    print()
    
    try:
        # Run all tests
        df = test_data_generation()
        clean_df, metrics = test_data_cleaning(df)
        test_visualizations(clean_df)
        test_file_operations()
        test_edge_cases()
        test_fuzzy_matching()
        
        # Summary
        print("=" * 60)
        print("VERIFICATION COMPLETE")
        print("=" * 60)
        print("✓ All tests passed successfully!")
        print("✓ Application is production-ready")
        print()
        print("Next steps:")
        print("1. Run: streamlit run app.py")
        print("2. Deploy to Streamlit Cloud or Docker")
        print("3. Capture screenshots for documentation")
        print("=" * 60)
        
        return 0
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
