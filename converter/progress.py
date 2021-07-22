import os
import re
import io
import signal
import threading
import subprocess
import shlex
import logging

from PyQt5.QtCore import pyqtSignal, QTimer
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import (
        QApplication, QDialog, QFrame, QLabel, QPushButton, QProgressBar,
        QMessageBox, QTextEdit
        )

from converter import utils


class Progress(QDialog):
    file_converted_signal = pyqtSignal()
    update_text_edit_signal = pyqtSignal(str)

    def __init__(self, files, tab, parent, test=False):

        super(Progress, self).__init__(parent)
        self.parent = parent

        self.files = files
        self.num_total_files = len(self.files)
        self.tab = tab
        if not test:
            self._type = tab.name
        self.ok = 0
        self.error = 0
        self.running = True

        self.nowQL = QLabel(self.tr('In progress: '))
        self.nowQPBar = QProgressBar()
        self.nowQPBar.setValue(0)
        self.cancelQPB = QPushButton(self.tr('Cancel'))

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        self.outputQTE = QTextEdit()
        self.outputQTE.setReadOnly(True)
        self.frame = QFrame()
        frame_layout = utils.add_to_layout('h', self.outputQTE)
        self.frame.setLayout(frame_layout)
        self.frame.hide()

        hlayout1 = utils.add_to_layout('h', None, self.nowQL, None)
        hlayout2 = utils.add_to_layout('h', line)
        hlayout3 = utils.add_to_layout('h', self.frame)
        hlayout4 = utils.add_to_layout('h', None, self.cancelQPB)
        vlayout = utils.add_to_layout(
                'v', hlayout1, self.nowQPBar, hlayout2, hlayout3, hlayout4)
        self.setLayout(vlayout)

        self.cancelQPB.clicked.connect(self.reject)
        self.file_converted_signal.connect(self.next_file)
        self.update_text_edit_signal.connect(self.update_text_edit)

        self.resize(484, 190)
        self.setWindowTitle('Media Converter - ' + self.tr('Conversion'))

        if not test:
            self.get_data()
            QTimer.singleShot(0, self.manage_conversions)

    def get_data(self):
        if self._type == 'AudioVideo':
            self.cmd = self.tab.commandQLE.text()

    def resize_dialog(self):
        height = 190 if self.frame.isVisible() else 450
        self.setMinimumSize(484, height)
        self.resize(484, height)

    def update_text_edit(self, txt):
        current = self.outputQTE.toPlainText()
        self.outputQTE.setText(current+txt)
        self.outputQTE.moveCursor(QTextCursor.End)

    def manage_conversions(self):
        if not self.running:
            return
        if not self.files:
            sum_files = self.ok + self.error
            msg = QMessageBox(self)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setWindowTitle(self.tr("Report"))
            msg.setText(self.tr("Converted: {0}/{1}".format(self.ok,sum_files)))
            msg.setModal(False)
            msg.show()

            self.cancelQPB.setText(self.tr("Close"))
        else:
            self.convert_a_file()

    def next_file(self):
        self.nowQPBar.setValue(100)
        QApplication.processEvents()
        self.files.pop(0)
        self.manage_conversions()

    def reject(self):
        if not self.files:
            QDialog.accept(self)
            return
        if self._type == 'AudioVideo':
            self.process.send_signal(signal.SIGSTOP)
        self.running = False
        reply = QMessageBox.question(
                self,
                'Media Converter - ' + self.tr('Cancel Conversion'),
                self.tr('Are you sure you want to cancel conversion?'),
                QMessageBox.Yes|QMessageBox.Cancel
                )
        if reply == QMessageBox.Yes:
            if self._type == 'AudioVideo':
                self.process.kill()
            self.running = False
            self.thread.join()
            QDialog.reject(self)
        if reply == QMessageBox.Cancel:
            self.running = True
            if self._type == 'AudioVideo':
                self.process.send_signal(signal.SIGCONT)
            else:
                self.manage_conversions()

    def convert_a_file(self):
        if not self.files:
            return
        from_file = list(self.files[0].keys())[0]
        to_file = list(self.files[0].values())[0]

        text = os.path.basename(from_file[1:-1])
        num_file = self.num_total_files - len(self.files) + 1
        text += ' ({0}/{1})'.format(num_file, self.num_total_files)

        self.nowQL.setText(self.tr('In progress:') + ' ' + text)
        self.nowQPBar.setValue(0)

        if not os.path.exists(from_file[1:-1]):
            self.error += 1
            self.file_converted_signal.emit()
            return

        def convert():
            if self._type == 'AudioVideo':
                conv_func = self.convert_video
                params = (from_file, to_file, self.cmd)

            if conv_func(*params):
                self.ok += 1
            else:
                self.error += 1

            self.file_converted_signal.emit()

        self.thread = threading.Thread(target=convert)
        self.thread.start()

    def convert_video(self, from_file, to_file, command):
        convert_cmd = '{0} -y -i {1} {2} {3}'.format(self.parent.ffmpeg_path, from_file, command, to_file)
        self.update_text_edit_signal.emit(convert_cmd + '\n')

        self.process = subprocess.Popen(
                shlex.split(convert_cmd),
                stderr=subprocess.STDOUT,
                stdout=subprocess.PIPE
                )

        final_output = myline = ''
        reader = io.TextIOWrapper(self.process.stdout, encoding='utf8')
        while True:
            out = reader.read(1)
            if out == '' and self.process.poll() is not None:
                break
            myline += out
            if out in ('\r', '\n'):
                m = re.search("Duration: ([0-9:.]+)", myline)
                if m:
                    total = utils.duration_in_seconds(m.group(1))
                n = re.search("time=([0-9:]+)", myline)
                if n:
                    time = n.group(1)
                    if ':' in time:
                        time = utils.duration_in_seconds(time)
                    now_sec = int(float(time))
                    try:
                        self.nowQPBar.setValue(100 * now_sec / total)
                    except (UnboundLocalError, ZeroDivisionError):
                        pass
                self.update_text_edit_signal.emit(myline)
                final_output += myline
                myline = ''
        self.update_text_edit_signal.emit('\n\n')

        return_code = self.process.poll()

        log_data = {
                'command' : convert_cmd,
                'returncode' : return_code,
                'type' : 'VIDEO'
                }
        log_lvl = logging.info if return_code == 0 else logging.error
        log_lvl(final_output, extra=log_data)

        return return_code == 0
