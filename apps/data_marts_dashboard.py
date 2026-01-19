# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.15",
#     "pandas>=2.0.0",
#     "plotly>=5.0.0",
# ]
# ///

import marimo

__generated_with = "0.19.4"
app = marimo.App(
    width="medium",
    layout_file="layouts/data_marts_dashboard.grid.json",
)


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
    from pathlib import Path
    return mo, pd, px


@app.cell
def _(mo):
    mo.md("""
    # 📊 Health Insurance Data Marts Dashboard

    **Interactive visualization of your complete 5-layer data warehouse**

    This dashboard displays data from exported CSV files, providing comprehensive analytics across all dimensions.
    """)
    return


@app.cell
def _():
    # Base URL for CSV files from GitHub raw content
    base_url = "https://raw.githubusercontent.com/njaltran/health-insurance-dashboard/main/apps/public"
    return (base_url,)


@app.cell
def _(mo):
    mo.md("""
    ## 🎯 Select Data Mart to Visualize
    """)
    return


@app.cell
def _(mo):
    data_mart_selector = mo.ui.dropdown(
        options=[
            "dm_customer_360",
            "dm_health_by_demographics",
            "dm_insurance_profitability",
            "dm_sleep_health_analysis",
            "dm_data_quality_dashboard"
        ],
        value="dm_customer_360",
        label="Choose a Data Mart:"
    )
    data_mart_selector
    return (data_mart_selector,)


@app.cell
def _(base_url, data_mart_selector, pd):
    # Load selected data mart from CSV
    selected_table = data_mart_selector.value

    # Display name mapping
    display_names = {
        "dm_customer_360": "Customer 360° View",
        "dm_health_by_demographics": "Health by Demographics",
        "dm_insurance_profitability": "Insurance Profitability",
        "dm_sleep_health_analysis": "Sleep Health Analysis",
        "dm_data_quality_dashboard": "Data Quality Dashboard"
    }
    display_name = display_names.get(selected_table, selected_table)

    # Read CSV file from GitHub raw URL
    csv_url = f"{base_url}/{selected_table}.csv"
    df = pd.read_csv(csv_url)
    return df, display_name, selected_table


@app.cell
def _(df, mo):
    mo.md(f"""
    ### 📋 Data Preview ({len(df)} rows)
    """)
    return


@app.cell
def _(df, mo):
    mo.ui.table(df.head(10), selection=None)
    return


@app.cell
def _(display_name, mo):
    mo.md(f"""
    ## 📈 Visualizations for {display_name}
    """)
    return


