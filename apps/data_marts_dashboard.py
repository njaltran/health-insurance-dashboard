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
    from pathlib import Path
    import os
    from plotly.subplots import make_subplots

    return go, make_subplots, mo, os, pd, px


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

        value=None # Default to None (show the aggregate view first)

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
    customer_selector,
    data_dir,
    df,
    go,
    make_subplots,
    os,
    pd,
    px,
    selected_table,
):
    # Dynamic visualizations based on selected data mart
    customer_360_charts = []

    if selected_table == "dm_customer_360":
            # 1. Calculate Global Averages (Used for Reference Lines)
            avg_hr = df['current_heart_rate_bpm'].mean()
            avg_claims = df['avg_annual_claims'].mean()
            avg_visits = df['avg_annual_doctor_visits'].mean()

            # 2. Determine Data Source (Single User vs. Global Average)
            cust_data = {}
            view_title = ""
        
            if customer_selector.value is not None:
                # CASE A: Specific Customer Selected
                pid = customer_selector.value
                cust_rows = df[df['PersonID'] == pid]
            
                if cust_rows.empty:
                    customer_360_charts = [go.Figure().add_annotation(text="Customer ID Not Found")]
                else:
                    # FIX: Convert to dictionary immediately to avoid Pandas "Ambiguous Truth" error
                    cust_data = cust_rows.iloc[0].to_dict()
                    view_title = f"Customer Profile: {pid}"
            else:
                # CASE B: No Selection -> Use Portfolio Averages
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

            # 3. Generate Visualizations (If valid data exists)
            if cust_data:
                # --- FIG 1: STATS CARD ---
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
                fig_stats.update_layout(
                    height=180, margin=dict(l=0, r=0, t=30, b=0),
                    title_text=view_title,
                    xaxis=dict(visible=False), yaxis=dict(visible=False),
                    plot_bgcolor='rgba(0,0,0,0)'
                )

                # --- FIG 2: LIFESTYLE AUDIT ---
                fig_lifestyle = make_subplots(rows=1, cols=2, subplot_titles=("Avg Sleep Hours (Target: 7h)", "Daily Steps (Target: 10k)"))
            
                # Sleep
                sleep_val = cust_data.get('current_sleep_hours', 0)
                fig_lifestyle.add_trace(go.Bar(
                    x=[sleep_val], y=[''], orientation='h', name='Sleep', marker_color='#4e79a7', 
                    text=[f"{sleep_val:.1f}h"], textposition='auto'
                ), row=1, col=1)
                fig_lifestyle.add_vline(x=7, line_width=2, line_dash="dash", line_color="gray", annotation_text="Target", row=1, col=1)

                # Steps
                steps_val = cust_data.get('current_daily_steps', 0)
                fig_lifestyle.add_trace(go.Bar(
                    x=[steps_val], y=[''], orientation='h', name='Steps', marker_color='#4e79a7',
                    text=[f"{int(steps_val):,}"], textposition='auto'
                ), row=1, col=2)
                fig_lifestyle.add_vline(x=10000, line_width=2, line_dash="dash", line_color="gray", annotation_text="Target", row=1, col=2)

                fig_lifestyle.update_layout(height=250, showlegend=False, title_text="Lifestyle Audit")
                fig_lifestyle.update_xaxes(range=[0, 12], row=1, col=1) 
                fig_lifestyle.update_xaxes(range=[0, 15000], row=1, col=2) 

                # --- FIG 3-5: COMPARISON CHARTS (Teal Dot vs Red Line) ---
                def create_comparison_chart(val, avg, title, max_range):
                    fig = go.Figure()
                    # The Dot (Customer/Average)
                    fig.add_trace(go.Scatter(
                        x=[val], y=[0], mode='markers',
                        marker=dict(color='#76b7b2', size=20, line=dict(width=2, color='white')),
                        name='Value'
                    ))
                    # The Line (Global Average)
                    fig.add_vline(x=avg, line_width=3, line_color="#e15759")
                
                    fig.add_annotation(
                        x=0.5, y=-0.3, text=f"Global Avg: {avg:,.1f}", 
                        showarrow=False, font=dict(size=12, color="#e15759"), xref="paper", yref="paper"
                    )

                    fig.update_layout(
                        title={'text': title, 'font': {'size': 14}}, 
                        height=150, margin=dict(l=20, r=20, t=40, b=40),
                        yaxis=dict(visible=False, range=[-0.5, 0.5]),
                        xaxis=dict(range=[0, max_range]), showlegend=False, plot_bgcolor='white'
                    )
                    fig.update_xaxes(showgrid=True, gridcolor='#f0f0f0')
                    return fig

                fig_hr = create_comparison_chart(cust_data.get('current_heart_rate_bpm', 0), avg_hr, "Average Heart Rate vs. Global Average", 120)
                fig_claims = create_comparison_chart(cust_data.get('avg_annual_claims', 0), avg_claims, "Annual Claims vs. Global Average", 6000)
                fig_visits = create_comparison_chart(cust_data.get('avg_annual_doctor_visits', 0), avg_visits, "Average Doctor Visits vs. Global Average", 20)

                # --- FIG 6: FINANCIAL BALANCE ---
                fig_fin = go.Figure()
                # Expenses (Red)
                claim_amt = cust_data.get('lifetime_claims_amount', 0)
                fig_fin.add_trace(go.Bar(
                    y=['Balance'], x=[claim_amt * -1],
                    name='Lifetime Claims', orientation='h', marker_color='#e15759',
                    text=[f"${claim_amt:,.0f}"], textposition='inside'
                ))
                # Income (Green)
                prem_amt = cust_data.get('lifetime_premiums_paid', 0)
                fig_fin.add_trace(go.Bar(
                    y=['Balance'], x=[prem_amt],
                    name='Lifetime Premiums', orientation='h', marker_color='#59a14f',
                    text=[f"${prem_amt:,.0f}"], textposition='inside'
                ))
                fig_fin.update_layout(
                    title="Financial Balance", barmode='relative', height=200,
                    xaxis=dict(title='Amount ($)', tickformat='s'), yaxis=dict(visible=False),
                    legend=dict(orientation="h", y=-0.2)
                )

                customer_360_charts = [fig_stats, fig_lifestyle, fig_hr, fig_claims, fig_visits, fig_fin]
        
    elif selected_table == "dm_health_by_demographics":
        # Health by Demographics visualizations
        age_order = ['18-29', '30-39', '40-49', '50-59', '60-69', '70+']

        # FIG 1: Scatter (Sleep vs Cost)
        cost_col = next((c for c in df.columns if 'insurance' in c.lower() and 'cost' in c.lower()), 'avg_insurance_cost')
        scatter_data = df.groupby('age_group', observed=True).agg({
            'avg_sleep_hours': 'mean', cost_col: 'mean', 'avg_sleep_quality_score': 'sum' 
        }).reset_index()

        fig1 = px.scatter(
            scatter_data, x='avg_sleep_hours', y=cost_col, color='age_group', size='avg_sleep_quality_score',
            title='Effect of Average Sleep Hours on Insurance Cost by Age Group',
            labels={'avg_sleep_hours': 'Avg Sleep Hours', cost_col: 'Avg Insurance Cost ($)', 'age_group': 'Age Group'},
            category_orders={'age_group': age_order}, color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig1.update_traces(textposition='top center', text=scatter_data[cost_col].round(2))

        # FIG 2: Heatmap
        fig2 = px.density_heatmap(
            df, x='age_group', y='family_status', z='pct_with_sleep_disorder', histfunc='avg', 
            title='Average Percentage with Sleep Disorder by Age Group and Family Status',
            labels={'age_group': 'Age Group', 'family_status': 'Family Status', 'pct_with_sleep_disorder': '% With Disorder'},
            category_orders={'age_group': age_order}, color_continuous_scale='Teal' 
        )

        # FIG 3: Bar (Heart Rate)
        hr_by_demo = df.groupby(['age_group', 'gender'], observed=True)['avg_heart_rate_bpm'].mean().reset_index()
        fig3 = px.bar(
            hr_by_demo, x='age_group', y='avg_heart_rate_bpm', color='gender', barmode='group',
            title='Average Heart Rate by Age Group and Gender',
            labels={'avg_heart_rate_bpm': 'Avg Heart Rate (BPM)', 'age_group': 'Age Group'},
            category_orders={'age_group': age_order},
            color_discrete_map={'female': '#e15759', 'male': '#4e79a7', 'other': '#bab0ac'}
        )
        customer_360_charts = [fig1, fig2, fig3]
    elif selected_table == "dm_insurance_profitability":
        # Insurance Profitability visualizations
    
        # Initialize variables
        top_row_fig = go.Figure()
        middle_row_fig = go.Figure()
        # fig_final = go.Figure() # Placeholder for your new specific visual

        # ---------------------------------------------------------
        # DATA LOADING & PREP
        # ---------------------------------------------------------
        try:
            # Load raw data
            ts_raw_df = pd.read_csv('data/dm_customer_360.csv')
        
            # 1. RENAME OCCUPATIONS
            ts_raw_df['occupational_category'] = ts_raw_df['occupational_category'].replace({
                "it specialist": "IT-Specialist", "healthcare_worker": "Healthcare Worker",
                "office_worker": "Office Worker", "retail_worker": "Retail Worker",
                "self-employed": "Self-Employed", "student": "Student",
                "engineer": "Engineer", "nurse": "Nurse",
                "teacher": "Teacher", "unemployed": "Unemployed"
            })

            # 2. Date Conversion
            date_col = 'insurance_sign_up_date'
            if date_col not in ts_raw_df.columns:
                date_col = 'created_at'  
            ts_raw_df['temp_date'] = pd.to_datetime(ts_raw_df[date_col], errors='coerce')

            # ---------------------------------------------------------
            # TOP ROW: Time Series
            # ---------------------------------------------------------
            trend_df = ts_raw_df.groupby(ts_raw_df['temp_date'].dt.to_period("M").dt.to_timestamp())[[
                'lifetime_premiums_paid', 'lifetime_claims_amount'
            ]].sum().reset_index()
            trend_df.rename(columns={'temp_date': 'Date'}, inplace=True)
            trend_df['Loss Ratio %'] = (trend_df['lifetime_claims_amount'] / trend_df['lifetime_premiums_paid'].replace(0, 1)) * 100

            top_row_fig = make_subplots(
                rows=1, cols=2,
                subplot_titles=("Financial Performance: Premiums vs Claims", "Loss Ratio KPI (Trend)"),
                horizontal_spacing=0.15
            )

            # LEFT: Financials
            top_row_fig.add_trace(go.Scatter(x=trend_df['Date'], y=trend_df['lifetime_premiums_paid'], mode='lines', name='Premiums', stackgroup='one', line=dict(color='#d4b9da')), row=1, col=1)
            top_row_fig.add_trace(go.Scatter(x=trend_df['Date'], y=trend_df['lifetime_claims_amount'], mode='lines', name='Claims', stackgroup='one', line=dict(color='#4e79a7')), row=1, col=1)

            # RIGHT: Loss Ratio
            top_row_fig.add_trace(go.Scatter(x=trend_df['Date'], y=trend_df['Loss Ratio %'], mode='lines', name='Loss Ratio %', line=dict(color='#4e79a7', width=3)), row=1, col=2)
            top_row_fig.add_hline(y=60, line_dash="solid", line_color="gray", annotation_text="Limit (60%)", row=1, col=2)
        
            if not trend_df.empty:
                last_val = trend_df.iloc[-1]
                top_row_fig.add_annotation(
                    x=last_val['Date'], y=last_val['Loss Ratio %'],
                    text=f"{last_val['Loss Ratio %']:.1f}%",
                    showarrow=True, arrowhead=2, yshift=10, row=1, col=2
                )

            top_row_fig.update_layout(height=450, showlegend=True, margin=dict(l=50, r=20, t=60, b=20))
            top_row_fig.update_yaxes(title_text="Amount ($)", row=1, col=1)
            top_row_fig.update_yaxes(title_text="Loss Ratio (%)", row=1, col=2)

            # ---------------------------------------------------------
            # MIDDLE ROW: Deviation & Heatmap
            # ---------------------------------------------------------
        
            # Heatmap Prep
            def get_hr_category(bpm):
                if pd.isna(bpm): return "Unknown"
                if bpm > 100: return 'High'
                elif bpm < 60: return 'Low'
                else: return 'Normal'

            ts_raw_df['Heart Rate Category'] = ts_raw_df['current_heart_rate_bpm'].apply(get_hr_category)
            cost_matrix = ts_raw_df.groupby(['occupational_category', 'Heart Rate Category']).agg({
                'lifetime_premiums_paid': 'sum', 'lifetime_claims_amount': 'sum'
            }).reset_index()
            cost_matrix['Loss Ratio'] = cost_matrix['lifetime_claims_amount'] / cost_matrix['lifetime_premiums_paid']
            heatmap_data = cost_matrix.pivot(index='occupational_category', columns='Heart Rate Category', values='Loss Ratio')

            # Deviation Prep
            total_claims_global = ts_raw_df['lifetime_claims_amount'].sum()
            total_premiums_global = ts_raw_df['lifetime_premiums_paid'].sum()
            portfolio_avg = total_claims_global / total_premiums_global

            dev_df = ts_raw_df.groupby('occupational_category').agg({
                'lifetime_claims_amount': 'sum', 'lifetime_premiums_paid': 'sum'
            }).reset_index()
            dev_df['Segment Loss Ratio'] = dev_df['lifetime_claims_amount'] / dev_df['lifetime_premiums_paid']
            dev_df['Deviation'] = dev_df['Segment Loss Ratio'] - portfolio_avg
            dev_df = dev_df.sort_values('Deviation', ascending=True)
        
            # Reorder Heatmap
            sorted_occupations = dev_df['occupational_category'].tolist()
            heatmap_data = heatmap_data.reindex(sorted_occupations)

            middle_row_fig = make_subplots(
                rows=1, cols=2,
                subplot_titles=("Segment Deviation from Portfolio Average", "Cost Drivers by Health Profile"),
                column_widths=[0.6, 0.4], horizontal_spacing=0.15
            )

            colors = ['#e15759' if x > 0 else '#4e79a7' for x in dev_df['Deviation']]
        
            # Bar Chart
            middle_row_fig.add_trace(go.Bar(
                x=dev_df['Deviation'], y=dev_df['occupational_category'], orientation='h',
                marker_color=colors, text=dev_df['Deviation'], texttemplate="%{x:+.1%}", textposition='outside'
            ), row=1, col=1)

            # Heatmap
            middle_row_fig.add_trace(go.Heatmap(
                z=heatmap_data.values, x=heatmap_data.columns, y=heatmap_data.index, 
                colorscale='RdBu_r', text=heatmap_data.values, texttemplate="%{z:.1%}",
                colorbar=dict(title="Loss Ratio", x=1.05, thickness=10)
            ), row=1, col=2)

            middle_row_fig.update_layout(height=500, showlegend=False, margin=dict(l=180, r=50, t=50, b=50))
            middle_row_fig.update_yaxes(categoryorder='trace', row=1, col=1)
            middle_row_fig.update_yaxes(categoryorder='trace', row=1, col=2)
            middle_row_fig.update_xaxes(title_text="Deviation", row=1, col=1)
            middle_row_fig.update_xaxes(title_text="Risk Category", row=1, col=2)

            # ---------------------------------------------------------
            # BOTTOM ROW: Sankey Diagram (Occupation -> Health -> Status)
            # ---------------------------------------------------------
            # 1. Aggregate data for the flows
            # Flow 1: Occupation -> Health Status
            flow1 = ts_raw_df.groupby(['occupational_category', 'health_status']).size().reset_index(name='count')
            flow1.columns = ['Source', 'Target', 'Value']
        
            # Flow 2: Health Status -> Insurance Status
            flow2 = ts_raw_df.groupby(['health_status', 'insurance_status']).size().reset_index(name='count')
            flow2.columns = ['Source', 'Target', 'Value']

            # 2. Create unique labels for nodes
            all_nodes = list(pd.concat([flow1['Source'], flow1['Target'], flow2['Target']]).unique())
            node_map = {name: i for i, name in enumerate(all_nodes)}

            # 3. Map names to indices
            links = []
            # Add Link 1
            for _, row in flow1.iterrows():
                links.append({
                    'source': node_map[row['Source']],
                    'target': node_map[row['Target']],
                    'value': row['Value'],
                    'color': 'rgba(211, 211, 211, 0.5)' # Light gray links
                })
            # Add Link 2
            for _, row in flow2.iterrows():
                links.append({
                    'source': node_map[row['Source']],
                    'target': node_map[row['Target']],
                    'value': row['Value'],
                    'color': 'rgba(211, 211, 211, 0.5)'
                })

            link_df = pd.DataFrame(links)

            # 4. Create Sankey
            bottom_row_fig = go.Figure(data=[go.Sankey(
                node = dict(
                    pad = 15,
                    thickness = 20,
                    line = dict(color = "black", width = 0.5),
                    label = all_nodes,
                    color = "#4e79a7" # Blue nodes
                ),
                link = dict(
                    source = link_df['source'],
                    target = link_df['target'],
                    value = link_df['value'],
                    color = link_df['color']
                )
            )])

            bottom_row_fig.update_layout(
                title_text="Customer Journey: Occupation → Health Profile → Policy Status",
                height=500,
                font_size=12
            )

        except Exception as e:
            print(f"Could not load data: {e}")
            top_row_fig = go.Figure().update_layout(title="Error Loading Data")
            middle_row_fig = go.Figure().update_layout(title="Error Loading Data")
            bottom_row_fig = go.Figure().update_layout(title="Error Loading Data")

        customer_360_charts = [top_row_fig, middle_row_fig, bottom_row_fig]

    elif selected_table == "dm_insurance_profitability":
        # Insurance Profitability visualizations
    
        # Initialize variables
        top_row_fig = go.Figure()
        middle_row_fig = go.Figure()
        # fig_final = go.Figure() # Placeholder for your new specific visual

        # ---------------------------------------------------------
        # DATA LOADING & PREP
        # ---------------------------------------------------------
        try:
            # Load raw data
            ts_raw_df = pd.read_csv(os.path.join(data_dir, 'dm_customer_360.csv'))
        
            # 1. RENAME OCCUPATIONS
            ts_raw_df['occupational_category'] = ts_raw_df['occupational_category'].replace({
                "it specialist": "IT-Specialist", "healthcare_worker": "Healthcare Worker",
                "office_worker": "Office Worker", "retail_worker": "Retail Worker",
                "self-employed": "Self-Employed", "student": "Student",
                "engineer": "Engineer", "nurse": "Nurse",
                "teacher": "Teacher", "unemployed": "Unemployed"
            })

            # 2. Date Conversion
            date_col = 'insurance_sign_up_date'
            if date_col not in ts_raw_df.columns:
                date_col = 'created_at'  
            ts_raw_df['temp_date'] = pd.to_datetime(ts_raw_df[date_col], errors='coerce')

            # ---------------------------------------------------------
            # TOP ROW: Time Series
            # ---------------------------------------------------------
            trend_df = ts_raw_df.groupby(ts_raw_df['temp_date'].dt.to_period("M").dt.to_timestamp())[[
                'lifetime_premiums_paid', 'lifetime_claims_amount'
            ]].sum().reset_index()
            trend_df.rename(columns={'temp_date': 'Date'}, inplace=True)
            trend_df['Loss Ratio %'] = (trend_df['lifetime_claims_amount'] / trend_df['lifetime_premiums_paid'].replace(0, 1)) * 100

            top_row_fig = make_subplots(
                rows=1, cols=2,
                subplot_titles=("Financial Performance: Premiums vs Claims", "Loss Ratio KPI (Trend)"),
                horizontal_spacing=0.15
            )

            # LEFT: Financials
            top_row_fig.add_trace(go.Scatter(x=trend_df['Date'], y=trend_df['lifetime_premiums_paid'], mode='lines', name='Premiums', stackgroup='one', line=dict(color='#d4b9da')), row=1, col=1)
            top_row_fig.add_trace(go.Scatter(x=trend_df['Date'], y=trend_df['lifetime_claims_amount'], mode='lines', name='Claims', stackgroup='one', line=dict(color='#4e79a7')), row=1, col=1)

            # RIGHT: Loss Ratio
            top_row_fig.add_trace(go.Scatter(x=trend_df['Date'], y=trend_df['Loss Ratio %'], mode='lines', name='Loss Ratio %', line=dict(color='#4e79a7', width=3)), row=1, col=2)
            top_row_fig.add_hline(y=60, line_dash="solid", line_color="gray", annotation_text="Limit (60%)", row=1, col=2)
        
            if not trend_df.empty:
                last_val = trend_df.iloc[-1]
                top_row_fig.add_annotation(
                    x=last_val['Date'], y=last_val['Loss Ratio %'],
                    text=f"{last_val['Loss Ratio %']:.1f}%",
                    showarrow=True, arrowhead=2, yshift=10, row=1, col=2
                )

            top_row_fig.update_layout(height=450, showlegend=True, margin=dict(l=50, r=20, t=60, b=20))
            top_row_fig.update_yaxes(title_text="Amount ($)", row=1, col=1)
            top_row_fig.update_yaxes(title_text="Loss Ratio (%)", row=1, col=2)

            # ---------------------------------------------------------
            # MIDDLE ROW: Deviation & Heatmap
            # ---------------------------------------------------------
        
            # Heatmap Prep
            def get_hr_category(bpm):
                if pd.isna(bpm): return "Unknown"
                if bpm > 100: return 'High'
                elif bpm < 60: return 'Low'
                else: return 'Normal'

            ts_raw_df['Heart Rate Category'] = ts_raw_df['current_heart_rate_bpm'].apply(get_hr_category)
            cost_matrix = ts_raw_df.groupby(['occupational_category', 'Heart Rate Category']).agg({
                'lifetime_premiums_paid': 'sum', 'lifetime_claims_amount': 'sum'
            }).reset_index()
            cost_matrix['Loss Ratio'] = cost_matrix['lifetime_claims_amount'] / cost_matrix['lifetime_premiums_paid']
            heatmap_data = cost_matrix.pivot(index='occupational_category', columns='Heart Rate Category', values='Loss Ratio')

            # Deviation Prep
            total_claims_global = ts_raw_df['lifetime_claims_amount'].sum()
            total_premiums_global = ts_raw_df['lifetime_premiums_paid'].sum()
            portfolio_avg = total_claims_global / total_premiums_global

            dev_df = ts_raw_df.groupby('occupational_category').agg({
                'lifetime_claims_amount': 'sum', 'lifetime_premiums_paid': 'sum'
            }).reset_index()
            dev_df['Segment Loss Ratio'] = dev_df['lifetime_claims_amount'] / dev_df['lifetime_premiums_paid']
            dev_df['Deviation'] = dev_df['Segment Loss Ratio'] - portfolio_avg
            dev_df = dev_df.sort_values('Deviation', ascending=True)
        
            # Reorder Heatmap
            sorted_occupations = dev_df['occupational_category'].tolist()
            heatmap_data = heatmap_data.reindex(sorted_occupations)

            middle_row_fig = make_subplots(
                rows=1, cols=2,
                subplot_titles=("Segment Deviation from Portfolio Average", "Cost Drivers by Health Profile"),
                column_widths=[0.6, 0.4], horizontal_spacing=0.15
            )

            colors = ['#e15759' if x > 0 else '#4e79a7' for x in dev_df['Deviation']]
        
            # Bar Chart
            middle_row_fig.add_trace(go.Bar(
                x=dev_df['Deviation'], y=dev_df['occupational_category'], orientation='h',
                marker_color=colors, text=dev_df['Deviation'], texttemplate="%{x:+.1%}", textposition='outside'
            ), row=1, col=1)

            # Heatmap
            middle_row_fig.add_trace(go.Heatmap(
                z=heatmap_data.values, x=heatmap_data.columns, y=heatmap_data.index, 
                colorscale='RdBu_r', text=heatmap_data.values, texttemplate="%{z:.1%}",
                colorbar=dict(title="Loss Ratio", x=1.05, thickness=10)
            ), row=1, col=2)

            middle_row_fig.update_layout(height=500, showlegend=False, margin=dict(l=180, r=50, t=50, b=50))
            middle_row_fig.update_yaxes(categoryorder='trace', row=1, col=1)
            middle_row_fig.update_yaxes(categoryorder='trace', row=1, col=2)
            middle_row_fig.update_xaxes(title_text="Deviation", row=1, col=1)
            middle_row_fig.update_xaxes(title_text="Risk Category", row=1, col=2)

            # ---------------------------------------------------------
            # BOTTOM ROW: Sankey Diagram (Occupation -> Health -> Status)
            # ---------------------------------------------------------
            # 1. Aggregate data for the flows
            # Flow 1: Occupation -> Health Status
            flow1 = ts_raw_df.groupby(['occupational_category', 'health_status']).size().reset_index(name='count')
            flow1.columns = ['Source', 'Target', 'Value']
        
            # Flow 2: Health Status -> Insurance Status
            flow2 = ts_raw_df.groupby(['health_status', 'insurance_status']).size().reset_index(name='count')
            flow2.columns = ['Source', 'Target', 'Value']

            # 2. Create unique labels for nodes
            all_nodes = list(pd.concat([flow1['Source'], flow1['Target'], flow2['Target']]).unique())
            node_map = {name: i for i, name in enumerate(all_nodes)}

            # 3. Map names to indices
            links = []
            # Add Link 1
            for _, row in flow1.iterrows():
                links.append({
                    'source': node_map[row['Source']],
                    'target': node_map[row['Target']],
                    'value': row['Value'],
                    'color': 'rgba(211, 211, 211, 0.5)' # Light gray links
                })
            # Add Link 2
            for _, row in flow2.iterrows():
                links.append({
                    'source': node_map[row['Source']],
                    'target': node_map[row['Target']],
                    'value': row['Value'],
                    'color': 'rgba(211, 211, 211, 0.5)'
                })

            link_df = pd.DataFrame(links)

            # 4. Create Sankey
            bottom_row_fig = go.Figure(data=[go.Sankey(
                node = dict(
                    pad = 15,
                    thickness = 20,
                    line = dict(color = "black", width = 0.5),
                    label = all_nodes,
                    color = "#4e79a7" # Blue nodes
                ),
                link = dict(
                    source = link_df['source'],
                    target = link_df['target'],
                    value = link_df['value'],
                    color = link_df['color']
                )
            )])

            bottom_row_fig.update_layout(
                title_text="Customer Journey: Occupation → Health Profile → Policy Status",
                height=500,
                font_size=12
            )

        except Exception as e:
            print(f"Could not load data: {e}")
            top_row_fig = go.Figure().update_layout(title="Error Loading Data")
            middle_row_fig = go.Figure().update_layout(title="Error Loading Data")
            bottom_row_fig = go.Figure().update_layout(title="Error Loading Data")

        customer_360_charts = [top_row_fig, middle_row_fig, bottom_row_fig]

    elif selected_table == "dm_sleep_health_analysis":
        # Sleep Health visualizations
        fig1 = px.box(df, x='sleep_disorder', y=['avg_sleep_hours', 'avg_sleep_quality_score'], title='Sleep Metrics by Disorder Type', points='all')
        fig2 = px.scatter(df, x='avg_daily_steps', y='avg_sleep_quality_score', color='activity_level', size='unique_persons', title='Daily Steps vs Sleep Quality')
        fig3 = px.bar(df.groupby('stress_level').agg({'avg_sleep_hours': 'mean', 'pct_sleep_deprived': 'mean'}).reset_index(), x='stress_level', y=['avg_sleep_hours', 'pct_sleep_deprived'], title='Sleep Metrics by Stress Level', barmode='group')
        fig4 = px.scatter(df, x='avg_heart_rate_bpm', y='avg_blood_oxygen_pct', color='sleep_disorder', size='unique_persons', title='Heart Rate vs Blood Oxygen')
        customer_360_charts = [fig1, fig2, fig3, fig4]

    elif selected_table == "dm_data_quality_dashboard":
        # Data Quality Dashboard visualizations

        overall_row = df[
            (df['data_source'] == 'All Sources') & 
            (df['quality_dimension'] == 'Overall')
        ].iloc[0]

        # Metric calculation - Missing Rows
        avg_missing = (overall_row['missing_blood_oxygen_pct'] + overall_row['missing_stress_level_pct']) / 2
        completeness_score = 100 - avg_missing
    
        # Error Counts for Donut
        error_counts = {
            "Missing Data": overall_row['missing_blood_oxygen_count'] + overall_row['missing_stress_level_count'],
            "Extreme/Anomalies": (
                overall_row['extreme_heart_rate_count'] + 
                overall_row['extreme_sleep_hours_count'] + 
                overall_row['extreme_step_count_count'] + 
                overall_row['excessive_claims_count']
            ),
            "Invalid Format": (
                overall_row['invalid_heart_rate_count'] + 
                overall_row['invalid_steps_count'] + 
                overall_row['invalid_blood_oxygen_count']
            )
        }
        total_errors = sum(error_counts.values())

        # Subplots created
        kpi_fig = make_subplots(
            rows=1, cols=3,
            specs=[[{'type': 'domain'}, {'type': 'domain'}, {'type': 'domain'}]],
            subplot_titles=("Overall Quality Score", "Data Completeness", "Quality Issues Distribution")
        )

        # COLUMN 1: Overall Quality Gauge
        kpi_fig.add_trace(go.Indicator(
            mode="gauge+number+delta",
            value=overall_row['overall_quality_score'],
            delta={'reference': 99.0, 'position': "top", 'suffix': "%"},
            gauge={
                'axis': {'range': [90, 100]},
                'bar': {'color': "#59a14f"},
                'steps': [
                    {'range': [90, 98], 'color': "#f28e2b"},
                    {'range': [98, 100], 'color': "#f1f1f1"}
                ],
                'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 99.0}
            }
        ), row=1, col=1)

        # COLUMN 2: Data Completeness Gauge
        kpi_fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=completeness_score,
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#4e79a7"},
                'steps': [{'range': [0, 95], 'color': "#e5e5e5"}]
            }
        ), row=1, col=2)

        # COLUMN 3: Error Composition Donut
        kpi_fig.add_trace(go.Pie(
            values=list(error_counts.values()),
            labels=list(error_counts.keys()),
            hole=0.6,
            marker_colors=px.colors.qualitative.Pastel
        ), row=1, col=3)

        # Add total error count in the center of the donut
        kpi_fig.add_annotation(
            text=f"{int(total_errors):,}", 
            x=0.88, y=0.5, # Approximate center of 3rd plot
            font_size=20, showarrow=False, xref="paper", yref="paper"
        )
    
        # Clean up layout
        kpi_fig.update_layout(height=350, margin=dict(l=20, r=20, t=50, b=20))

        scorecard_df = df[
            (df['data_source'] == 'By Occupation') | 
            (df['data_source'] == 'All Sources')
        ].copy()

        scorecard_df['quality_dimension'] = scorecard_df['quality_dimension'].replace({
                "it specialist": "IT-Specialist",
                "healthcare_worker": "Healthcare Worker",
                "office_worker": "Office Worker",
                "retail_worker": "Retail Worker",
                "self-employed": "Self-Employed",
                "student": "Student",
                "engineer": "Engineer",
                "nurse": "Nurse",
                "teacher": "Teacher",
                "unemployed": "Unemployed",
                "Overall": " OVERALL BENCHMARK"
            })

        def categorize_quality(row):
            if row['quality_dimension'].strip() == "OVERALL BENCHMARK":
                return "BENCHMARK"
            
            score = row['overall_quality_score']    
            if score > 99.25:
                return "PERFECT (>99.25-100%)"
            elif score >= 99.0:
                return "EXCELLENT (99%-99.25%)"
            else:
                return "GOOD (98.8%-99%)"

        scorecard_df['Quality Alert'] = scorecard_df.apply(categorize_quality, axis=1)
        scorecard_df = scorecard_df.sort_values('overall_quality_score', ascending=True)

        # 4. Plot
        fig4 = px.bar(
            scorecard_df,
            x="overall_quality_score",
            y="quality_dimension",
            color="Quality Alert",
            title="Segment Reliability Scorecard (vs Benchmark)",
            orientation='h',
            color_discrete_map={
                "PERFECT (>99.25-100%)": "#59a14f",  # Dark Green
                "EXCELLENT (99%-99.25%)": "#8cd17d", # Light Green
                "GOOD (98.8%-99%)": "#bab0ac",       # Grey
                "BENCHMARK": "#4e79a7"               # Blue (Distinct color for Overall)
            },
            labels={
                "overall_quality_score": "Quality Score",
                "quality_dimension": "Segment"
            }
        )
    
        fig4.update_layout(xaxis_range=[98, 100])

        # 5. Hygiene Matrix Heatmap
        metric_cols = [
            'missing_blood_oxygen_pct',
            'missing_stress_level_pct',
            'invalid_blood_oxygen_pct', 
            'invalid_heart_rate_pct',
            'invalid_steps_pct',
            'extreme_heart_rate_pct',
            'extreme_sleep_hours_pct',
            'extreme_step_count_pct',
            'excessive_claims_pct'
        ]

        # Filter to focus on occupations
        heatmap_df = df[
            (df['data_source'] == 'By Occupation') | 
            (df['data_source'] == 'All Sources')
        ].copy()

        # Rename rows for better readability
        heatmap_df['quality_dimension'] = heatmap_df['quality_dimension'].replace({
            "it specialist": "IT-Specialist",
            "healthcare_worker": "Healthcare Worker",
            "office_worker": "Office Worker",
            "retail_worker": "Retail Worker",
            "self-employed": "Self-Employed",
            "student": "Student",
            "engineer": "Engineer",
            "nurse": "Nurse",
            "teacher": "Teacher",
            "unemployed": "Unemployed",
            "Overall": "TOTAL (Average)"
        })

        overall_row = heatmap_df[heatmap_df['data_source'] == 'All Sources']
        occupations = heatmap_df[heatmap_df['data_source'] == 'By Occupation']
        occupations_sorted = occupations.sort_values('overall_quality_score', ascending=True)
        heatmap_sorted = pd.concat([overall_row, occupations_sorted])
        final_row_order = heatmap_sorted['quality_dimension'].tolist()
        # Sort columns
        avg_errors = heatmap_df[metric_cols].mean()
        sorted_metrics = avg_errors.sort_values(ascending=False).index.tolist()
        clean_col_map = {m: m.replace('_pct', '').replace('_', ' ').title() for m in sorted_metrics}
        col_order = [clean_col_map[m] for m in sorted_metrics]

        # Melt dataframe
        heatmap_melted = heatmap_df.melt(
            id_vars=['quality_dimension'], 
            value_vars=metric_cols,
            var_name='Metric',
            value_name='Error Rate (%)'
        )
        heatmap_melted['Metric'] = heatmap_melted['Metric'].map(lambda x: x.replace('_pct', '').replace('_', ' ').title())

        fig5 = px.density_heatmap(
            heatmap_melted,
            x="Metric",
            y="quality_dimension",
            z="Error Rate (%)",
            title="Field-Level Hygiene Matrix",
            color_continuous_scale="OrRd",
            labels={"quality_dimension": "Segment", "Metric": "Quality Indicator"},
            category_orders={
                "quality_dimension": final_row_order, 
                "Metric": col_order
            }
        )
    
        fig5.update_traces(texttemplate="%{z:.1f}", textfont={"size": 10})

        # 6. Self-report vs actuals
        # Clustering logic
        fig6 = None 

        try:
            # 1. Load data
            raw_df = pd.read_csv('data/dm_customer_360.csv')
        
            # 2. Clean data
            activity_mapper = {
                "sedentary": 1, "seddentary": 1,
                "active": 2, "actve": 2,
                "highly_active": 3, "highly active": 3
            }
            raw_df['activity_level_numeric'] = raw_df['current_activity_level'].str.lower().map(activity_mapper).fillna(0)

            # 3. Classify Anomalies 
            def classify_anomaly(row):
                level = row['activity_level_numeric']
                steps = row.get('current_daily_steps', 0)

                if level == 3 and steps < 4000:
                    return "Over-Reporter"       # Matches your screenshot
                elif level == 1 and steps > 8000:
                    return "Under-Reporter"      # Matches your screenshot
                elif level == 3 and steps >= 8000:
                    return "Verified Active"
                elif level == 1 and steps <= 4000:
                    return "Verified Sedentary"
                else:
                    return "Normal Range"

            raw_df['Anomaly Status'] = raw_df.apply(classify_anomaly, axis=1)



            # 4. Define the Exact Order
            custom_order = [
                "Over-Reporter", 
                "Under-Reporter", 
                "Normal Range", 
                "Verified Sedentary", 
                "Verified Active"
            ]

            # 5. Plot
            fig6 = px.strip(
                raw_df,
                x="activity_level_numeric",
                y="current_daily_steps",
                color="Anomaly Status",
                title="Anomaly Detection: Actual vs. Reported Activity",
                stripmode='overlay',
                color_discrete_map={
                    "Over-Reporter": "#e15759",      # Red
                    "Under-Reporter": "#f28e2b",     # Orange
                    "Normal Range": "#bab0ac",       # Grey
                    "Verified Sedentary": "#76b7b2", # Teal/Grey
                    "Verified Active": "#59a14f"     # Green
                },
                category_orders={"Anomaly Status": custom_order},
                labels={
                    "activity_level_numeric": "Activity Level",
                    "current_daily_steps": "Recorded Daily Steps"
                }
            )
        
            # Add threshold lines
            fig6.add_hline(y=4000, line_dash="dash", line_color="gray", annotation_text="Sedentary Threshhold (<4k)")
            fig6.add_hline(y=8000, line_dash="dash", line_color="gray", annotation_text="Active Threshhold (>8k)")
            fig6.update_xaxes(tickvals=[1, 2, 3])

        except Exception as e:
            print(f"Could not generate Anomaly Chart: {e}")
    
        # Update the list
        customer_360_charts = [kpi_fig, fig4, fig5]
        if fig6:
            customer_360_charts.append(fig6)

    else:
        customer_360_charts = []
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
