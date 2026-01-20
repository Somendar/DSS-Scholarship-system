"""
Data Processor for Scholarship DSS
Handles dataset loading, enhancement, and preprocessing
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

class ScholarshipDataProcessor:
    """
    Processes and enhances student performance data for scholarship decisions
    """
    
    def __init__(self):
        self.scaler = MinMaxScaler()
        self.categorical_mappings = {}
        
    def load_and_enhance_data(self, filepath):
        """
        Load CSV and add realistic simulated columns
        
        Args:
            filepath: Path to StudentPerformance.csv
            
        Returns:
            Enhanced DataFrame
        """
        # Load original data
        df = pd.read_csv(filepath)
        
        # Set random seed for reproducibility
        np.random.seed(42)
        n = len(df)
        
        # 1. Family Income (realistic distribution)
        # Using log-normal distribution for realistic income spread
        income_base = np.random.lognormal(mean=10.5, sigma=0.8, size=n)
        df['family_income'] = (income_base * 5000).astype(int)
        # Clip to reasonable range
        df['family_income'] = df['family_income'].clip(15000, 200000)
        
        # 2. Parent Education (weighted distribution)
        education_choices = ['High School', 'Undergraduate', 'Postgraduate']
        education_weights = [0.4, 0.4, 0.2]  # Realistic distribution
        df['parent_education'] = np.random.choice(
            education_choices, 
            size=n, 
            p=education_weights
        )
        
        # 3. Attendance Percentage (correlated with performance)
        # Students with better performance tend to have better attendance
        base_attendance = np.random.normal(80, 10, size=n)
        performance_boost = (df['Performance Index'] / 100) * 15
        df['attendance_percentage'] = (base_attendance + performance_boost).clip(60, 100)
        df['attendance_percentage'] = df['attendance_percentage'].round(1)
        
        # 4. Previous Scholarship (inversely correlated with income)
        # Lower income students more likely to have had previous scholarship
        income_normalized = (df['family_income'] - df['family_income'].min()) / \
                           (df['family_income'].max() - df['family_income'].min())
        scholarship_prob = 1 - income_normalized * 0.7  # 30% base, up to 100%
        df['previous_scholarship'] = np.random.random(n) < scholarship_prob
        df['previous_scholarship'] = df['previous_scholarship'].map({True: 'Yes', False: 'No'})
        
        return df
    
    def preprocess_data(self, df):
        """
        Prepare data for DSS scoring with transparent transformations
        
        Args:
            df: Enhanced DataFrame
            
        Returns:
            Processed DataFrame with normalized scores
        """
        df_processed = df.copy()
        
        # Encode categorical variables (transparent mapping)
        # Extracurricular Activities
        df_processed['extracurricular_score'] = df_processed['Extracurricular Activities'].map({
            'Yes': 1.0,
            'No': 0.0
        })
        
        # Parent Education (ordinal encoding)
        education_map = {
            'High School': 1,
            'Undergraduate': 2,
            'Postgraduate': 3
        }
        df_processed['parent_education_score'] = df_processed['parent_education'].map(education_map)
        self.categorical_mappings['parent_education'] = education_map
        
        # Previous Scholarship
        df_processed['previous_scholarship_score'] = df_processed['previous_scholarship'].map({
            'Yes': 1.0,
            'No': 0.0
        })
        
        # Normalize numerical features (0-100 scale for interpretability)
        numerical_features = {
            'Hours Studied': (0, 10),
            'Previous Scores': (0, 100),
            'Sleep Hours': (0, 10),
            'Sample Question Papers Practiced': (0, 10),
            'Performance Index': (0, 100),
            'family_income': (df_processed['family_income'].min(), df_processed['family_income'].max()),
            'attendance_percentage': (60, 100),
            'parent_education_score': (1, 3)
        }
        
        for feature, (min_val, max_val) in numerical_features.items():
            if feature in df_processed.columns:
                if max_val > min_val:
                    df_processed[f'{feature}_normalized'] = (
                        (df_processed[feature] - min_val) / (max_val - min_val) * 100
                        ).clip(0, 100)
                else:
                    df_processed[f'{feature}_normalized'] = 50

        
        # Invert income score (lower income = higher need score)
        # SAFE income need score 
        if 'family_income_normalized' in df_processed.columns:
            df_processed['income_need_score'] = 100 - df_processed['family_income_normalized']
        else:
            df_processed['income_need_score'] = 50

        
        return df_processed
    
    def get_feature_explanation(self, feature_name):
        """
        Provide human-readable explanation of each feature
        """
        explanations = {
            'Performance Index': 'Overall academic performance (0-100)',
            'Previous Scores': 'Historical academic achievement (0-100)',
            'family_income': 'Annual family income (lower = higher need)',
            'parent_education': 'Highest education level of parents',
            'attendance_percentage': 'Class attendance rate (60-100%)',
            'Extracurricular Activities': 'Participation in extracurriculars',
            'previous_scholarship': 'Previously received scholarship assistance'
        }
        return explanations.get(feature_name, 'Feature score')
