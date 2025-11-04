import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt

# Page configuration
st.set_page_config(
    page_title="Social Media & Mental Health Analysis",
    page_icon="🧠",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# Title and description
st.title("🧠 Social Media & Mental Health Dashboard")
st.markdown("""
    This interactive dashboard explores the relationship between social media usage patterns
    and mental health indicators across different demographics.
""")

# Load and prepare data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('Mental_Health_and_Social_Media_Balance_Dataset.csv')
        # Create age ranges
        bins = [10, 20, 25, 30, 35, 40, 50, 100]
        labels = ["15-20", "21-25", "26-30", "31-35", "36-40", "41-50", "50+"]
        df["Age_Range"] = pd.cut(df["Age"], bins=bins, labels=labels, include_lowest=True)
        return df
    except FileNotFoundError:
        st.error("Error: The data file 'Mental_Health_and_Social_Media_Balance_Dataset.csv' was not found. Please make sure it's in the same directory as the dashboard.")
        return None
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

df = load_data()
if df is None:
    st.stop()

# Sidebar filters
st.sidebar.header("📊 Filters")

# Add filters
selected_platform = st.sidebar.multiselect(
    "Social Media Platform",
    options=df["Social_Media_Platform"].unique(),
    default=df["Social_Media_Platform"].unique()
)

selected_age_range = st.sidebar.multiselect(
    "Age Range",
    options=df["Age_Range"].unique(),
    default=df["Age_Range"].unique()
)

selected_gender = st.sidebar.multiselect(
    "Gender",
    options=df["Gender"].unique(),
    default=df["Gender"].unique()
)

# Filter the dataframe
filtered_df = df[
    (df["Social_Media_Platform"].isin(selected_platform)) &
    (df["Age_Range"].isin(selected_age_range)) &
    (df["Gender"].isin(selected_gender))
]

# Key Metrics Section
st.header("📈 Key Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Average Happiness",
        f"{filtered_df['Happiness_Index(1-10)'].mean():.2f}",
        f"{filtered_df['Happiness_Index(1-10)'].mean() - df['Happiness_Index(1-10)'].mean():.2f}"
    )

with col2:
    st.metric(
        "Average Stress Level",
        f"{filtered_df['Stress_Level(1-10)'].mean():.2f}",
        f"{df['Stress_Level(1-10)'].mean() - filtered_df['Stress_Level(1-10)'].mean():.2f}"
    )

with col3:
    st.metric(
        "Avg Screen Time (hrs)",
        f"{filtered_df['Daily_Screen_Time(hrs)'].mean():.2f}",
        f"{filtered_df['Daily_Screen_Time(hrs)'].mean() - df['Daily_Screen_Time(hrs)'].mean():.2f}"
    )

with col4:
    st.metric(
        "Avg Exercise (weekly)",
        f"{filtered_df['Exercise_Frequency(week)'].mean():.2f}",
        f"{filtered_df['Exercise_Frequency(week)'].mean() - df['Exercise_Frequency(week)'].mean():.2f}"
    )

# Create tabs for different analyses
tab1, tab2, tab3 = st.tabs(["📱 Platform Analysis", "🎯 Mental Health Insights", "📊 Demographics"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        # Platform Distribution
        fig_platform = px.pie(
            filtered_df,
            names="Social_Media_Platform",
            title="Social Media Platform Distribution",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig_platform, use_container_width=True)
    
    with col2:
        # Screen Time by Platform
        fig_screen_time = px.box(
            filtered_df,
            x="Social_Media_Platform",
            y="Daily_Screen_Time(hrs)",
            color="Social_Media_Platform",
            title="Screen Time Distribution by Platform"
        )
        st.plotly_chart(fig_screen_time, use_container_width=True)

with tab2:
    col1, col2 = st.columns(2)
    
    with col1:
        # Happiness vs Screen Time
        try:
            fig_happiness = px.scatter(
                filtered_df,
                x="Daily_Screen_Time(hrs)",
                y="Happiness_Index(1-10)",
                color="Social_Media_Platform",
                size="Exercise_Frequency(week)",
                title="Happiness Index vs Screen Time",
                trendline="lowess",  # Using lowess instead of ols as it doesn't require statsmodels
                trendline_options=dict(frac=0.5)
            )
        except Exception:
            # Fallback without trendline if there's any error
            fig_happiness = px.scatter(
                filtered_df,
                x="Daily_Screen_Time(hrs)",
                y="Happiness_Index(1-10)",
                color="Social_Media_Platform",
                size="Exercise_Frequency(week)",
                title="Happiness Index vs Screen Time"
            )
        
        # Add custom layout
        fig_happiness.update_layout(
            xaxis_title="Daily Screen Time (hours)",
            yaxis_title="Happiness Index (1-10)",
            legend_title="Social Media Platform",
            plot_bgcolor="white"
        )
        st.plotly_chart(fig_happiness, use_container_width=True)
    
    with col2:
        # Radar Chart for Mental Health Indicators
        categories = ['Sleep_Quality(1-10)', 'Stress_Level(1-10)', 
                     'Happiness_Index(1-10)', 'Exercise_Frequency(week)']
        
        fig_radar = go.Figure()
        
        for platform in selected_platform:
            platform_data = filtered_df[filtered_df['Social_Media_Platform'] == platform]
            values = platform_data[categories].mean().tolist()
            values += values[:1]
            
            fig_radar.add_trace(go.Scatterpolar(
                r=values,
                theta=categories + [categories[0]],
                name=platform,
                fill='toself'
            ))
        
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
            showlegend=True,
            title="Mental Health Indicators by Platform"
        )
        st.plotly_chart(fig_radar, use_container_width=True)

with tab3:
    col1, col2 = st.columns(2)
    
    with col1:
        # Age Distribution
        fig_age = px.histogram(
            filtered_df,
            x="Age_Range",
            color="Gender",
            title="Age Distribution by Gender",
            barmode="group"
        )
        st.plotly_chart(fig_age, use_container_width=True)
    
    with col2:
        # Exercise vs Stress Level by Gender
        fig_exercise = px.scatter(
            filtered_df,
            x="Exercise_Frequency(week)",
            y="Stress_Level(1-10)",
            color="Gender",
            size="Daily_Screen_Time(hrs)",
            title="Exercise Frequency vs Stress Level"
        )
        st.plotly_chart(fig_exercise, use_container_width=True)

# Correlation Analysis
st.header("🔄 Correlation Analysis")
numeric_cols = filtered_df.select_dtypes(include=[np.number]).columns
corr = filtered_df[numeric_cols].corr()

fig_corr = go.Figure(data=go.Heatmap(
    z=corr,
    x=numeric_cols,
    y=numeric_cols,
    text=corr.round(2),
    texttemplate='%{text}',
    textfont={"size": 10},
    hoverongaps=False,
    colorscale='RdBu_r',
    zmin=-1,
    zmax=1
))

fig_corr.update_layout(
    title="Correlation Heatmap of Numeric Variables",
    xaxis_title="Features",
    yaxis_title="Features",
    width=800,
    height=800
)

st.plotly_chart(fig_corr, use_container_width=True)

# Data Summary
with st.expander("Show Data Summary"):
    st.dataframe(filtered_df.describe())

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center'>
        Dashboard created for Social Media and Mental Health Analysis
    </div>
""", unsafe_allow_html=True)