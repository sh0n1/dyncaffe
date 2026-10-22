"""Runs the simulation in a separate Python process so the GUI never shares a GIL with the model."""

import json
import os
import sys
import tempfile

from PyQt6.QtCore import QObject, QProcess, QProcessEnvironment, pyqtSignal

RESULT_MARKER = "CAFFE_GUI_OUTPUTS:"
RUNNER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "runner.py")


class SimulationWorker(QObject):
    succeeded = pyqtSignal(dict)  # {"wd": path, "wl": path, "mwd": path}
    failed = pyqtSignal(str)      # error text
    output = pyqtSignal(str)      # live text printed by the model (for a log panel later)

    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self._log = []
        self._config_path = None

        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.process.readyReadStandardOutput.connect(self._on_output)
        self.process.finished.connect(self._on_finished)
        self.process.errorOccurred.connect(self._on_error)

    def start(self):
        fd, self._config_path = tempfile.mkstemp(suffix=".json", prefix="caffe_config_")
        with os.fdopen(fd, "w") as f:
            json.dump(self.config, f)

        # Give the child the same import paths as the GUI so "from caffe import caffe" resolves
        env = QProcessEnvironment.systemEnvironment()
        env.insert("PYTHONPATH", os.pathsep.join(p for p in sys.path if p))
        self.process.setProcessEnvironment(env)

        # -u = unbuffered, so model output arrives as it is printed
        self.process.start(sys.executable, ["-u", RUNNER_PATH, self._config_path])

    def isRunning(self):
        return self.process.state() != QProcess.ProcessState.NotRunning

    def cancel(self):
        """Kill the run without emitting succeeded/failed."""
        try:
            self.process.finished.disconnect()
        except TypeError:
            pass
        self.process.kill()
        self.process.waitForFinished(2000)
        self._cleanup()

    def _on_output(self):
        text = bytes(self.process.readAllStandardOutput()).decode(errors="replace")
        self._log.append(text)
        self.output.emit(text)
        if sys.stdout is not None:  # None when launched without a console
            sys.stdout.write(text)
            sys.stdout.flush()

    def _on_finished(self, exit_code, exit_status):
        self._cleanup()
        text = "".join(self._log)

        outputs = None
        for line in text.splitlines():
            if line.startswith(RESULT_MARKER):
                outputs = json.loads(line[len(RESULT_MARKER):])

        if exit_code == 0 and outputs is not None:
            self.succeeded.emit(outputs)
        else:
            tail = "\n".join(text.strip().splitlines()[-15:])  # the traceback's last lines
            self.failed.emit(tail or f"Simulation process exited with code {exit_code}.")

    def _on_error(self, error):
        if error == QProcess.ProcessError.FailedToStart:
            self._cleanup()
            self.failed.emit("Could not start the simulation process.")

    def _cleanup(self):
        if self._config_path and os.path.exists(self._config_path):
            os.remove(self._config_path)
        self._config_path = None