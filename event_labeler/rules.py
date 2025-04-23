"""
Rule-based labeling functionality for water consumption events
"""

import json
import os
import numpy as np
import pandas as pd

def define_labeling_rules():
    """
    Define rules for auto-labeling water events.
    
    Returns:
    --------
    dict
        Dictionary of labeling rules
    """
    print("\n📝 Define Rules for Auto-Labeling")
    print("Define conditions for each water fixture type.")
    print("You can create rules based on event length, volume, flow rate, etc.")
    
    rules = []
    fixture_types = [
        "shower", "bathroom_faucet", "kitchen_faucet", 
        "toilet", "washing_machine", "dishwasher", 
        "ice_maker", "irrigation", "other"
    ]
    
    print("\n💧 Available water fixture types:")
    for i, fixture in enumerate(fixture_types):
        print(f"{i+1}. {fixture}")
    
    while True:
        print("\n🔧 Creating a new rule:")
        
        # Select fixture type
        print("Select a fixture type or enter a custom name:")
        for i, fixture in enumerate(fixture_types):
            print(f"{i+1}. {fixture}")
        print(f"{len(fixture_types)+1}. Custom fixture type")
        
        fixture_input = input("Enter fixture type number or name: ")
        try:
            fixture_idx = int(fixture_input) - 1
            if 0 <= fixture_idx < len(fixture_types):
                label = fixture_types[fixture_idx]
            elif fixture_idx == len(fixture_types):
                label = input("Enter custom fixture type name: ")
            else:
                print("❌ Invalid selection.")
                continue
        except ValueError:
            label = fixture_input
        
        # Define conditions
        print("\n📏 Define conditions for this fixture type:")
        print("Format: column_name operator value")
        print("Example: eventLength > 600")
        print("Available operators: >, <, >=, <=, ==, !=")
        print("Available columns: eventLength, eventVolume, avgFlowRate, maxFlowRate")
        print("Enter 'done' when finished with conditions for this fixture.")
        
        conditions = []
        while True:
            condition = input("Enter condition (or 'done'): ")
            if condition.lower() == 'done':
                break
            
            try:
                # Parse condition
                parts = condition.split()
                if len(parts) != 3:
                    print("❌ Invalid condition format. Example: eventLength > 600")
                    continue
                
                column, operator, value = parts
                
                # Validate column
                valid_columns = ['eventLength', 'eventVolume', 'avgFlowRate', 'maxFlowRate']
                if column not in valid_columns:
                    print(f"❌ Invalid column name. Choose from: {', '.join(valid_columns)}")
                    continue
                
                # Validate operator
                valid_operators = ['>', '<', '>=', '<=', '==', '!=']
                if operator not in valid_operators:
                    print(f"❌ Invalid operator. Choose from: {', '.join(valid_operators)}")
                    continue
                
                # Validate value
                try:
                    value = float(value)
                except ValueError:
                    print("❌ Value must be a number.")
                    continue
                
                # Add condition
                conditions.append({
                    'column': column,
                    'operator': operator,
                    'value': value
                })
                print(f"✅ Condition added: {condition}")
                
            except Exception as e:
                print(f"❌ Error: {str(e)}")
        
        # Add rule if conditions were defined
        if conditions:
            rules.append({
                'label': label,
                'conditions': conditions,
                'description': input("Enter a description for this rule (optional): ")
            })
            print(f"✅ Rule for '{label}' created with {len(conditions)} conditions.")
        else:
            print("⚠️ No conditions defined, rule not created.")
        
        # Ask if user wants to create another rule
        another = input("Create another rule? (y/n): ")
        if another.lower() != 'y':
            break
    
    return rules


