# Scholarship Allocation Decision Support System

A transparent, rule-based DSS for fair scholarship allocation that balances academic merit, financial need, and student engagement.

##  Features

- **Transparent Scoring**: Every decision is fully explainable
- **Configurable Weights**: Adjust priorities based on institutional needs
- **Interactive Dashboard**: Streamlit-based interface for exploration
- **Fair Allocation**: Balanced consideration of multiple factors
- **Data Enhancement**: Automatically generates realistic additional fields
- **Individual Analysis**: Detailed breakdown for each applicant

##  Project Structure

```
scholarship-dss/
├── data/
│   └── StudentPerformance.csv      # Your input data
├── src/
│   ├── data_processor.py           # Data loading and enhancement
│   ├── dss_engine.py               # Scoring and decision logic
│   └── app.py                      # Streamlit application
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

##  Installation & Setup

### 1. Clone or Download

```bash
# Create project directory
mkdir DSS-PROJECT
cd DSS-PROJECT

# Create subdirectories
mkdir data src
```

### 2. Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

### 3. Prepare Data

Place your `StudentPerformance.csv` file in the `data/` folder.

### 4. Run the Application

```bash
# From project root
cd src
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

##  How It Works

### Data Enhancement

The system automatically adds these fields to your dataset:

1. **family_income**: Annual income ($15K-$200K, log-normal distribution)
2. **parent_education**: High School, Undergraduate, or Postgraduate
3. **attendance_percentage**: 60-100%, correlated with performance
4. **previous_scholarship**: Yes/No, inversely correlated with income

### Scoring Model

#### Three Main Components:

**1. Academic Merit (Default: 40%)**
- Performance Index: 60%
- Previous Scores: 40%

**2. Financial Need (Default: 40%)**
- Family Income (inverted): 70%
- Parent Education (inverted): 30%

**3. Engagement (Default: 20%)**
- Attendance: 50%
- Extracurriculars: 30%
- Practice Papers: 20%

### Decision Rules

- **Score ≥ 80**: Full Scholarship ($10,000)
- **Score 60-79**: Partial Scholarship ($5,000)
- **Score < 60**: Not Eligible ($0)

## Application

### Upload Data
1. Click "Browse files" in the sidebar
2. Upload your `StudentPerformance.csv`

### Adjust Weights
Use sliders to change importance of each category:
- Academic Merit
- Financial Need
- Engagement

**Note**: Weights must sum to 100%

### Adjust Thresholds
Modify score cutoffs for:
- Full Scholarship (default: 80)
- Partial Scholarship (default: 60)

### Explore Results

**Overview Tab**: Summary statistics and score distribution

**Applicant Rankings Tab**: Sortable table with all applicants, downloadable as CSV

**Individual Analysis Tab**: Detailed breakdown for any applicant showing:
- Final recommendation
- Score components
- Contributing factors

**Visualizations Tab**: 
- Academic vs Financial scatter plot
- Income distribution by recommendation
- Performance index distribution

**System Explanation Tab**: Complete documentation of how the DSS works

##  Key Principles

### Transparency
Every calculation is visible and explainable. No black-box algorithms.

### Fairness
Balanced consideration of:
- Merit (what students have achieved)
- Need (what students require)
- Engagement (what students contribute)

### Configurability
Weights can be adjusted to match institutional priorities and policies.

### Human-in-the-Loop
The system **supports** human decision-makers, it doesn't replace them.

##  Sample Output

```
Rank #1
Final Score: 92.5/100
Recommendation: Full Scholarship

Breakdown:
- Academic Merit: 95.0 (40% weight → 38.0 contribution)
- Financial Need: 88.0 (40% weight → 35.2 contribution)  
- Engagement: 96.0 (20% weight → 19.2 contribution)
```

##  Customization

### Modify Scoring Weights

In `dss_engine.py`, adjust default weights:

```python
dss = ScholarshipDSS(
    academic_weight=0.50,  # 50% instead of 40%
    financial_weight=0.30,  # 30% instead of 40%
    engagement_weight=0.20  # Keep at 20%
)
```

### Change Decision Thresholds

In `app.py` or via sliders:

```python
full_threshold = 85  # Raise bar for full scholarship
partial_threshold = 65  # Raise bar for partial
```

### Add New Data Fields

In `data_processor.py`, add custom enhancements:

```python
df['new_field'] = your_logic_here
```

##  Important Notes

1. **Simulated Data**: Added fields (income, education, etc.) are realistic simulations based on the original data
2. **Not Deterministic**: Each run may generate slightly different simulated values (set random seed for reproducibility)
3. **Decision Support**: This tool aids decision-making but should not be the sole factor
4. **Context Matters**: Consider institutional policies, special circumstances, and qualitative factors

##  Best Practices

1. **Review Top and Bottom**: Check both highly-scored and low-scored applicants
2. **Test Different Weights**: See how priorities affect outcomes
3. **Document Decisions**: Export rankings for record-keeping
4. **Human Review**: Final decisions should involve human judgment
5. **Regular Updates**: Recalibrate thresholds based on outcomes

##  Troubleshooting

### Issue: Weights don't sum to 100%
**Solution**: Adjust sliders until the green checkmark appears

### Issue: No data showing
**Solution**: Ensure CSV has correct column names (case-sensitive)

### Issue: Import errors
**Solution**: Verify all files are in correct folders and dependencies are installed

### Issue: Streamlit won't start
**Solution**: Check that you're in the `src/` directory and have activated virtual environment

##  References

This DSS follows principles from:
- Multi-Criteria Decision Analysis (MCDA)
- Weighted Scoring Models
- Transparent AI/Explainable AI (XAI)

##  License

This is an educational project. Adapt as needed for your institution's policies and legal requirements.

##  Support

For questions about the DSS methodology or implementation, refer to the "System Explanation" tab in the application or review the inline code comments.

---

**Version**: 1.0  
**Last Updated**: January 2026  
**Status**: Production-Ready
