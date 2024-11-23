from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit
from PyQt6.QtGui import QKeySequence, QShortcut
from src.terminal_widget import TerminalWidget
import os

class MainWindow(QMainWindow):
  def __init__(self):
    super().__init__()
    self.setWindowTitle("Team D Awesome Terminal")
    self.setMinimumSize(800, 600)
    
    # Create central widget and layout
    central_widget = QWidget()
    self.setCentralWidget(central_widget)
    layout = QVBoxLayout(central_widget)
    layout.setContentsMargins(0, 0, 0, 0)
    
    # Create title bar
    title_label = QLabel("Team D Terminal")
    title_label.setStyleSheet("""
        QLabel {
            color: #f0f0f0;
            font-size: 16px;
            font-weight: bold;
            padding: 10px;
        }
    """)
    
    # Create current directory label
    self.current_dir_label = QLineEdit()
    self.current_dir_label.setReadOnly(True)
    self.current_dir_label.setStyleSheet("""
        QLineEdit {
            background-color: #1e1e1e;
            color: #f0f0f0;
            border: 1px solid #2d2d2d;
            border-radius: 6px;
            padding: 8px;
        }
    """)
    self.update_current_dir_label(os.path.expanduser("~"))

    # Create terminal widget
    self.terminal = TerminalWidget()
    self.terminal.commandEntered.connect(self.handle_command)
    
    # Add widgets to layout
    layout.addWidget(title_label)
    layout.addWidget(self.terminal)
    
    # Set window styling
    self.setStyleSheet("""
        QMainWindow {
            background-color: #252526;
        }
    """)
    
    # Set up shortcuts
    QShortcut(QKeySequence("Ctrl+L"), self).activated.connect(self.clear_terminal)
      
  def handle_command(self, command):
    if command.lower() == "clear" or command.lower() == "cls":
      self.clear_terminal()
    elif command.lower() == "exit":
      self.close()
    else:
      self.update_current_dir_label(self.terminal.current_directory)
          
  def clear_terminal(self):
    self.terminal.clear()
    self.terminal.insert_prompt()

  def update_current_dir_label(self, directory):
    self.current_dir_label.setText(f"$ {directory}")