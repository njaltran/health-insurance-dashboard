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
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    return go, make_subplots, mo, pd, px


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
def _(df, mo, selected_table):
    # Only populate this if we are looking at the Customer 360 mart
    customer_selector = mo.ui.dropdown(
        options=sorted(df['PersonID'].unique().tolist()) if 'PersonID' in df.columns else [],
        label="🔍 Drill Down: Select a Customer ID (Clear to view All)",
        value=None 
    )

    # Only display the dropdown if we are in the right data mart
    display_selector = mo.vstack([
        mo.md("### 👤 Single Customer Lookup"), 
        customer_selector
    ]) if selected_table == "dm_customer_360" and 'PersonID' in df.columns else mo.md("")

    display_selector
    return (customer_selector,)


@app.cell
def _(
    base_url,
    customer_selector,
    df,
    go,
    make_subplots,
    pd,
    px,
    selected_table,
):
    # Dynamic visualizations based on selected data mart
    customer_360_charts = []

    # ==========================================
    # 1. CUSTOMER 360
    # ==========================================
    if selected_table == "dm_customer_360":
            # 1. Calculate Global Averages
            avg_hr = df['current_heart_rate_bpm'].mean()
            avg_claims = df['avg_annual_claims'].mean()
            avg_visits = df['avg_annual_doctor_visits'].mean()

            # 2. Determine Data Source
            cust_data = {}
            view_title = ""
        
            if customer_selector.value is not None:
                pid = customer_selector.value
                cust_rows = df[df['PersonID'] == pid]
                if cust_rows.empty:
                    customer_360_charts = [go.Figure().add_annotation(text="Customer ID Not Found")]
                else:
                    cust_data = cust_rows.iloc[0].to_dict()
                    view_title = f"Customer Profile: {pid}"
            else:
                cust_data = {
                    'age': df['age'].mean(),
                    'avg_annual_doctor_visits': avg_visits,
                    'lifetime_doctor_visits': df['lifetime_doctor_visits'].mean(),
                    'lifetime_premiums_paid': df['lifetime_premiums_paid'].mean(),
                    'current_sleep_hours': df['current_sleep_hours'].mean(),
                    'current_daily_steps': df['current_daily_steps'].mean(),
                    'current_heart_rate_bpm': avg_hr,
                    'avg_annual_claims': avg_claims,
                    'lifetime_claims_amount': df['lifetime_claims_amount'].mean()
                }
                view_title = "Global Portfolio Average (All Customers)"

            # 3. Generate Visualizations
            if cust_data:
                # FIG 1: STATS CARD
                fig_stats = go.Figure()
                stats_text = [
                    f"<b>Age:</b> {int(cust_data.get('age', 0))}",
                    f"<b>Annual DV's:</b> {cust_data.get('avg_annual_doctor_visits', 0):.1f}",
                    f"<b>Lifetime DV's:</b> {int(cust_data.get('lifetime_doctor_visits', 0))}",
                    f"<b>Lifetime Prem:</b> ${cust_data.get('lifetime_premiums_paid', 0):,.0f}"
                ]
                fig_stats.add_annotation(
                    x=0.5, y=0.5, text="<br>".join(stats_text), showarrow=False,
                    font=dict(size=14, color="#333"), align="left",
                    bgcolor="#f0f0f0", bordercolor="#ccc", borderwidth=1, borderpad=20, width=200
                )
                fig_stats.update_layout(height=180, margin=dict(l=0, r=0, t=30, b=0), title_text=view_title, xaxis=dict(visible=False), yaxis=dict(visible=False), plot_bgcolor='rgba(0,0,0,0)')

                # FIG 2: LIFESTYLE
                fig_lifestyle = make_subplots(rows=1, cols=2, subplot_titles=("Avg Sleep Hours (Target: 7h)", "Daily Steps (Target: 10k)"))
                fig_lifestyle.add_trace(go.Bar(x=[cust_data.get('current_sleep_hours', 0)], y=[''], orientation='h', name='Sleep', marker_color='#4e79a7', text=[f"{cust_data.get('current_sleep_hours', 0):.1f}h"], textposition='auto'), row=1, col=1)
                fig_lifestyle.add_vline(x=7, line_width=2, line_dash="dash", line_color="gray", row=1, col=1)
                fig_lifestyle.add_trace(go.Bar(x=[cust_data.get('current_daily_steps', 0)], y=[''], orientation='h', name='Steps', marker_color='#4e79a7', text=[f"{int(cust_data.get('current_daily_steps', 0)):,}"], textposition='auto'), row=1, col=2)
                fig_lifestyle.add_vline(x=10000, line_width=2, line_dash="dash", line_color="gray", row=1, col=2)
                fig_lifestyle.update_layout(height=250, showlegend=False, title_text="Lifestyle Audit")

                # COMPARISON CHARTS
                def create_comparison_chart(val, avg, title, max_range):
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=[val], y=[0], mode='markers', marker=dict(color='#76b7b2', size=20, line=dict(width=2, color='white'))))
                    fig.add_vline(x=avg, line_width=3, line_color="#e15759")
                    fig.add_annotation(
                        x=0.5, y=-0.5, # Moved down to avoid overlap
                        text=f"Global Avg: {avg:,.1f}", 
                        showarrow=False, font=dict(size=12, color="#e15759"), xref="paper", yref="paper"
                    )
                    # Increased bottom margin (b=80) to fit the label
                    fig.update_layout(
                        title={'text': title, 'font': {'size': 14}}, 
                        height=180, margin=dict(l=20, r=20, t=40, b=80), 
                        yaxis=dict(visible=False, range=[-0.5, 0.5]), 
                        xaxis=dict(range=[0, max_range]), showlegend=False
                    )
                    return fig

                fig_hr = create_comparison_chart(cust_data.get('current_heart_rate_bpm', 0), avg_hr, "Average Heart Rate vs. Global Average", 120)
                fig_claims = create_comparison_chart(cust_data.get('avg_annual_claims', 0), avg_claims, "Annual Claims vs. Global Average", 6000)
                fig_visits = create_comparison_chart(cust_data.get('avg_annual_doctor_visits', 0), avg_visits, "Average Doctor Visits vs. Global Average", 20)

                # FIG 6: FINANCIAL
                fig_fin = go.Figure()
                fig_fin.add_trace(go.Bar(y=['Balance'], x=[cust_data.get('lifetime_claims_amount', 0) * -1], name='Claims', orientation='h', marker_color='#e15759'))
                fig_fin.add_trace(go.Bar(y=['Balance'], x=[cust_data.get('lifetime_premiums_paid', 0)], name='Premiums', orientation='h', marker_color='#59a14f'))
                fig_fin.update_layout(title="Financial Balance", barmode='relative', height=200, yaxis=dict(visible=False))

                customer_360_charts = [fig_stats, fig_lifestyle, fig_hr, fig_claims, fig_visits, fig_fin]
    
    # ==========================================
    # 2. HEALTH BY DEMOGRAPHICS
    # ==========================================
    elif selected_table == "dm_health_by_demographics":
        age_order = ['18-29', '30-39', '40-49', '50-59', '60-69', '70+']
        cost_col = next((c for c in df.columns if 'insurance' in c.lower() and 'cost' in c.lower()), 'avg_insurance_cost')
        
        scatter_data = df.groupby('age_group', observed=True).agg({'avg_sleep_hours': 'mean', cost_col: 'mean', 'avg_sleep_quality_score': 'sum'}).reset_index()
        fig1 = px.scatter(scatter_data, x='avg_sleep_hours', y=cost_col, color='age_group', size='avg_sleep_quality_score', title='Sleep vs Cost by Age', category_orders={'age_group': age_order})
        # Explicit height to fix squishing
        fig1.update_layout(height=500, margin=dict(t=50, b=50))
        
        fig2 = px.density_heatmap(df, x='age_group', y='family_status', z='pct_with_sleep_disorder', histfunc='avg', title='Sleep Disorder Heatmap', category_orders={'age_group': age_order})
        fig2.update_layout(height=500, margin=dict(t=50, b=50))
        
        hr_by_demo = df.groupby(['age_group', 'gender'], observed=True)['avg_heart_rate_bpm'].mean().reset_index()
        fig3 = px.bar(hr_by_demo, x='age_group', y='avg_heart_rate_bpm', color='gender', barmode='group', title='Heart Rate by Age & Gender', category_orders={'age_group': age_order})
        fig3.update_layout(height=500, margin=dict(t=50, b=50))
        
        customer_360_charts = [fig1, fig2, fig3]

    # ==========================================
    # 3. INSURANCE PROFITABILITY
    # ==========================================
    elif selected_table == "dm_insurance_profitability":
        try:
            cust_url = f"{base_url}/dm_customer_360.csv"
            ts_raw_df = pd.read_csv(cust_url)
        
            ts_raw_df['occupational_category'] = ts_raw_df['occupational_category'].replace({
                "it specialist": "IT-Specialist", "healthcare_worker": "Healthcare Worker", "office_worker": "Office Worker", 
                "retail_worker": "Retail Worker", "self-employed": "Self-Employed", "student": "Student", 
                "engineer": "Engineer", "nurse": "Nurse", "teacher": "Teacher", "unemployed": "Unemployed"
            })
            date_col = 'insurance_sign_up_date' if 'insurance_sign_up_date' in ts_raw_df.columns else 'created_at'
            ts_raw_df['temp_date'] = pd.to_datetime(ts_raw_df[date_col], errors='coerce')

            # Top Row: Trend
            trend_df = ts_raw_df.groupby(ts_raw_df['temp_date'].dt.to_period("M").dt.to_timestamp())[['lifetime_premiums_paid', 'lifetime_claims_amount']].sum().reset_index()
            trend_df.rename(columns={'temp_date': 'Date'}, inplace=True)
            trend_df['Loss Ratio %'] = (trend_df['lifetime_claims_amount'] / trend_df['lifetime_premiums_paid'].replace(0, 1)) * 100

            top_row_fig = make_subplots(rows=1, cols=2, subplot_titles=("Premiums vs Claims", "Loss Ratio Trend"), horizontal_spacing=0.15)
            top_row_fig.add_trace(go.Scatter(x=trend_df['Date'], y=trend_df['lifetime_premiums_paid'], mode='lines', name='Premiums', stackgroup='one', line=dict(color='#d4b9da')), row=1, col=1)
            top_row_fig.add_trace(go.Scatter(x=trend_df['Date'], y=trend_df['lifetime_claims_amount'], mode='lines', name='Claims', stackgroup='one', line=dict(color='#4e79a7')), row=1, col=1)
            top_row_fig.add_trace(go.Scatter(x=trend_df['Date'], y=trend_df['Loss Ratio %'], mode='lines', name='Loss Ratio %', line=dict(color='#4e79a7', width=3)), row=1, col=2)
            top_row_fig.add_hline(y=60, line_dash="solid", line_color="gray", annotation_text="Limit (60%)", row=1, col=2)
            # Explicit height
            top_row_fig.update_layout(height=500, showlegend=True, title_text="Financial Performance")

            # Middle Row: Deviation
            total_claims = ts_raw_df['lifetime_claims_amount'].sum()
            total_prem = ts_raw_df['lifetime_premiums_paid'].sum()
            portfolio_avg = total_claims / total_prem
            dev_df = ts_raw_df.groupby('occupational_category').agg({'lifetime_claims_amount': 'sum', 'lifetime_premiums_paid': 'sum'}).reset_index()
            dev_df['Deviation'] = (dev_df['lifetime_claims_amount'] / dev_df['lifetime_premiums_paid']) - portfolio_avg
            dev_df = dev_df.sort_values('Deviation')

            middle_row_fig = make_subplots(rows=1, cols=1, subplot_titles=("Segment Deviation from Portfolio Avg",))
            colors = ['#e15759' if x > 0 else '#4e79a7' for x in dev_df['Deviation']]
            middle_row_fig.add_trace(go.Bar(x=dev_df['Deviation'], y=dev_df['occupational_category'], orientation='h', marker_color=colors, text=dev_df['Deviation'], texttemplate="%{x:+.1%}"), row=1, col=1)
            # Explicit height
            middle_row_fig.update_layout(height=500, title_text="Risk Analysis")

            customer_360_charts = [top_row_fig, middle_row_fig]
        except Exception as e:
            customer_360_charts = [go.Figure().add_annotation(text=f"Error: {e}")]

    # ==========================================
    # 4. SLEEP HEALTH
    # ==========================================
    elif selected_table == "dm_sleep_health_analysis":
        fig1 = px.box(df, x='sleep_disorder', y=['avg_sleep_hours', 'avg_sleep_quality_score'], title='Sleep Metrics by Disorder')
        fig1.update_layout(height=500)
        
        fig2 = px.scatter(df, x='avg_daily_steps', y='avg_sleep_quality_score', color='activity_level', title='Steps vs Sleep Quality')
        fig2.update_layout(height=500)
        
        fig3 = px.bar(df.groupby('stress_level').agg({'avg_sleep_hours': 'mean'}).reset_index(), x='stress_level', y='avg_sleep_hours', title='Sleep by Stress Level')
        fig3.update_layout(height=500)
        
        customer_360_charts = [fig1, fig2, fig3]

    # ==========================================
    # 5. DATA QUALITY
    # ==========================================
    elif selected_table == "dm_data_quality_dashboard":
        overall_row = df[(df['data_source'] == 'All Sources') & (df['quality_dimension'] == 'Overall')].iloc[0]
        
        # Gauges and KPIs
        kpi_fig = make_subplots(rows=1, cols=2, specs=[[{'type': 'domain'}, {'type': 'domain'}]], subplot_titles=("Overall Quality", "Data Completeness"))
        kpi_fig.add_trace(go.Indicator(mode="gauge+number", value=overall_row['overall_quality_score'], gauge={'axis': {'range': [90, 100]}, 'bar': {'color': "#59a14f"}}), row=1, col=1)
        
        avg_missing = (overall_row['missing_blood_oxygen_pct'] + overall_row['missing_stress_level_pct']) / 2
        kpi_fig.add_trace(go.Indicator(mode="gauge+number", value=100-avg_missing, gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#4e79a7"}}), row=1, col=2)
        # Explicit height and title to overwrite any potential Frankenstein states
        kpi_fig.update_layout(height=400, title_text="Data Quality KPI Monitor")

        # Anomaly Chart
        try:
            cust_url = f"{base_url}/dm_customer_360.csv"
            raw_df = pd.read_csv(cust_url)
            
            activity_mapper = {"sedentary": 1, "active": 2, "highly_active": 3}
            raw_df['act_num'] = raw_df['current_activity_level'].str.lower().map(activity_mapper).fillna(0)
            
            def check_anomaly(row):
                if row['act_num'] == 3 and row['current_daily_steps'] < 4000: return "Over-Reporter"
                if row['act_num'] == 1 and row['current_daily_steps'] > 8000: return "Under-Reporter"
                return "Normal"
            
            raw_df['Status'] = raw_df.apply(check_anomaly, axis=1)
            fig_anomaly = px.strip(raw_df, x="act_num", y="current_daily_steps", color="Status", title="Activity Anomalies")
            fig_anomaly.add_hline(y=4000, line_dash="dash"); fig_anomaly.add_hline(y=8000, line_dash="dash")
            fig_anomaly.update_layout(height=500)
            
            customer_360_charts = [kpi_fig, fig_anomaly]
        except:
            customer_360_charts = [kpi_fig]

    return (customer_360_charts,)


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


if __name__ == "__main__":
    app.run()