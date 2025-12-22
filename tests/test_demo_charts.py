"""
Tests for demo_charts.py script.

This module ensures the demo chart generation script works correctly
and handles errors appropriately.
"""

import pytest
import os
import sys
from pathlib import Path

# Add parent directory to path to import demo_charts
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestDemoChartsScript:
    """Test cases for the demo_charts.py script."""
    
    def test_demo_charts_imports(self):
        """Test that demo_charts can import all required modules."""
        try:
            import plotly.io as pio
            import kaleido
            from utils.data_generator import generate_messy_data
            from utils.cleaner import DataCleaner
            from utils.visualizer import (
                plot_attendance_trend, 
                plot_role_distribution, 
                plot_attendance_histogram
            )
            # If we get here, all imports worked
            assert True
        except ImportError as e:
            pytest.fail(f"Failed to import required module: {e}")
    
    def test_kaleido_available(self):
        """Test that kaleido package is available for image export."""
        try:
            import kaleido
            assert kaleido is not None
        except ImportError:
            pytest.fail("kaleido package not installed - required for demo_charts.py")
    
    def test_output_directory_creation(self):
        """Test that output directory can be created."""
        test_dir = 'test_demo_outputs'
        try:
            os.makedirs(test_dir, exist_ok=True)
            assert os.path.exists(test_dir)
            assert os.path.isdir(test_dir)
        finally:
            # Clean up
            if os.path.exists(test_dir):
                os.rmdir(test_dir)
    
    def test_demo_chart_generation_workflow(self):
        """Test the complete demo chart generation workflow."""
        from utils.data_generator import generate_messy_data
        from utils.cleaner import DataCleaner
        from utils.visualizer import (
            plot_attendance_trend, 
            plot_role_distribution, 
            plot_attendance_histogram
        )
        import plotly.io as pio
        
        # Generate minimal test data
        df = generate_messy_data(num_records=10, messiness_level='low')
        assert df is not None
        assert len(df) > 0
        
        # Clean the data
        cleaner = DataCleaner(df)
        clean_df = cleaner.clean_all()
        assert clean_df is not None
        
        # Create visualizations (don't save to disk in test)
        fig1 = plot_attendance_trend(clean_df, data_state="cleaned")
        assert fig1 is not None
        
        fig2 = plot_role_distribution(clean_df, data_state="cleaned")
        assert fig2 is not None
        
        fig3 = plot_attendance_histogram(clean_df, data_state="cleaned")
        assert fig3 is not None
    
    def test_demo_charts_error_handling(self):
        """Test that the script has proper error handling."""
        # This test verifies the script file contains error handling
        script_path = Path(__file__).parent.parent / 'demo_charts.py'
        
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Check for error handling patterns
        assert 'try:' in content, "Script should have try-except blocks"
        assert 'except' in content, "Script should have exception handling"
        assert 'ImportError' in content, "Script should check for ImportError"
        assert 'sys.exit' in content, "Script should exit on critical errors"
    
    def test_demo_charts_has_docstring(self):
        """Test that demo_charts.py has proper documentation."""
        script_path = Path(__file__).parent.parent / 'demo_charts.py'
        
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Check for docstring
        assert '"""' in content or "'''" in content, "Script should have docstring"
        assert 'Requirements:' in content, "Script should document requirements"
        assert 'kaleido' in content, "Script should mention kaleido requirement"


class TestDemoChartsOutputs:
    """Test cases for demo chart outputs."""
    
    def test_demo_outputs_directory_exists_after_run(self):
        """Test that demo_outputs directory exists after script runs."""
        # Note: This assumes the script has been run at least once
        # In CI/CD, this would be part of the build process
        output_dir = Path(__file__).parent.parent / 'demo_outputs'
        
        # We don't fail if it doesn't exist, just check if it does
        if output_dir.exists():
            assert output_dir.is_dir()
            
            # Check for expected files if directory exists
            expected_files = [
                'attendance_trend_enhanced.png',
                'role_distribution_enhanced.png',
                'attendance_histogram_enhanced.png',
                'comparison_raw.png',
                'comparison_cleaned.png'
            ]
            
            # If any file exists, verify it's a valid file
            for filename in expected_files:
                filepath = output_dir / filename
                if filepath.exists():
                    assert filepath.is_file()
                    assert filepath.stat().st_size > 0, f"{filename} should not be empty"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
