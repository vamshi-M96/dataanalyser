import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Set page configuration
st.set_page_config(page_title="📊 Dataset Analyzer", layout="wide")

# Title and Description
st.markdown("<h1 style='text-align: center; font-size: 62px;'>📊 Dataset Analyzer</h1>", unsafe_allow_html=True)
st.markdown("""
This app allows you to upload a dataset (CSV or Excel format) and automatically:
- Identify data types
- Display summaries of missing and unique values
- Visualize individual columns with appropriate plots
- Explore relationships using correlation and categorical comparisons
""")

# File Upload
uploaded_file = st.sidebar.file_uploader("📂 Upload CSV/XLSX File", type=["csv", "xlsx"])

# Process File
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Failed to load file: {e}")
        st.stop()

    # Try to convert date/time columns automatically
    for col in df.columns:
        if "date" in col.lower() or "time" in col.lower():
            try:
                df[col] = pd.to_datetime(df[col])
            except:
                pass

    # Identify column types
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    categorical_cols = df.select_dtypes(include='object').columns.tolist()
    datetime_cols = df.select_dtypes(include='datetime64').columns.tolist()

    # Sidebar Column Info
    st.sidebar.markdown("### 🧮 Column Types")
    if numeric_cols:
        st.sidebar.markdown(f"**Numeric Columns ({len(numeric_cols)}):**")
        for col in numeric_cols:
            st.sidebar.write(f"- {col}")

    if categorical_cols:
        st.sidebar.markdown(f"**Categorical Columns ({len(categorical_cols)}):**")
        for col in categorical_cols:
            st.sidebar.write(f"- {col}")

    if datetime_cols:
        st.sidebar.markdown(f"**Datetime Columns ({len(datetime_cols)}):**")
        for col in datetime_cols:
            st.sidebar.write(f"- {col}")

    # Sidebar correlation filter
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📈 Correlation-Based Column Filter")
    if numeric_cols:
        corr_base_col = st.sidebar.selectbox("Select base column", numeric_cols)
        corr_threshold = st.sidebar.slider("Minimum correlation (absolute)", 0.0, 1.0, 0.3, 0.05)

        corr_matrix = df[numeric_cols].corr()
        if corr_base_col in corr_matrix.columns:
            corr_series = corr_matrix[corr_base_col].drop(corr_base_col)
            selected_corr_cols = corr_series[abs(corr_series) >= corr_threshold].index.tolist()
            selected_columns = [corr_base_col] + selected_corr_cols
            numeric_cols = list(set(numeric_cols).intersection(selected_columns))

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Overview", "📊 Numeric Columns", "🔤 Categorical Columns", "📈 Correlation Heatmap"])

    # Overview Tab
    with tab1:
        st.subheader("🔍 Dataset Overview")
        st.dataframe(df.head())

        summary = pd.DataFrame({
            'Missing': df.isnull().sum(),
            'Unique': df.nunique()
        })
        st.write("### Column Summary")
        st.dataframe(summary)

        if categorical_cols:
            st.write("### 🧠 Unique Value Distribution (Top 20)")
            for col in categorical_cols:
                if col in df.columns:
                    with st.expander(f"🔠 {col} ({df[col].nunique()} unique values)"):
                        vc = df[col].fillna("Missing").value_counts(dropna=False).head(20)
                        percent = (vc / len(df) * 100).round(2)
                        summary_df = pd.DataFrame({
                            "Value": vc.index,
                            "Count": vc.values,
                            "% of Total": percent.values
                        })
                        st.dataframe(summary_df)

        st.write("### Missing Values Heatmap")
        fig, ax = plt.subplots()
        sns.heatmap(df.isnull(), cbar=False, cmap="viridis", ax=ax)
        st.pyplot(fig)

    # Numeric Columns Tab
    with tab2:
        st.subheader("📊 Visualizations for Numeric Columns")
        for col in numeric_cols:
            st.markdown(f"### {col}")
            col1, col2, col3 = st.columns(3)
            with col1:
                fig, ax = plt.subplots()
                sns.histplot(df[col], bins=30, ax=ax)
                ax.set_title("Histogram")
                st.pyplot(fig)
            with col2:
                fig, ax = plt.subplots()
                sns.kdeplot(df[col], fill=True, ax=ax)
                ax.set_title("KDE Plot")
                st.pyplot(fig)
            with col3:
                fig, ax = plt.subplots()
                sns.boxplot(x=df[col], ax=ax)
                ax.set_title("Boxplot")
                st.pyplot(fig)

            st.markdown("### 🔗 Correlation with Other Numeric Columns")
            try:
                corr_vals = df[numeric_cols].corr()[col].drop(col).sort_values(ascending=False)
                st.dataframe(corr_vals.to_frame(name="Correlation"))
            except Exception as e:
                st.warning(f"Could not compute correlation for {col}: {e}")

    # Categorical Columns Tab
    with tab3:
        st.subheader("🔤 Categorical Columns vs Numeric Columns")
        for col in categorical_cols:
            if df[col].nunique() <= 20:
                for num in numeric_cols:
                    fig, ax = plt.subplots()
                    sns.boxplot(data=df, x=col, y=num, ax=ax)
                    ax.set_title(f"{num} by {col}")
                    plt.xticks(rotation=30)
                    st.pyplot(fig)
            else:
                st.info(f"⚠️ {col} has too many unique values to plot.")

    # Correlation Heatmap Tab
    with tab4:
        st.subheader("📈 Correlation Heatmap")
        if len(numeric_cols) >= 2:
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.heatmap(df[numeric_cols].corr(), annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
            st.pyplot(fig)
        else:
            st.info("Not enough numeric columns for correlation heatmap.")

else:
    st.info("👈 Upload a dataset from the sidebar to start analysis.")