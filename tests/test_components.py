"""Smoke tests for component module imports."""


class TestComponentImports:
    def test_import_sidebar(self):
        from components.sidebar import render_sidebar

        assert callable(render_sidebar)

    def test_import_kpi_display(self):
        from components.kpi_display import render_kpi_section

        assert callable(render_kpi_section)

    def test_import_comparison(self):
        from components.comparison import render_comparison

        assert callable(render_comparison)

    def test_import_tab_preparation(self):
        from components.tab_preparation import render_preparation_tab

        assert callable(render_preparation_tab)

    def test_import_tab_analytics(self):
        from components.tab_analytics import render_analytics_tab

        assert callable(render_analytics_tab)

    def test_import_tab_explorer(self):
        from components.tab_explorer import render_explorer_tab

        assert callable(render_explorer_tab)