@app.cell
def _(df, px, selected_table):
    # Dynamic visualizations based on selected data mart

    if selected_table == "dm_customer_360":
        # Customer 360 visualizations

        # 1. Customer Segmentation
        fig1 = px.sunburst(
            df,
            path=['customer_segment', 'health_status'],
            values='lifetime_profit_contribution',
            title='Customer Segmentation by Profit Contribution',
            color='lifetime_profit_contribution',
            color_continuous_scale='RdYlGn'
        )

        # 2. Health Risk Score Distribution
        fig2 = px.histogram(
            df,
            x='health_risk_score',
            color='customer_segment',
            title='Health Risk Score Distribution by Segment',
            nbins=17,
            barmode='overlay',
            opacity=0.7
        )

        # 3. Lifetime Value Analysis
        fig3 = px.scatter(
            df,
            x='lifetime_premiums_paid',
            y='lifetime_claims_amount',
            color='customer_segment',
            size='years_as_customer',
            hover_data=['PersonID', 'health_risk_score'],
            title='Lifetime Premiums vs Claims by Customer Segment',
            labels={'lifetime_premiums_paid': 'Premiums Paid ($)',
                   'lifetime_claims_amount': 'Claims Amount ($)'}
        )

        # 4. Health Metrics Overview
        fig4 = px.box(
            df,
            x='customer_segment',
            y='current_heart_rate_bpm',
            color='health_status',
            title='Current Heart Rate Distribution by Segment',
            points='all'
        )

        customer_360_charts = [fig1, fig2, fig3, fig4]

    elif selected_table == "dm_health_by_demographics":
        # Health by Demographics visualizations

        # 1. Health Metrics by Age Group
        fig1 = px.bar(
            df.groupby('age_group').agg({
                'avg_heart_rate_bpm': 'mean',
                'avg_blood_oxygen_pct': 'mean',
                'avg_sleep_hours': 'mean'
            }).reset_index(),
            x='age_group',
            y=['avg_heart_rate_bpm', 'avg_blood_oxygen_pct', 'avg_sleep_hours'],
            title='Average Health Metrics by Age Group',
            barmode='group'
        )

        # 2. Sleep Quality by Demographics
        fig2 = px.scatter(
            df,
            x='avg_sleep_hours',
            y='avg_sleep_quality_score',
            size='unique_persons',
            color='gender',
            facet_col='family_status',
            title='Sleep Hours vs Quality by Demographics',
            labels={'avg_sleep_hours': 'Average Sleep Hours',
                   'avg_sleep_quality_score': 'Sleep Quality Score'}
        )

        # 3. Blood Pressure by Age and Gender
        fig3 = px.scatter(
            df,
            x='avg_systolic_bp',
            y='avg_diastolic_bp',
            color='age_group',
            size='unique_persons',
            facet_col='gender',
            title='Blood Pressure by Age Group and Gender',
            labels={'avg_systolic_bp': 'Systolic BP',
                   'avg_diastolic_bp': 'Diastolic BP'}
        )

        # 4. Health Risk Indicators
        fig4 = px.bar(
            df,
            x='age_group',
            y=['pct_elevated_heart_rate', 'pct_low_blood_oxygen',
               'pct_sleep_deprived', 'pct_with_sleep_disorder'],
            title='Health Risk Indicators by Age Group (%)',
            barmode='group',
            color_discrete_sequence=px.colors.qualitative.Set2
        )

        customer_360_charts = [fig1, fig2, fig3, fig4]

    elif selected_table == "dm_insurance_profitability":
        # Insurance Profitability visualizations

        # 1. Profit by Occupation and Wealth
        fig1 = px.treemap(
            df,
            path=['occupational_category', 'wealth_bracket'],
            values='net_profit',
            color='loss_ratio_pct',
            title='Insurance Profit by Occupation and Wealth Bracket',
            color_continuous_scale='RdYlGn_r',
            hover_data=['unique_customers', 'avg_profit_per_policy']
        )

        # 2. Loss Ratio Analysis
        fig2 = px.scatter(
            df,
            x='avg_annual_premium',
            y='avg_annual_claims',
            color='loss_ratio_pct',
            size='unique_customers',
            facet_col='insurance_status',
            title='Premium vs Claims with Loss Ratio',
            labels={'avg_annual_premium': 'Average Annual Premium ($)',
                   'avg_annual_claims': 'Average Annual Claims ($)'},
            color_continuous_scale='RdYlGn_r'
        )

        # 3. Profitability Overview
        fig3 = px.bar(
            df.groupby('occupational_category').agg({
                'total_premiums_collected': 'sum',
                'total_claims_paid': 'sum',
                'net_profit': 'sum'
            }).reset_index(),
            x='occupational_category',
            y=['total_premiums_collected', 'total_claims_paid', 'net_profit'],
            title='Financial Overview by Occupation',
            barmode='group',
            labels={'value': 'Amount ($)', 'variable': 'Metric'}
        )

        # 4. Risk Indicators by Segment
        fig4 = px.scatter(
            df,
            x='pct_unprofitable_policies',
            y='pct_high_utilizers',
            color='occupational_category',
            size='unique_customers',
            title='Risk Profile: Unprofitable Policies vs High Utilizers',
            labels={'pct_unprofitable_policies': '% Unprofitable Policies',
                   'pct_high_utilizers': '% High Utilizers'}
        )

        customer_360_charts = [fig1, fig2, fig3, fig4]

    elif selected_table == "dm_sleep_health_analysis":
        # Sleep Health Analysis visualizations

        # 1. Sleep metrics distribution
        fig1 = px.box(
            df,
            x='sleep_disorder',
            y=['avg_sleep_hours', 'avg_sleep_quality_score'],
            title='Sleep Metrics by Disorder Type',
            points='all'
        )

        # 2. Activity and Sleep relationship
        fig2 = px.scatter(
            df,
            x='avg_daily_steps',
            y='avg_sleep_quality_score',
            color='activity_level',
            size='unique_persons',
            title='Daily Steps vs Sleep Quality by Activity Level',
            labels={'avg_daily_steps': 'Average Daily Steps',
                   'avg_sleep_quality_score': 'Sleep Quality Score'}
        )

        # 3. Stress and Sleep
        fig3 = px.bar(
            df.groupby('stress_level').agg({
                'avg_sleep_hours': 'mean',
                'pct_sleep_deprived': 'mean',
                'pct_optimal_sleep': 'mean'
            }).reset_index(),
            x='stress_level',
            y=['avg_sleep_hours', 'pct_sleep_deprived', 'pct_optimal_sleep'],
            title='Sleep Metrics by Stress Level',
            barmode='group'
        )

        # 4. Health correlations
        fig4 = px.scatter(
            df,
            x='avg_heart_rate_bpm',
            y='avg_blood_oxygen_pct',
            color='sleep_disorder',
            size='unique_persons',
            title='Heart Rate vs Blood Oxygen by Sleep Disorder',
            labels={'avg_heart_rate_bpm': 'Heart Rate (BPM)',
                   'avg_blood_oxygen_pct': 'Blood Oxygen (%)'}
        )

        customer_360_charts = [fig1, fig2, fig3, fig4]

    elif selected_table == "dm_data_quality_dashboard":
        # Data Quality Dashboard visualizations

        # 1. Missing Data Overview
        fig1 = px.bar(
            df,
            x='data_source',
            y='total_records',
            title='Total records by source',
            barmode='group',
            labels={'value': 'Count', 'variable': 'Metric'}
        )

        # 2. Invalid Data Distribution
        fig2 = px.bar(
            df,
            x='data_source',
            y='overall_quality_score',
            title='Quality score by source',
            barmode='group',
            labels={'value': 'Percentage (%)', 'variable': 'Metric'})

        # 3. Extreme Values Detection
        fig3 = px.bar(
            df,
            x='data_source',
            y=['extreme_heart_rate_pct', 'extreme_sleep_hours_pct', 'extreme_step_count_pct'],
            title='Extreme Values by Source (%)',
            barmode='group',
            labels={'value': 'Percentage (%)', 'variable': 'Metric'}
        )

        # 4. Overall Quality Score
        fig4 = px.bar(
            df,
            x='data_source',
            y='overall_quality_score',
            color='quality_dimension',
            title='Overall Data Quality Score by Source and Dimension',
            labels={'overall_quality_score': 'Quality Score (0-100)'}
        )

        customer_360_charts = [fig1, fig2, fig3, fig4]

    else:
        customer_360_charts = []
    return customer_360_charts, fig1, fig2, fig3, fig4


