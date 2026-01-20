"""
DSS Engine for Scholarship Allocation
Implements transparent, rule-based scoring and decision logic
"""

import pandas as pd
import numpy as np

class ScholarshipDSS:
    """
    Decision Support System for Fair Scholarship Allocation
    Uses transparent weighted scoring with explainable rules
    """
    
    def __init__(self, 
                 academic_weight=0.40,
                 financial_weight=0.40, 
                 engagement_weight=0.20):
        """
        Initialize DSS with configurable weights
        
        Args:
            academic_weight: Weight for academic merit (default 40%)
            financial_weight: Weight for financial need (default 40%)
            engagement_weight: Weight for engagement factors (default 20%)
        """
        # Validate weights sum to 1.0
        total = academic_weight + financial_weight + engagement_weight
        if not np.isclose(total, 1.0):
            raise ValueError(f"Weights must sum to 1.0 (current: {total})")
        
        self.academic_weight = academic_weight
        self.financial_weight = financial_weight
        self.engagement_weight = engagement_weight
        
    def calculate_academic_score(self, df):
        """
        Calculate academic merit score (40% default)
        Components:
        - Performance Index: 60% of academic score
        - Previous Scores: 40% of academic score
        
        Returns:
            Series with scores 0-100
        """
        performance_weight = 0.6
        previous_weight = 0.4
        
        academic_score = (
            df['Performance Index_normalized'] * performance_weight +
            df['Previous Scores_normalized'] * previous_weight
        )
        
        return academic_score
    
    def calculate_financial_score(self, df):
        """
        Calculate financial need score (40% default)
        Components:
        - Family Income (inverted): 70% of financial score
        - Parent Education (inverted): 30% of financial score
        
        Lower income and education = higher need
        
        Returns:
            Series with scores 0-100
        """
        income_weight = 0.7
        education_weight = 0.3
        
        # Invert parent education score (lower education = higher need)
        parent_ed_need = 100 - ((df['parent_education_score'] - 1) / 2 * 100)
        
        financial_score = (
            df['income_need_score'].fillna(50) * income_weight +
            parent_ed_need.fillna(50) * education_weight
            )

        
        return financial_score
    
    def calculate_engagement_score(self, df):
        """
        Calculate engagement score (20% default)
        Components:
        - Attendance: 50% of engagement score
        - Extracurricular Activities: 30% of engagement score
        - Sample Papers Practiced: 20% of engagement score
        
        Returns:
            Series with scores 0-100
        """
        attendance_weight = 0.5
        extracurricular_weight = 0.3
        practice_weight = 0.2
        
        engagement_score = (
            df['attendance_percentage_normalized'] * attendance_weight +
            df['extracurricular_score'] * 100 * extracurricular_weight +
            df['Sample Question Papers Practiced_normalized'] * practice_weight
        )
        
        return engagement_score
    
    def calculate_final_score(self, df):
        """
        Calculate final weighted scholarship score
        
        Returns:
            DataFrame with component scores and final score
        """
        df_scored = df.copy()
        
        # Calculate component scores
        df_scored['academic_score'] = self.calculate_academic_score(df)
        df_scored['financial_score'] = self.calculate_financial_score(df)
        df_scored['engagement_score'] = self.calculate_engagement_score(df)
        
        # Calculate weighted final score
        df_scored['final_score'] = (
            df_scored['academic_score'] * self.academic_weight +
            df_scored['financial_score'] * self.financial_weight +
            df_scored['engagement_score'] * self.engagement_weight
        )
        
        # Round for clarity
        df_scored['final_score'] = df_scored['final_score'].round(2)
        df_scored['academic_score'] = df_scored['academic_score'].round(2)
        df_scored['financial_score'] = df_scored['financial_score'].round(2)
        df_scored['engagement_score'] = df_scored['engagement_score'].round(2)
        
        return df_scored
    
    def apply_decision_rules(self, df_scored):
        """
        Apply transparent decision rules based on final score
        
        Rules:
        - Score ≥ 80: Full Scholarship
        - Score 60-79: Partial Scholarship
        - Score < 60: Not Eligible
        
        Returns:
            DataFrame with recommendation and amount
        """
        df_decision = df_scored.copy()
        
        # Apply decision rules
        conditions = [
            df_decision['final_score'] >= 80,
            (df_decision['final_score'] >= 60) & (df_decision['final_score'] < 80),
            df_decision['final_score'] < 60
        ]
        
        choices = ['Full Scholarship', 'Partial Scholarship', 'Not Eligible']
        df_decision['recommendation'] = np.select(conditions, choices)
        
        # Calculate scholarship amount (based on typical tuition)
        # Full: $10,000, Partial: $5,000, None: $0
        amount_conditions = [
            df_decision['final_score'] >= 80,
            (df_decision['final_score'] >= 60) & (df_decision['final_score'] < 80),
            df_decision['final_score'] < 60
        ]
        
        amount_choices = [10000, 5000, 0]
        df_decision['scholarship_amount'] = np.select(amount_conditions, amount_choices)
        
        return df_decision
    
    def get_score_explanation(self, row):
        """
        Generate human-readable explanation for a single applicant's score
        
        Args:
            row: Single row from scored DataFrame
            
        Returns:
            Dictionary with explanation
        """
        explanation = {
            'final_score': row['final_score'],
            'recommendation': row['recommendation'],
            'breakdown': {
                'Academic Merit': {
                    'score': row['academic_score'],
                    'weight': f"{self.academic_weight*100}%",
                    'contribution': row['academic_score'] * self.academic_weight,
                    'components': {
                        'Performance Index': row['Performance Index'],
                        'Previous Scores': row['Previous Scores']
                    }
                },
                'Financial Need': {
                    'score': row['financial_score'],
                    'weight': f"{self.financial_weight*100}%",
                    'contribution': row['financial_score'] * self.financial_weight,
                    'components': {
                        'Family Income': f"${row['family_income']:,}",
                        'Parent Education': row['parent_education']
                    }
                },
                'Engagement': {
                    'score': row['engagement_score'],
                    'weight': f"{self.engagement_weight*100}%",
                    'contribution': row['engagement_score'] * self.engagement_weight,
                    'components': {
                        'Attendance': f"{row['attendance_percentage']}%",
                        'Extracurriculars': row['Extracurricular Activities'],
                        'Practice Papers': row['Sample Question Papers Practiced']
                    }
                }
            }
        }
        
        return explanation
    
    def rank_applicants(self, df_decision):
        """
        Rank applicants by final score
        
        Returns:
            Sorted DataFrame with rank column
        """
        df_ranked = df_decision.sort_values('final_score', ascending=False).copy()
        df_ranked['rank'] = range(1, len(df_ranked) + 1)
        
        return df_ranked
