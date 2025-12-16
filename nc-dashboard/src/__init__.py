"""
NC Dashboard Source Package
Contains all modules for the Non-Conformance Analysis Dashboard

Author: Xander @ Calyx Containers
"""

from .data_loader import (
    load_nc_data,
    refresh_data,
    get_data_summary,
    load_sample_data
)

from .kpi_cards import render_open_nc_status_tracker

from .aging_analysis import (
    render_aging_dashboard,
    calculate_aging_metrics
)

from .cost_analysis import (
    render_cost_of_rework,
    render_cost_avoided
)

from .customer_analysis import render_customer_analysis

from .pareto_chart import (
    render_issue_type_pareto,
    calculate_pareto_data
)

from .utils import (
    setup_logging,
    export_dataframe,
    format_currency,
    format_number,
    format_percentage
)

__all__ = [
    'load_nc_data',
    'refresh_data',
    'get_data_summary',
    'load_sample_data',
    'render_open_nc_status_tracker',
    'render_aging_dashboard',
    'calculate_aging_metrics',
    'render_cost_of_rework',
    'render_cost_avoided',
    'render_customer_analysis',
    'render_issue_type_pareto',
    'calculate_pareto_data',
    'setup_logging',
    'export_dataframe',
    'format_currency',
    'format_number',
    'format_percentage'
]

__version__ = '1.0.0'
