# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.15",
# ]
# ///

import marimo

__generated_with = "0.19.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return mo


@app.cell
def _(mo):
    mo.md("""
    # 📈 Tableau Health Analysis Dashboard
    
    Interactive health analysis dashboard embedded from Tableau.
    """)
    return


@app.cell
def _(mo):
    tableau_url = "https://dub01.online.tableau.com/t/bipm_dwh_2025/views/HealthAnalystDashboard/Dashboard2?:showVizHome=no&:embed=true&:device=desktop&:tabs=yes"
    
    mo.Html(f"""
        <iframe 
            src="{tableau_url}" 
            style="width: 100%; height: 1200px; border: none; border-radius: 8px;">
        </iframe>
    """)
    return


if __name__ == "__main__":
    app.run()