def apply_rules(df, rules):
    """
    Apply labeling rules to the dataset.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame containing water events
    rules : list
        List of rule dictionaries
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with labels applied
    """
    # Create a copy of the dataframe
    df_labeled = df.copy()
    
    # Add label column if it doesn't exist
    if 'label' not in df_labeled.columns:
        # Initialize with an empty string instead of NaN to avoid dtype issues
        df_labeled['label'] = ''
    elif df_labeled['label'].dtype != 'object':
        # Convert to string type if it's not already
        df_labeled['label'] = df_labeled['label'].astype(str)
        # Replace 'nan' strings with empty strings
        df_labeled['label'] = df_labeled['label'].replace('nan', '')
    
    # Check if user wants to override existing labels
    override_existing = False
    if (df_labeled['label'] != '').any():
        labeled_count = (df_labeled['label'] != '').sum()
        total_count = len(df_labeled)
        print(f"\n⚠️ Dataset already has {labeled_count}/{total_count} labeled events.")
        override_choice = input("Do you want to: \n1. Label only unlabeled events \n2. Override all existing labels \n3. Cancel \n\nEnter choice (1-3): ")
        
        if override_choice == '2':
            override_existing = True
            # Reset all labels to empty string
            df_labeled['label'] = ''
            print("✅ All existing labels will be overridden.")
        elif override_choice == '3':
            print("❌ Operation cancelled.")
            return df
        else:
            print("✅ Applying rules only to unlabeled events.")
    
    # Count of events labeled by each rule
    rule_counts = {}
    
    # Apply each rule
    for rule in rules:
        label = rule['label']
        conditions = rule['conditions']
        
        # Create a mask for this rule
        mask = pd.Series(True, index=df_labeled.index)
        for condition in conditions:
            column = condition['column']
            operator = condition['operator']
            value = condition['value']
            
            if operator == '>':
                mask = mask & (df_labeled[column] > value)
            elif operator == '<':
                mask = mask & (df_labeled[column] < value)
            elif operator == '>=':
                mask = mask & (df_labeled[column] >= value)
            elif operator == '<=':
                mask = mask & (df_labeled[column] <= value)
            elif operator == '==':
                mask = mask & (df_labeled[column] == value)
            elif operator == '!=':
                mask = mask & (df_labeled[column] != value)
        
        # Apply this rule to unlabeled events
        if override_existing:
            # Apply to all matching events
            unlabeled_mask = mask
        else:
            # Apply only to currently unlabeled events
            unlabeled_mask = mask & (df_labeled['label'] == '')
            
        df_labeled.loc[unlabeled_mask, 'label'] = label
        
        # Count events labeled by this rule
        count = unlabeled_mask.sum()
        rule_counts[label] = rule_counts.get(label, 0) + count
    
    # Report results
    total_labeled = (df_labeled['label'] != '').sum()
    total_events = len(df_labeled)
    
    print(f"\n✅ Auto-labeling complete.")
    print(f"📊 Total events labeled: {total_labeled}/{total_events} ({total_labeled/total_events*100:.1f}%)")
    
    print("\n📈 Events labeled by rule:")
    for label, count in rule_counts.items():
        print(f"  {label}: {count} events")
    
    # Show distribution of all labels in the dataset
    all_labels = df_labeled['label'].value_counts()
    if len(all_labels) > 0:
        print("\n📊 Overall label distribution:")
        for label, count in all_labels.items():
            if label != '':
                print(f"  {label}: {count} events ({count/total_events*100:.1f}%)")
    
    # Report unlabeled events
    unlabeled_count = (df_labeled['label'] == '').sum()
    if unlabeled_count > 0:
        print(f"\n⚠️ {unlabeled_count} events remain unlabeled ({unlabeled_count/total_events*100:.1f}%)")
    
    return df_labeled


def save_rules(rules, filename=os.path.join('config', 'water_event_rules.json')):
    """
    Save labeling rules to a JSON file.
    
    Parameters:
    -----------
    rules : list
        List of rule dictionaries
    filename : str
        Filename to save rules to
    
    Returns:
    --------
    str
        Path to the saved file
    """
    try:
        with open(filename, 'w') as f:
            json.dump(rules, f, indent=2)
        print(f"✅ Rules saved to {filename}")
        return filename
    except Exception as e:
        print(f"❌ Error saving rules: {str(e)}")
        return None


def load_rules(filename=os.path.join('config', 'water_event_rules.json')):
    """
    Load labeling rules from a JSON file.
    
    Parameters:
    -----------
    filename : str
        Filename to load rules from
    
    Returns:
    --------
    list
        List of rule dictionaries
    """
    try:
        if not os.path.exists(filename):
            print(f"❌ Rules file not found: {filename}")
            return None
            
        with open(filename, 'r') as f:
            rules = json.load(f)
        print(f"✅ Rules loaded from {filename}")
        return rules
    except Exception as e:
        print(f"❌ Error loading rules: {str(e)}")
        return None