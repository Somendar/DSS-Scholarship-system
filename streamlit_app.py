"""
Streamlit App for Scholarship Decision Support System
Interactive interface for scholarship allocation decisions
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data_processor import ScholarshipDataProcessor
from dss_engine import ScholarshipDSS

# Page configuration
st.set_page_config(
    page_title="Scholarship Allocation DSS",
    page_icon="🎓",
    layout="wide"
)

# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
    st.session_state.df_original = None
    st.session_state.df_processed = None

def main():
    st.title("🎓 Scholarship Allocation Decision Support System")
    st.markdown("""
    This transparent DSS helps allocate scholarships fairly based on:
    - **Academic Merit** (Performance, Previous Scores)
    - **Financial Need** (Income, Parent Education)
    - **Student Engagement** (Attendance, Activities)
    """)
    
    # Sidebar for controls
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # File upload
        st.subheader("1. Upload Data")
        uploaded_file = st.file_uploader(
            "Upload StudentPerformance.csv",
            type=['csv']
        )
        
        # Weight adjustment sliders
        st.subheader("2. Adjust Weights")
        st.markdown("*Weights must sum to 100%*")
        
        academic_weight = st.slider(
            "Academic Merit Weight",
            min_value=0,
            max_value=100,
            value=40,
            step=5,
            help="Importance of academic performance"
        )
        
        financial_weight = st.slider(
            "Financial Need Weight",
            min_value=0,
            max_value=100,
            value=40,
            step=5,
            help="Importance of financial circumstances"
        )
        
        engagement_weight = st.slider(
            "Engagement Weight",
            min_value=0,
            max_value=100,
            value=20,
            step=5,
            help="Importance of student engagement"
        )
        
        # Validate weights
        total_weight = academic_weight + financial_weight + engagement_weight
        if total_weight != 100:
            st.error(f"⚠️ Weights sum to {total_weight}%. Must equal 100%!")
        else:
            st.success(f"✅ Weights sum to 100%")
        
        # Decision thresholds
        st.subheader("3. Decision Thresholds")
        full_threshold = st.slider(
            "Full Scholarship Threshold",
            min_value=70,
            max_value=95,
            value=80,
            help="Minimum score for full scholarship"
        )
        
        partial_threshold = st.slider(
            "Partial Scholarship Threshold",
            min_value=50,
            max_value=full_threshold-1,
            value=60,
            help="Minimum score for partial scholarship"
        )
    
    # Main content
    if uploaded_file is not None:
        # Load and process data
        if not st.session_state.data_loaded or uploaded_file != st.session_state.get('last_file'):
            with st.spinner("Loading and enhancing dataset..."):
                processor = ScholarshipDataProcessor()
                df_enhanced = processor.load_and_enhance_data(uploaded_file)
                df_processed = processor.preprocess_data(df_enhanced)
                
                st.session_state.df_original = df_enhanced
                st.session_state.df_processed = df_processed
                st.session_state.data_loaded = True
                st.session_state.last_file = uploaded_file
        
        df_processed = st.session_state.df_processed
        df_original = st.session_state.df_original
        
        # Calculate scores with current weights
        if total_weight == 100:
            dss = ScholarshipDSS(
                academic_weight=academic_weight/100,
                financial_weight=financial_weight/100,
                engagement_weight=engagement_weight/100
            )
            
            df_scored = dss.calculate_final_score(df_processed)
            
            # Apply decision rules (simple, transparent, DSS-safe)
            df_scored['recommendation'] = pd.cut(
                df_scored['final_score'],
                bins=[0, partial_threshold, full_threshold, 100],
                labels=['Not Eligible', 'Partial Scholarship', 'Full Scholarship'],
                include_lowest=True
                )


            
            # Simpler approach
            df_scored['recommendation'] = pd.cut(
                df_scored['final_score'],
                bins=[0, partial_threshold, full_threshold, 100],
                labels=['Not Eligible', 'Partial Scholarship', 'Full Scholarship'],
                include_lowest=True
            )
            
            df_ranked = dss.rank_applicants(df_scored)
            
            # Display results
            tabs = st.tabs([
                "📊 Overview",
                "👥 Applicant Rankings", 
                "🔍 Individual Analysis",
                "📈 Visualizations",
                "ℹ️ System Explanation"
            ])
            
            with tabs[0]:
                st.header("📊 Scholarship Allocation Overview")
                
                # Summary metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    total_applicants = len(df_ranked)
                    st.metric("Total Applicants", total_applicants)
                
                with col2:
                    full_count = len(df_ranked[df_ranked['recommendation'] == 'Full Scholarship'])
                    st.metric("Full Scholarships", full_count, f"{full_count/total_applicants*100:.1f}%")
                
                with col3:
                    partial_count = len(df_ranked[df_ranked['recommendation'] == 'Partial Scholarship'])
                    st.metric("Partial Scholarships", partial_count, f"{partial_count/total_applicants*100:.1f}%")
                
                with col4:
                    not_eligible = len(df_ranked[df_ranked['recommendation'] == 'Not Eligible'])
                    st.metric("Not Eligible", not_eligible, f"{not_eligible/total_applicants*100:.1f}%")
                
                # Score distribution
                st.subheader("Score Distribution")
                fig_dist = px.histogram(
                    df_ranked,
                    x='final_score',
                    nbins=30,
                    color='recommendation',
                    title='Final Score Distribution by Recommendation',
                    labels={'final_score': 'Final Score', 'count': 'Number of Applicants'},
                    color_discrete_map={
                        'Full Scholarship': '#28a745',
                        'Partial Scholarship': '#ffc107',
                        'Not Eligible': '#dc3545'
                    }
                )
                st.plotly_chart(fig_dist, use_container_width=True)
            
            with tabs[1]:
                st.header("👥 Applicant Rankings")
                
                # Filter options
                col1, col2 = st.columns(2)
                with col1:
                    recommendation_filter = st.multiselect(
                        "Filter by Recommendation",
                        options=['Full Scholarship', 'Partial Scholarship', 'Not Eligible'],
                        default=['Full Scholarship', 'Partial Scholarship', 'Not Eligible']
                    )
                
                with col2:
                    top_n = st.slider("Show top N applicants", 10, len(df_ranked), 50)
                
                # Display filtered rankings
                df_display = df_ranked[df_ranked['recommendation'].isin(recommendation_filter)].head(top_n)
                
                display_columns = [
                    'rank', 'final_score', 'recommendation',
                    'academic_score', 'financial_score', 'engagement_score',
                    'Performance Index', 'Previous Scores', 'family_income',
                    'parent_education', 'attendance_percentage',
                    'Extracurricular Activities'
                ]
                
                st.dataframe(
                    df_display[display_columns].style.background_gradient(
                        subset=['final_score', 'academic_score', 'financial_score', 'engagement_score'],
                        cmap='RdYlGn'
                    ),
                    height=600
                )
                
                # Download option
                csv = df_ranked.to_csv(index=False)
                st.download_button(
                    label="📥 Download Full Results",
                    data=csv,
                    file_name="scholarship_rankings.csv",
                    mime="text/csv"
                )
            
            with tabs[2]:
                st.header("🔍 Individual Applicant Analysis")
                
                # Select applicant
                applicant_id = st.selectbox(
                    "Select Applicant (by Rank)",
                    options=df_ranked['rank'].tolist(),
                    format_func=lambda x: f"Rank #{x}"
                )
                
                applicant_row = df_ranked[df_ranked['rank'] == applicant_id].iloc[0]
                explanation = dss.get_score_explanation(applicant_row)
                
                # Display recommendation
                st.subheader(f"Recommendation: {explanation['recommendation']}")
                st.metric("Final Score", f"{explanation['final_score']:.2f}/100")
                
                # Score breakdown
                st.subheader("Score Breakdown")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("**Academic Merit**")
                    st.metric("Score", f"{explanation['breakdown']['Academic Merit']['score']:.2f}")
                    st.write(f"Weight: {explanation['breakdown']['Academic Merit']['weight']}")
                    st.write(f"Contribution: {explanation['breakdown']['Academic Merit']['contribution']:.2f}")
                    with st.expander("Components"):
                        for k, v in explanation['breakdown']['Academic Merit']['components'].items():
                            st.write(f"- {k}: {v}")
                
                with col2:
                    st.markdown("**Financial Need**")
                    st.metric("Score", f"{explanation['breakdown']['Financial Need']['score']:.2f}")
                    st.write(f"Weight: {explanation['breakdown']['Financial Need']['weight']}")
                    st.write(f"Contribution: {explanation['breakdown']['Financial Need']['contribution']:.2f}")
                    with st.expander("Components"):
                        for k, v in explanation['breakdown']['Financial Need']['components'].items():
                            st.write(f"- {k}: {v}")
                
                with col3:
                    st.markdown("**Engagement**")
                    st.metric("Score", f"{explanation['breakdown']['Engagement']['score']:.2f}")
                    st.write(f"Weight: {explanation['breakdown']['Engagement']['weight']}")
                    st.write(f"Contribution: {explanation['breakdown']['Engagement']['contribution']:.2f}")
                    with st.expander("Components"):
                        for k, v in explanation['breakdown']['Engagement']['components'].items():
                            st.write(f"- {k}: {v}")
                
                # Visualization
                categories = ['Academic\nMerit', 'Financial\nNeed', 'Engagement']
                contributions = [
                    explanation['breakdown']['Academic Merit']['contribution'],
                    explanation['breakdown']['Financial Need']['contribution'],
                    explanation['breakdown']['Engagement']['contribution']
                ]
                
                fig_contribution = go.Figure(data=[
                    go.Bar(
                        x=categories,
                        y=contributions,
                        marker_color=['#3498db', '#e74c3c', '#f39c12']
                    )
                ])
                fig_contribution.update_layout(
                    title='Score Contribution by Category',
                    yaxis_title='Contribution to Final Score',
                    showlegend=False
                )
                st.plotly_chart(fig_contribution, use_container_width=True)
            
            with tabs[3]:
                st.header("📈 System Visualizations")
                
                # 1. Score components scatter
                st.subheader("Academic vs Financial Scores")
                fig_scatter = px.scatter(
                    df_ranked,
                    x='academic_score',
                    y='financial_score',
                    color='recommendation',
                    size='engagement_score',
                    hover_data=['rank', 'final_score'],
                    title='Academic Merit vs Financial Need',
                    color_discrete_map={
                        'Full Scholarship': '#28a745',
                        'Partial Scholarship': '#ffc107',
                        'Not Eligible': '#dc3545'
                    }
                )
                st.plotly_chart(fig_scatter, use_container_width=True)
                
                # 2. Income vs Recommendation
                st.subheader("Income Distribution by Recommendation")
                fig_income = px.box(
                    df_ranked,
                    x='recommendation',
                    y='family_income',
                    color='recommendation',
                    title='Family Income by Scholarship Type',
                    color_discrete_map={
                        'Full Scholarship': '#28a745',
                        'Partial Scholarship': '#ffc107',
                        'Not Eligible': '#dc3545'
                    }
                )
                st.plotly_chart(fig_income, use_container_width=True)
                
                # 3. Performance distribution
                st.subheader("Performance Index by Recommendation")
                fig_performance = px.violin(
                    df_ranked,
                    x='recommendation',
                    y='Performance Index',
                    color='recommendation',
                    box=True,
                    title='Performance Index Distribution',
                    color_discrete_map={
                        'Full Scholarship': '#28a745',
                        'Partial Scholarship': '#ffc107',
                        'Not Eligible': '#dc3545'
                    }
                )
                st.plotly_chart(fig_performance, use_container_width=True)
            
            with tabs[4]:
                st.header("ℹ️ System Explanation")
                
                st.markdown("""
                ### How the DSS Works
                
                This Decision Support System uses a **transparent, rule-based approach** to recommend 
                scholarship allocations. Unlike black-box AI models, every decision can be traced 
                and explained.
                
                #### Scoring Components
                
                **1. Academic Merit (Default 40%)**
                - Performance Index (60% of academic score)
                - Previous Scores (40% of academic score)
                
                **2. Financial Need (Default 40%)**
                - Family Income - inverted (70% of financial score)
                - Parent Education - inverted (30% of financial score)
                - *Lower income/education = higher need score*
                
                **3. Engagement (Default 20%)**
                - Attendance Percentage (50% of engagement score)
                - Extracurricular Activities (30% of engagement score)
                - Practice Papers (20% of engagement score)
                
                #### Decision Rules
                
                - **Final Score ≥ 80**: Full Scholarship
                - **Final Score 60-79**: Partial Scholarship
                - **Final Score < 60**: Not Eligible
                
                #### Key Principles
                
                 **Transparency**: All calculations are visible and explainable
                
                 **Fairness**: Balanced consideration of merit and need
                
                 **Configurability**: Weights can be adjusted based on institutional priorities
                
                **Human-in-the-loop**: System supports decisions, doesn't make them automatically
                
                #### Data Enhancement
                
                The system adds realistic simulated fields:
                - Family income (log-normal distribution)
                - Parent education (weighted distribution)
                - Attendance (correlated with performance)
                - Previous scholarship (inversely correlated with income)
                """)
                
                st.info("""
                **Important Note**: This DSS is designed to support human decision-makers, 
                not replace them. Final decisions should consider additional contextual factors 
                and institutional policies.
                """)
        else:
            st.warning(" Please adjust weights to sum to 100% before viewing results.")
    
    else:
        st.info(" Please upload StudentPerformance.csv to begin")
        
        # Show sample data format
        with st.expander("📄 Expected Data Format"):
            st.markdown("""
            Your CSV should contain these columns:
            - Hours Studied
            - Previous Scores
            - Extracurricular Activities (Yes/No)
            - Sleep Hours
            - Sample Question Papers Practiced
            - Performance Index
            
            The system will automatically add:
            - family_income
            - parent_education
            - attendance_percentage
            - previous_scholarship
            """)

if __name__ == "__main__":
    main()
