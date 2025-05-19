import os
import shutil
import streamlit as st
import google.generativeai as genai
import mimetypes
from pathlib import Path
import re

# Configure the Gemini API with the provided key
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

def initialize_app():
    """Initialize the app with necessary session state variables."""
    if "selected_dir" not in st.session_state:
        st.session_state.selected_dir = ""
    if "file_operations_log" not in st.session_state:
        st.session_state.file_operations_log = []

def select_directory():
    """Allow user to input the directory path they want to manage."""
    st.write("Select a directory to manage:")
    directory = st.text_input("Directory Path", 
                          value=st.session_state.selected_dir,
                          placeholder="Example: /Users/username/Documents",
                          help="Enter the full path to the directory you want to manage")
    
    if directory and os.path.isdir(directory):
        st.session_state.selected_dir = directory
        return True
    elif directory:
        st.error(f"Directory '{directory}' not found or not accessible.")
    
    return False

def list_directory_contents(directory):
    """List the contents of the selected directory."""
    try:
        contents = os.listdir(directory)
        files = []
        folders = []
        
        for item in contents:
            item_path = os.path.join(directory, item)
            if os.path.isfile(item_path):
                file_type = get_file_type(item_path)
                size = os.path.getsize(item_path)
                files.append({"name": item, "type": file_type, "size": format_size(size)})
            elif os.path.isdir(item_path):
                folders.append({"name": item, "type": "folder", "size": ""})
        
        return folders, files
    except Exception as e:
        st.error(f"Error accessing directory: {str(e)}")
        return [], []

def get_file_type(file_path):
    """Get the type of a file based on its extension."""
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type:
        return mime_type.split('/')[0]
    return "unknown"

def format_size(size_bytes):
    """Format file size in a human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024 or unit == 'GB':
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024

def process_command_with_gemini(command, directory):
    """Process the user's command using Gemini API."""
    if not command.strip():
        return "Please enter a command."
    
    folders, files = list_directory_contents(directory)
    
    # Create a context with directory information for Gemini
    directory_info = {
        "directory": directory,
        "folders": folders,
        "files": files
    }
    
    context = f"""
    You are a file system assistant that helps organize files in a directory. 
    The current directory is: {directory}
    
    Folders in this directory:
    {', '.join([folder['name'] for folder in folders]) if folders else 'No folders found.'}
    
    Files in this directory:
    {', '.join([f"{file['name']} ({file['type']})" for file in files]) if files else 'No files found.'}
    
    The user would like to: {command}
    
    Only respond with the exact commands I should execute to fulfill this request.
    Structure your response as a JSON object with:
    1. "operations": a list of operations to perform, each with "action" (one of: "create_folder", "move", "rename", "delete", "organize_by_type"), "source" and "destination" fields
    2. "explanation": a simple explanation of what will be done
    
    Only use the files and folders that exist in the provided directory information. Don't reference files or folders that aren't listed.
    """
    
    try:
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content(context)
        
        # Extract JSON from the response
        json_pattern = r'\{[\s\S]*\}'
        match = re.search(json_pattern, response.text)
        
        if match:
            import json
            result = json.loads(match.group(0))
            return result
        else:
            return {"operations": [], "explanation": "I couldn't understand how to process that request. Please try a different command."}
    
    except Exception as e:
        return {"operations": [], "explanation": f"Error processing command: {str(e)}"}

def execute_file_operations(operations, directory):
    """Execute the file operations returned by Gemini."""
    results = []
    
    for op in operations:
        action = op.get("action", "")
        source = op.get("source", "")
        destination = op.get("destination", "")
        
        try:
            if action == "create_folder":
                folder_path = os.path.join(directory, destination)
                os.makedirs(folder_path, exist_ok=True)
                results.append(f"Created folder: {destination}")
                
            elif action == "move":
                source_path = os.path.join(directory, source)
                dest_path = os.path.join(directory, destination)
                
                # Ensure destination directory exists
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                
                shutil.move(source_path, dest_path)
                results.append(f"Moved: {source} → {destination}")
                
            elif action == "rename":
                source_path = os.path.join(directory, source)
                dest_path = os.path.join(directory, destination)
                os.rename(source_path, dest_path)
                results.append(f"Renamed: {source} → {destination}")
                
            elif action == "delete":
                source_path = os.path.join(directory, source)
                if os.path.isfile(source_path):
                    os.remove(source_path)
                elif os.path.isdir(source_path):
                    shutil.rmtree(source_path)
                results.append(f"Deleted: {source}")
                
            elif action == "organize_by_type":
                # Get the list of files in the directory
                files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
                
                # Create a dictionary to group files by type
                file_types = {}
                for file in files:
                    file_path = os.path.join(directory, file)
                    file_type = get_file_type(file_path)
                    
                    if file_type not in file_types:
                        file_types[file_type] = []
                    
                    file_types[file_type].append(file)
                
                # Create folders for each type and move files
                for file_type, type_files in file_types.items():
                    if file_type == "unknown":
                        continue
                        
                    type_folder = os.path.join(directory, file_type.capitalize())
                    os.makedirs(type_folder, exist_ok=True)
                    
                    for file in type_files:
                        source_path = os.path.join(directory, file)
                        dest_path = os.path.join(type_folder, file)
                        shutil.move(source_path, dest_path)
                    
                    results.append(f"Moved {len(type_files)} {file_type} files to {file_type.capitalize()} folder")
        
        except Exception as e:
            results.append(f"Error during {action}: {str(e)}")
    
    return results

