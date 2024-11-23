from PyQt6.QtWidgets import QPlainTextEdit
from PyQt6.QtGui import QFont, QKeySequence, QTextCharFormat, QTextCursor
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
import platform
from pathlib import Path
import shutil
from datetime import datetime

class TerminalWidget(QPlainTextEdit):
  commandEntered = pyqtSignal(str)
  
  def __init__(self, parent=None):
    super().__init__(parent)
    
    # Set up custom styling
    self.setup_styling()
    
    # Initialize command history
    self.command_history = []
    self.history_index = 0

    # Track the last prompt position
    self.last_prompt_position = 0
    
    # Set up prompt
    self.prompt = "$ "
    self.current_directory = Path.home()

    # Make widget read-only initially
    self.setReadOnly(True)
    
    # Clear any existing content
    self.clear()
        
    # Show welcome message and initial prompt
    # this runs after widget is fully initialized
    QTimer.singleShot(0, self.initial_setup)
  
  # INITIAL SETUP
  def initial_setup(self):
    self.show_welcome_message()
    self.insert_prompt()

  # STYLINGS
  def setup_styling(self):
    # Set font
    font = QFont("Consolas" if platform.system() == "Windows" else "Menlo")
    font.setPointSize(11)
    self.setFont(font)
    
    # Set colors and styling
    self.setStyleSheet("""
        QPlainTextEdit {
            background-color: #1e1e1e;
            color: #f0f0f0;
            border: 1px solid #2d2d2d;
            border-radius: 6px;
            padding: 8px;
        }
    """)
  
  # SHOW WELCOME MESSAGE
  def show_welcome_message(self):
    welcome_text = """
      ╔════════════════════════════════════════════════════════════════════════════╗
      ║                     Welcome to Team D Terminal v1.0                        ║
      ║                                                                            ║
      ║    Type 'help' to see available commands and their descriptions            ║
      ║    Press Ctrl+L to clear the screen                                        ║
      ║    Type 'exit' to close the terminal                                       ║
      ╚════════════════════════════════════════════════════════════════════════════╝
    """

    self.appendPlainText(welcome_text)
    self.last_prompt_position = self.textCursor().position()

  # SHOW HELP MESSAGE
  def show_help_message(self):
      help_text = """
        Available Commands:
        ------------------
        clear or cls : Clear the terminal screen
        cd <dir> : Change directory (use .. to go back)
        ls : List files and directories in current directory
        pwd : Show current directory path
        mkdir <name> : Create a new directory
        rmdir <name> : Remove an empty directory
        rmdir -r <name> : Remove directory and its contents
        rmdir -f <name> : Force remove without confirmation
        touch <name> : Create a new file
        rm <name> : Delete a file
        write <file> <content> : Write content to a file
        read <file> : Display the content of a file
        help : Show this help message
        exit : Close the terminal

        Shortcuts:
        ---------
        Ctrl+L : Clear screen
        Up/Down Arrow : Navigate through command history
      """

      self.appendPlainText(help_text)
      self.last_prompt_position = self.textCursor().position()

  # CREATE A FILE
  def create_file(self, file_name):
    try:
      new_file = self.current_directory / file_name
      new_file.touch()
      self.appendPlainText(f"\nFile created: {new_file}")
    except Exception as e:
      self.appendPlainText(f"\nError creating file: {e}")

  # CREATE OR UPDATE EXISTING FILE
  def write_to_file(self, file_name, content):
    """Write content to a file in the current directory."""
    try:
      file_path = self.current_directory / file_name
      # Remove surrounding quotes if present
      content = content.strip('"\'')
      with open(file_path, 'w', encoding='utf-8') as f:
          f.write(content)
      self.appendPlainText(f"\nContent written to '{file_name}' successfully")
    except Exception as e:
      self.appendPlainText(f"\nError writing to file: {e}")

  # READ FILE
  def read_file(self, file_name):
    """Read and display the content of a file."""
    try:
      file_path = self.current_directory / file_name
      if not file_path.exists():
        self.appendPlainText(f"\nError: File '{file_name}' not found")
        return
      if file_path.is_dir():
        self.appendPlainText(f"\nError: '{file_name}' is a directory")
        return
      with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
      self.appendPlainText(f"\nContent of '{file_name}':")
      self.appendPlainText("----------------------------------------")
      self.appendPlainText(content)
      self.appendPlainText("----------------------------------------")
    except Exception as e:
      self.appendPlainText(f"\nError reading file: {e}")

  # DELETE FILE
  def delete_file(self, file_name):
    """Delete a file from the current directory."""

    try:
      file_path = self.current_directory / file_name
      if not file_path.exists():
        self.appendPlainText(f"\nError: File '{file_name}' not found")
        return
      if file_path.is_dir():
        shutil.rmtree(file_path)
        self.appendPlainText(f"\nDirectory '{file_name}' and its contents deleted successfully")
      else:
        file_path.unlink()
        self.appendPlainText(f"\nFile '{file_name}' deleted successfully")
    except Exception as e:
      self.appendPlainText(f"\nError deleting file: {e}")

  # DIRECTORY CREATION
  def create_directory(self, directory_name):
    try:
      new_dir = self.current_directory / directory_name
      new_dir.mkdir(exist_ok=True)
      self.appendPlainText(f"\nDirectory created: {new_dir}")
    except Exception as e:
      self.appendPlainText(f"\nError creating directory: {e}")

  # SHOW REMOVE DIRECTORY HELP
  def show_rmdir_help(self):
    """Show help for rmdir command"""
    help_text = """
    rmdir - Remove directory command

    Usage: rmdir [options] <directory_name>

    Options:
      -r, --recursive  : Remove directory and its contents recursively
      -f, --force     : Force removal without confirmation

    Examples:
      rmdir empty_dir          : Remove an empty directory
      rmdir -r project_dir     : Remove directory and all its contents
      rmdir -f old_dir         : Force remove without confirmation
      rmdir -rf temp_dir       : Force remove recursively without confirmation
    """
    self.appendPlainText(help_text)

  # REMOVE DIRECTORY
  def remove_directory(self, dir_name, force=False, recursive=False):
    """
    Remove a directory with various options
    
    Args:
        dir_name (str): Name of directory to remove
        force (bool): If True, skip confirmation
        recursive (bool): If True, remove directory and all contents
    """
    try:
      dir_path = self.current_directory / dir_name
      
      # Check if directory exists
      if not dir_path.exists():
        self.appendPlainText(f"\nError: Directory '{dir_name}' does not exist")
        return
          
      # Check if it's actually a directory
      if not dir_path.is_dir():
        self.appendPlainText(f"\nError: '{dir_name}' is not a directory")
        return
          
      # Check if directory is empty when not using recursive
      if not recursive and any(dir_path.iterdir()):
        self.appendPlainText(f"\nError: Directory '{dir_name}' is not empty")
        self.appendPlainText("Use 'rmdir -r' to remove directory and its contents")
        return
          
      # Safety check: prevent removing important directories
      if dir_path == Path.home() or dir_path == Path("/"):
        self.appendPlainText(f"\nError: Cannot remove critical directory '{dir_name}'")
        return
          
      # Get confirmation if not force mode
      if not force:
        msg = f"Remove {'directory and its contents' if recursive else 'empty directory'}: {dir_name}?"
        self.appendPlainText(f"\n{msg} (y/n): ")
        # Store the confirmation state
        self._awaiting_confirmation = True
        self._pending_operation = lambda: self._complete_remove_directory(dir_path, recursive)
        return
          
      # If force mode, proceed directly
      self._complete_remove_directory(dir_path, recursive)
        
    except Exception as e:
      self.appendPlainText(f"\nError removing directory: {e}")

  def _complete_remove_directory(self, dir_path, recursive):
    """Complete the directory removal operation"""
    try:
      if recursive:
        shutil.rmtree(dir_path)
        self.appendPlainText(f"\nDirectory '{dir_path.name}' and its contents removed successfully")
      else:
        dir_path.rmdir()
        self.appendPlainText(f"\nEmpty directory '{dir_path.name}' removed successfully")
    except Exception as e:
        self.appendPlainText(f"\nError completing directory removal: {e}")

  # CHANGE DIRECTORY
  def change_directory(self, directory):
    try:
      # Handle multiple dots for going back multiple levels
      if directory.startswith('.'):
        dot_count = directory.count('.')
        # Get the parent directory for the number of dots
        new_dir = self.current_directory
        for _ in range(dot_count):
          new_dir = new_dir.parent
          # Prevent going above root directory
          if new_dir == new_dir.parent:
              break
      else:
        # Normalize path separators and handle absolute/relative paths
        normalized_path = directory.replace('\\', '/')
        if normalized_path.startswith('/'):
          # Absolute path
          new_dir = Path(normalized_path)
        else:
          # Relative path
          new_dir = self.current_directory / normalized_path

      # Resolve the path to handle . and .. references
      new_dir = new_dir.resolve()

      if new_dir.is_dir():
        self.current_directory = new_dir
        self.appendPlainText(f"\nChanged directory to: {new_dir}")
      else:
        self.appendPlainText(f"\nDirectory not found: {new_dir}")
    except Exception as e:
      self.appendPlainText(f"\nError changing directory: {e}")

  # FILES AND DIRECTORIES LISTINGS
  def list_files(self):
    """Enhanced list_files method with more details."""
    try:
      self.appendPlainText("\nDirectory contents:")
      self.appendPlainText("----------------------------------------")
      self.appendPlainText("Type       Size        Modified         Name")
      self.appendPlainText("----------------------------------------")
        
      for item in sorted(self.current_directory.iterdir()):
        item_type = "DIR " if item.is_dir() else "FILE"
        stats = item.stat()
        size = "-" if item.is_dir() else f"{stats.st_size:8d}B"
        modified = datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M")
        self.appendPlainText(f"{item_type:9} {size:10} {modified:15} {item.name}")
      
      self.appendPlainText("----------------------------------------")
    except Exception as e:
      self.appendPlainText(f"\nError listing files: {e}")

  # PROMPT INSERTION
  def insert_prompt(self):
    self.setReadOnly(False)
    prompt_text = f"{self.prompt}{self.current_directory}>"
    self.appendPlainText("" if self.document().isEmpty() else "\n")
    self.insertPlainText(prompt_text + " ")
    self.last_prompt_position = self.textCursor().position()
    self.moveCursor(QTextCursor.MoveOperation.End)
    self.setReadOnly(False)
 
  # CURRENT COMMAND UPDATE
  def replace_current_command(self, new_command):
    cursor = self.textCursor()
    cursor.movePosition(QTextCursor.MoveOperation.End)
    cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock, QTextCursor.MoveMode.KeepAnchor)
    cursor.removeSelectedText()
    prompt_text = f"{self.prompt}{self.current_directory} "
    cursor.insertText(prompt_text + new_command)
  
  # KEY PRESS EVENTS
  def keyPressEvent(self, event):
    cursor = self.textCursor()

    # Handle confirmation prompts first
    if hasattr(self, '_awaiting_confirmation'):
      if event.text().lower() in ['y', 'n']:
        self.appendPlainText(event.text())
        if event.text().lower() == 'y':
          if hasattr(self, '_pending_operation'):
              self._pending_operation()
        else:
          self.appendPlainText("\nOperation cancelled")
        
        # Clean up confirmation state
        delattr(self, '_awaiting_confirmation')
        if hasattr(self, '_pending_operation'):
          delattr(self, '_pending_operation')
        
        self.insert_prompt()
        return
      elif event.key() not in [Qt.Key.Key_Left, Qt.Key.Key_Right, Qt.Key.Key_Up, Qt.Key.Key_Down]:
        return
    
    # Always allow copying
    if event.matches(QKeySequence.StandardKey.Copy):
      super().keyPressEvent(event)
      return
        
    # Prevent editing prompt area
    if cursor.position() < self.last_prompt_position and not event.matches(QKeySequence.StandardKey.Copy):
      if event.key() not in [Qt.Key.Key_Left, Qt.Key.Key_Right, Qt.Key.Key_Up, Qt.Key.Key_Down]:
        return
            
    if event.key() == Qt.Key.Key_Return:
      cursor = self.textCursor()
      cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
      cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor)
      command_line = cursor.selectedText()
      command = command_line[command_line.find(self.prompt) + len(self.prompt) + str(self.current_directory).__len__() + 1:].strip()
      
      if command:
        self.command_history.append(command)
        self.history_index = len(self.command_history)
        self.process_command(command)
      else:
        self.insert_prompt()
            
    elif event.key() == Qt.Key.Key_Up:
      if self.history_index > 0:
        self.history_index -= 1
        self.replace_current_command(self.command_history[self.history_index])
            
    elif event.key() == Qt.Key.Key_Down:
      if self.history_index < len(self.command_history) - 1:
        self.history_index += 1
        self.replace_current_command(self.command_history[self.history_index])
      else:
        self.history_index = len(self.command_history)
        self.replace_current_command("")
            
    elif event.key() == Qt.Key.Key_Left:
      if cursor.position() > self.last_prompt_position:
        super().keyPressEvent(event)
            
    elif event.key() == Qt.Key.Key_Backspace:
      if cursor.position() > self.last_prompt_position:
        super().keyPressEvent(event)
            
    elif event.key() == Qt.Key.Key_Home:
      cursor.setPosition(self.last_prompt_position)
      self.setTextCursor(cursor)
        
    else:
      super().keyPressEvent(event)

  # COMMANDS PROCESSES
  def process_command(self, command):
    parts = command.split()
    if not parts:
      self.insert_prompt()
      return
        
    if parts[0] == "help":
      self.show_help_message()
    elif parts[0] == "mkdir":
      if len(parts) < 2:
        self.appendPlainText("\nError: mkdir command requires a directory name")
        self.appendPlainText("Usage: mkdir <directory_name>")
        self.appendPlainText("Example: mkdir project")
      else:
        self.create_directory(parts[1])
    elif parts[0] == "rmdir":
      if len(parts) < 2:
        self.show_rmdir_help()
      else:
        force = "-f" in parts or "--force" in parts
        recursive = "-r" in parts or "--recursive" in parts
        # Get the directory name (last argument)
        dir_name = parts[-1]
        self.remove_directory(dir_name, force=force, recursive=recursive)
    elif parts[0] == "ls":
      self.list_files()
    elif parts[0] == "touch":
      if len(parts) < 2:
        self.appendPlainText("\nError: touch command requires a file name")
        self.appendPlainText("Usage: touch <file_name>")
        self.appendPlainText("Example: touch index.ts")
      else:
        self.create_file(parts[1])
    elif parts[0] == "cd":
      if len(parts) < 2:
        self.appendPlainText("\nError: cd command requires a directory path")
        self.appendPlainText("Usage: cd <directory_path>")
        self.appendPlainText("Examples:")
        self.appendPlainText("  cd project")
        self.appendPlainText("  cd ..")
        self.appendPlainText("  cd ../..")
      else:
        self.change_directory(parts[1])
    elif parts[0] == "pwd":
      self.show_current_directory()
    elif parts[0] == "rm":
      if len(parts) < 2:
        self.appendPlainText("\nError: rm command requires a file name")
        self.appendPlainText("Usage: rm <file_name>")
        self.appendPlainText("Example: rm test.txt")
      else:
        self.delete_file(parts[1])
    elif parts[0] == "write":
      if len(parts) < 3:
        self.appendPlainText("\nError: write command requires a file name and content")
        self.appendPlainText("Usage: write <file_name> <content>")
        self.appendPlainText('Example: write test.txt "Hello, World!"')
      else:
        content = ' '.join(parts[2:])
        self.write_to_file(parts[1], content)
    elif parts[0] == "read":
      if len(parts) < 2:
        self.appendPlainText("\nError: read command requires a file name")
        self.appendPlainText("Usage: read <file_name>")
        self.appendPlainText("Example: read test.txt")
      else:
        self.read_file(parts[1])
    elif parts[0] == "clear" or parts[0] == "cls":
      self.clear()
      self.show_welcome_message()
      self.insert_prompt()
      return
    else:
      self.appendPlainText(f"\nCommand not found: {command}")
        
    self.insert_prompt()
    self.commandEntered.emit(command)

  # SHOW THE CURRENT DIRECTORY
  def show_current_directory(self):
    self.appendPlainText(f"\n{self.current_directory}")