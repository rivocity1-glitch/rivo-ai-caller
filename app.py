import sys

from PySide6.QtCore import QThread, Signal, QTimer
from PySide6.QtWidgets import (
    QApplication, QComboBox, QHBoxLayout, QLabel, QMainWindow,
    QMessageBox, QPushButton, QProgressBar, QPlainTextEdit,
    QVBoxLayout, QWidget,
)

from src.rivo_ai_caller.audio_devices import MicrophoneMonitor, list_input_devices
from src.rivo_ai_caller.config import settings
from src.rivo_ai_caller.ollama_client import check_connection, generate_reply, OllamaError


class OllamaWorker(QThread):
    succeeded = Signal(str)
    failed = Signal(str)

    def __init__(self, prompt: str):
        super().__init__()
        self.prompt = prompt

    def run(self):
        try:
            answer = generate_reply(self.prompt, timeout=180.0)
            if not answer:
                self.failed.emit("Ollama returned an empty response. Check that the model is loaded.")
            else:
                self.succeeded.emit(answer)
        except Exception as exc:
            self.failed.emit(f"{type(exc).__name__}: {exc}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rivo AI Caller — Local Prototype")
        self.resize(820, 620)
        self.monitor = None
        self.ai_worker = None

        root = QWidget()
        layout = QVBoxLayout(root)
        layout.setSpacing(12)

        title = QLabel("Rivo AI Caller")
        title.setObjectName("title")
        subtitle = QLabel("Local-first vendor conversation prototype · Windows")
        subtitle.setObjectName("muted")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        self.call_status = QLabel("CALL STATUS: No active phone call")
        self.call_status.setObjectName("status")
        layout.addWidget(self.call_status)

        layout.addWidget(QLabel("Microphone input"))
        self.device_combo = QComboBox()
        self.refresh_devices()
        layout.addWidget(self.device_combo)

        controls = QHBoxLayout()
        self.mic_button = QPushButton("Start microphone test")
        self.mic_button.clicked.connect(self.toggle_microphone)
        refresh_button = QPushButton("Refresh devices")
        refresh_button.clicked.connect(self.refresh_devices)
        controls.addWidget(self.mic_button)
        controls.addWidget(refresh_button)
        layout.addLayout(controls)

        layout.addWidget(QLabel("Input level"))
        self.level_bar = QProgressBar()
        self.level_bar.setRange(0, 100)
        self.level_bar.setValue(0)
        self.level_bar.setFormat("%p%")
        self.level_bar.setTextVisible(True)
        self.level_bar.setMinimumHeight(22)
        self.level_bar.setObjectName("audioLevelBar")
        layout.addWidget(self.level_bar)

        ollama_row = QHBoxLayout()
        self.ollama_button = QPushButton("Test local AI (Ollama)")
        self.ollama_button.clicked.connect(self.test_ollama)
        self.ollama_status = QLabel("Ollama: not checked")
        ollama_row.addWidget(self.ollama_button)
        ollama_row.addWidget(self.ollama_status, 1)
        layout.addLayout(ollama_row)

        layout.addWidget(QLabel("AI test prompt"))
        self.prompt = QPlainTextEdit()
        self.prompt.setPlaceholderText("Ask the local model a question...")
        self.prompt.setPlainText(
            "You are RivoCity's AI assistant. In two short sentences, explain "
            "that RivoCity helps local shops receive orders from nearby customers. "
            "Do not promise guaranteed sales."
        )
        self.prompt.setMaximumHeight(100)
        layout.addWidget(self.prompt)

        self.ask_button = QPushButton("Send test prompt")
        self.ask_button.clicked.connect(self.ask_model)
        layout.addWidget(self.ask_button)

        layout.addWidget(QLabel("Local AI response / diagnostics"))
        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output, 1)

        footer = QLabel(
            f"Model: {settings.ollama_model}  ·  "
            "No calls are placed by this prototype."
        )
        footer.setObjectName("muted")
        layout.addWidget(footer)

        self.setCentralWidget(root)
        self.setStyleSheet("""
            QMainWindow, QWidget { background: #101410; color: #edf3ed; font-size: 14px; }
            QLabel#title { font-size: 28px; font-weight: 700; color: #a8e63a; }
            QLabel#muted { color: #9aa79a; }
            QLabel#status { padding: 12px; background: #1b281b; border-radius: 8px; }
            QComboBox, QPlainTextEdit {
                background: #1b241b; border: 1px solid #354335;
                border-radius: 7px; padding: 9px; color: #edf3ed;
            }
            QPushButton {
                background: #a8e63a; color: #101410; border: 0;
                border-radius: 7px; padding: 11px 15px; font-weight: 700;
            }
            QPushButton:disabled { background: #596452; color: #c0c9bc; }
            QProgressBar#audioLevelBar {
                background: #263126; border: 1px solid #354335;
                border-radius: 6px; min-height: 20px;
                color: #ffffff; text-align: center; font-weight: 700;
            }
            QProgressBar#audioLevelBar::chunk {
                border-radius: 5px;
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #2ecc71, stop: 0.60 #a8e63a,
                    stop: 0.78 #f1c40f, stop: 1 #e74c3c
                );
            }
        """)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_audio_meter)

    def refresh_devices(self):
        self.device_combo.clear()
        try:
            devices = list_input_devices()
            for device in devices:
                self.device_combo.addItem(device["name"], device["index"])
            if not devices:
                self.device_combo.addItem("No microphone input found", None)
        except Exception as exc:
            self.device_combo.addItem("Audio device error", None)
            if hasattr(self, "output"):
                self.output.appendPlainText(f"Audio discovery error: {exc}")

    def toggle_microphone(self):
        if self.monitor is not None:
            self.timer.stop()
            self.monitor.stop()
            self.monitor = None
            self.mic_button.setText("Start microphone test")
            self.level_bar.setValue(0)
            return

        device_index = self.device_combo.currentData()
        if device_index is None:
            QMessageBox.warning(self, "No microphone", "Select an available microphone.")
            return
        try:
            self.monitor = MicrophoneMonitor(device_index=device_index)
            self.monitor.start()
            self.timer.start(80)
            self.mic_button.setText("Stop microphone test")
            self.output.appendPlainText("Microphone test started. Speak near the microphone.")
        except Exception as exc:
            self.monitor = None
            QMessageBox.critical(self, "Microphone error", str(exc))

    def update_audio_meter(self):
        if self.monitor is None:
            return
        level = max(0, min(100, int(self.monitor.level() * 100)))
        self.level_bar.setValue(level)
        error = self.monitor.pop_error()
        if error:
            self.output.appendPlainText(f"Audio warning: {error}")

    def test_ollama(self):
        self.ollama_button.setEnabled(False)
        QApplication.processEvents()
        try:
            ok, details = check_connection()
            self.ollama_status.setText("Ollama: connected" if ok else "Ollama: unavailable")
            self.output.appendPlainText(f"Ollama {'OK' if ok else 'ERROR'} — {details}")
        except Exception as exc:
            self.ollama_status.setText("Ollama: error")
            self.output.appendPlainText(f"Ollama check failed: {type(exc).__name__}: {exc}")
        finally:
            self.ollama_button.setEnabled(True)

    def ask_model(self):
        prompt = self.prompt.toPlainText().strip()
        if not prompt:
            return
        if self.ai_worker is not None and self.ai_worker.isRunning():
            return

        self.ask_button.setEnabled(False)
        self.output.appendPlainText("\nYou: " + prompt)
        self.output.appendPlainText("Rivo AI is generating a response…")
        self.ai_worker = OllamaWorker(prompt)
        self.ai_worker.succeeded.connect(self.on_ai_success)
        self.ai_worker.failed.connect(self.on_ai_error)
        self.ai_worker.finished.connect(self.on_ai_finished)
        self.ai_worker.start()

    def on_ai_success(self, answer):
        self.output.appendPlainText("\nRivo AI: " + answer)

    def on_ai_error(self, message):
        self.output.appendPlainText(f"\nAI request failed: {message}")

    def on_ai_finished(self):
        self.ask_button.setEnabled(True)
        self.ai_worker = None

    def closeEvent(self, event):
        self.timer.stop()
        if self.monitor is not None:
            self.monitor.stop()
        if self.ai_worker is not None and self.ai_worker.isRunning():
            self.ai_worker.wait(2000)
        event.accept()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