def main():
    """Main function to run the Streamlit app."""
    st.set_page_config(
        page_title="File System Manager",
        page_icon="📁",
        layout="wide"
    )
    
    # Initialize app
    initialize_app()
    
    # App header
    st.title("📁 File System Manager")
    st.write("Use natural language to organize, rename, and rearrange your files and folders.")
    
    # Set Gemini API key
    with st.sidebar:
        st.subheader("API Configuration")
        api_key = st.text_input("Gemini API Key", value="AIzaSyC6WUfVwtDCNixDulJNdz_PHPipUO8tPdw", type="password")
        if api_key:
            st.secrets["GEMINI_API_KEY"] = api_key
            genai.configure(api_key=api_key)
    
    # Directory selection
    valid_dir = select_directory()
    
    if valid_dir:
        # Display directory contents
        st.subheader("Directory Contents")
        
        folders, files = list_directory_contents(st.session_state.selected_dir)
        
        # Create two columns for folders and files
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Folders:**")
            if folders:
                for folder in folders:
                    st.write(f"📁 {folder['name']}")
            else:
                st.write("No folders found")
        
        with col2:
            st.write("**Files:**")
            if files:
                for file in files:
                    icon = "📄"
                    if file["type"] == "image":
                        icon = "🖼️"
                    elif file["type"] == "audio":
                        icon = "🔊"
                    elif file["type"] == "video":
                        icon = "🎬"
                    st.write(f"{icon} {file['name']} ({file['size']})")
            else:
                st.write("No files found")
        
        # Command input
        st.subheader("What would you like to do?")
        st.write("Examples: 'Move all images to a Photos folder', 'Rename all PDF files to include today's date', 'Organize files by type'")
        
        command = st.text_area("Enter your command", height=100)
        
        if st.button("Execute Command"):
            with st.spinner("Processing your command..."):
                result = process_command_with_gemini(command, st.session_state.selected_dir)
                
                # Display explanation
                st.info(result.get("explanation", "No explanation provided."))
                
                # Execute operations
                operations = result.get("operations", [])
                if operations:
                    with st.expander("Operations to be performed", expanded=True):
                        for op in operations:
                            action = op.get("action", "")
                            source = op.get("source", "")
                            destination = op.get("destination", "")
                            
                            if action == "create_folder":
                                st.write(f"✅ Create folder: {destination}")
                            elif action == "move":
                                st.write(f"✅ Move: {source} → {destination}")
                            elif action == "rename":
                                st.write(f"✅ Rename: {source} → {destination}")
                            elif action == "delete":
                                st.write(f"❌ Delete: {source}")
                            elif action == "organize_by_type":
                                st.write(f"✅ Organize files by type")
                    
                    # Confirm before executing
                    if st.button("Confirm and Execute"):
                        with st.spinner("Executing file operations..."):
                            results = execute_file_operations(operations, st.session_state.selected_dir)
                            
                            # Log the results
                            st.session_state.file_operations_log.extend(results)
                            
                            # Display results
                            st.success("Operations completed!")
                            for result in results:
                                st.write(result)
                            
                            # Update directory contents after operations
                            st.experimental_rerun()
                else:
                    st.warning("No operations to perform. Try a different command.")
        
        # Show operation log
        if st.session_state.file_operations_log:
            with st.expander("Operation Log", expanded=False):
                for log_entry in st.session_state.file_operations_log:
                    st.write(log_entry)
                
                if st.button("Clear Log"):
                    st.session_state.file_operations_log = []
                    st.experimental_rerun()

if __name__ == "__main__":
    main()