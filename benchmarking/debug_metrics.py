import pandas as pd

# Load and analyze master metrics
df = pd.read_csv('results/master_session_metrics.csv')

print('Unique proficiency levels:', df['proficiency_level'].unique())
print('\nFor each level:')

for level in ['beginner', 'intermediate', 'advanced', 'expert']:
    level_df = df[df['proficiency_level'] == level]
    if not level_df.empty:
        print(f'\n{level.upper()}:')
        print(f'  Count: {len(level_df)}')
        print(f'  Avg reflection_depth: {level_df["reflection_depth"].mean():.3f}')
        print(f'  Avg question_quality: {level_df["question_quality"].mean():.3f}')
        print(f'  Avg problem_solving: {level_df["problem_solving"].mean():.3f}')
        print(f'  All reflection values: {level_df["reflection_depth"].tolist()}')
    else:
        print(f'\n{level.upper()}: No sessions')

# Check what the dashboard function would return
from collections import defaultdict

# Simulate the dashboard logic
proficiency_groups = df.groupby('proficiency_level')

result = {}
for metric in ['question_quality', 'reflection_depth', 'concept_integration', 
              'problem_solving', 'critical_thinking']:
    metric_values = []
    for level in ['beginner', 'intermediate', 'advanced', 'expert']:
        if level in proficiency_groups.groups:
            level_data = proficiency_groups.get_group(level)
            avg_value = level_data[metric].mean()
            metric_values.append(avg_value)
        else:
            # This is where defaults would be used
            default_progression = {
                'beginner': 0.35,
                'intermediate': 0.55,
                'advanced': 0.75,
                'expert': 0.90
            }
            metric_values.append(default_progression[level])
            print(f"WARNING: Using default for {level} - {metric}")
    
    # Capitalize metric name for display
    display_name = ' '.join(word.capitalize() for word in metric.split('_'))
    result[display_name] = metric_values

print("\nFinal result that dashboard would use:")
for metric, values in result.items():
    print(f"{metric}: {[f'{v:.3f}' for v in values]}")