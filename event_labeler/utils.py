"""
Utility functions for the event labeler module
"""

import os

def clear_screen():
    """Clear the terminal screen based on operating system"""
    # For macOS and Linux
    if os.name == 'posix':
        os.system('clear')
    # For Windows
    elif os.name == 'nt':
        os.system('cls')


def display_menu():
    """
    Display the main menu options.
    
    Returns:
    --------
    str
        Selected menu option
    """
    print("\n" + "="*60)
    print("💧 Water Event Labeler 💧".center(60))
    print("="*60)
    print("🔽 Select an option:")
    print("1️⃣ Load dataset")
    print("2️⃣ Visualize events and patterns")
    print("3️⃣ Define auto-labeling rules")
    print("4️⃣ Apply auto-labeling rules")
    print("5️⃣ Manually label events")
    print("6️⃣ Create train/test split")
    print("7️⃣ Save labeled dataset")
    print("8️⃣ Exit")
    return input("\n🔍 Enter your choice (1-8): ")