@app.cell
def _(customer_360_charts, mo):
    # Display all charts for the selected data mart
    if customer_360_charts:
        chart_displays = [mo.ui.plotly(chart) for chart in customer_360_charts]
        charts_display = mo.vstack(chart_displays)
    else:
        charts_display = mo.md("*Select a data mart to view visualizations*")
    charts_display
    return


@app.cell
def _(customer_360_charts, mo):
    # Individual chart display for debugging
    if len(customer_360_charts) >= 2:
        mo.md("### Individual Chart Display - Chart 2")
    return


@app.cell
def _(customer_360_charts, mo):
    # Show the second chart explicitly
    if len(customer_360_charts) >= 2:
        mo.ui.plotly(customer_360_charts[1])
    return


@app.cell
def _(df, display_name, mo):
    mo.md(f"""
    ## 📊 Summary Statistics for {display_name}

    **Total Rows:** {len(df):,}
    **Total Columns:** {len(df.columns)}
    """)
    return


@app.cell
def _(df, mo):
    # Display summary statistics
    mo.ui.table(
        df.describe().round(2).reset_index(),
        selection=None,
        label="Statistical Summary"
    )
    return


@app.cell
def _(mo):
    mo.md("""
    ## 💾 Data Source Information

    This dashboard uses pre-exported CSV files from BigQuery data marts.
    To run custom queries or refresh the data, use the local BigQuery connection.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ---

    ## 📚 Data Marts Overview

    ### Available Data Marts:

    1. **dm_customer_360**: Complete customer profile with health metrics, lifetime value, and risk scoring
    2. **dm_health_by_demographics**: Population health analysis by age, gender, and family status
    3. **dm_insurance_profitability**: Financial performance and loss ratios by occupation and wealth
    4. **dm_sleep_health_analysis**: Sleep health research with activity and stress correlations
    5. **dm_data_quality_dashboard**: Data quality monitoring across all sources and dimensions

    ### Data Source:
    - **Format:** CSV files (exported from BigQuery)
    - **Location:** data/ directory
    - **Original Source:** dbt + BigQuery 5-Layer Data Warehouse

    ---

    **Built with [marimo](https://marimo.io/) | Data from dbt + BigQuery 5-Layer Data Warehouse**
    """)
    return


@app.cell
def _(fig1):
    fig1
    return


@app.cell
def _(fig2):
    fig2
    return


@app.cell
def _(fig3):
    fig3
    return


@app.cell
def _(fig4):
    fig4
    return


if __name__ == "__main__":
    app.run()