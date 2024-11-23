import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from src.main_window import MainWindow

def main():
  app = QApplication(sys.argv)
  
  # Set application-wide style
  app.setStyle("Fusion")
  
  window = MainWindow()
  window.show()
  
  sys.exit(app.exec())

if __name__ == "__main__":
  main()