import os

# Ask user for directory path
path = input("D:/Python work/chapter 1 practice set/")


# Check if path exists
if os.path.exists(path):
    print(f"\nContents of '{path}':")
    print("-" * 40)
    
    # List all files and directories
    for item in os.listdir(path):
        full_path = os.path.join(path, item)
        if os.path.isdir(full_path):
            print(f"[DIR]  {item}")
        else:
            print(f"[FILE] {item}")
else:
    print(f"Error: The path '{path}' does not exist.")