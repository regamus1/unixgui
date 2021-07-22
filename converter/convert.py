import os
import sys

from PyQt5.QtCore import (QSettings, Qt)
from PyQt5.QtWidgets import (
        QAbstractItemView, QApplication, QFileDialog, QLabel,
        QLineEdit, QMainWindow, QMessageBox, QPushButton, QShortcut, QTabWidget,
        QToolButton, QWidget
        )

from converter import utils
from converter import config
from converter import progress
from converter.audiovideotab import AudioVideoTab

class ValidationError(Exception):
    pass


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.fnames = []
        addQPB = QPushButton(self.tr('Add'))
        delQPB = QPushButton(self.tr('Delete'))
        clearQPB = QPushButton(self.tr('Clear'))
        vlayout1 = utils.add_to_layout('v', addQPB, delQPB, clearQPB, None)

        self.filesList = utils.FilesList()
        self.filesList.setSelectionMode(QAbstractItemView.ExtendedSelection)
        hlayout1 = utils.add_to_layout('h', self.filesList, vlayout1)

        outputQL = QLabel(self.tr('Output folder:'))
        self.toQLE = QLineEdit()
        self.toQLE.setReadOnly(True)
        self.toQTB = QToolButton()
        self.toQTB.setText('...')
        hlayout2 = utils.add_to_layout('h', outputQL, self.toQLE, self.toQTB)

        self.audiovideo_tab = AudioVideoTab(self)
        self.tabs = [self.audiovideo_tab]
        tab_names = [self.tr('Audio/Video')]

        self.tabWidget = QTabWidget()
        for num, tab in enumerate(tab_names):
            self.tabWidget.addTab(self.tabs[num], tab)
        self.tabWidget.setCurrentIndex(0)

        convertQPB = QPushButton(self.tr('&Convert'))

        hlayout4 = utils.add_to_layout('h', None, convertQPB)
        final_layout = utils.add_to_layout(
                'v', hlayout1, self.tabWidget, hlayout2, hlayout4)

        self.dependenciesQL = QLabel()
        self.statusBar().addPermanentWidget(self.dependenciesQL, stretch=1)

        widget = QWidget()
        widget.setLayout(final_layout)
        self.setCentralWidget(widget)

        convertAction = utils.create_action(
                self, self.tr('Convert'), 'Ctrl+C', None,
                self.tr('Convert files'), self.start_conversion
                )

        self.filesList.dropped.connect(self.filesList_add_dragged)
        addQPB.clicked.connect(self.filesList_add)
        delQPB.clicked.connect(self.filesList_delete)
        clearQPB.clicked.connect(self.filesList_clear)
        self.tabWidget.currentChanged.connect(
                lambda: self.tabs[0].moreQPB.setChecked(False))
        self.toQTB.clicked.connect(self.get_output_folder)
        convertQPB.clicked.connect(convertAction.triggered)

        del_shortcut = QShortcut(self)
        del_shortcut.setKey(Qt.Key_Delete)
        del_shortcut.activated.connect(self.filesList_delete)

        self.setWindowTitle('Media Converter')

        self.load_settings()

        self.audiovideo_tab.set_default_command()
        self.toQLE.setText(self.default_output)

        self.filesList_update()

    def load_settings(self):
        settings = QSettings()

        self.overwrite_existing = settings.value('overwrite_existing', type=bool)
        self.default_output = settings.value('default_output', type=str)
        self.prefix = settings.value('prefix', type=str)
        self.suffix = settings.value('suffix', type=str)
        self.ffmpeg_path = settings.value('ffmpeg_path', type=str)
        self.default_command = (settings.value('default_command', type=str) or
                config.default_ffmpeg_cmd)

        extraformats_video = (settings.value('extraformats_video') or [])

        self.audiovideo_tab.fill_video_comboboxes(extraformats_video)

    def get_current_tab(self):
        for i in self.tabs:
            if self.tabs.index(i) == self.tabWidget.currentIndex():
                return i

    def filesList_update(self):
        self.filesList.clear()
        for i in self.fnames:
            self.filesList.addItem(i)

    def filesList_add(self):
 
        fnames = QFileDialog.getOpenFileNames(self, 'Media Converter - ' +
                self.tr('Choose File'), config.home,
                options=QFileDialog.HideNameFilterDetails)[0]

        if fnames:
            for i in fnames:
                if not i in self.fnames:
                    self.fnames.append(i)
            self.filesList_update()

    def filesList_add_dragged(self, links):
        for path in links:
            if os.path.isfile(path) and not path in self.fnames:
                self.fnames.append(path)
        self.filesList_update()

    def filesList_delete(self):
        items = self.filesList.selectedItems()
        if items:
            for i in items:
                self.fnames.remove(i.text())
            self.filesList_update()

    def filesList_clear(self):
        self.fnames = []
        self.filesList_update()

    def clear_all(self):
        self.toQLE.clear()
        self.filesList_clear()

        self.audiovideo_tab.clear()

    def get_output_folder(self):
        if self.toQLE.isEnabled():
            output = QFileDialog.getExistingDirectory(
                    self, 'Media Converter - ' +
                    self.tr('Choose output destination'),
                    config.home)
            if output:
                self.toQLE.setText(output)

    def ok_to_continue(self):
        try:
            if not self.fnames:
                raise ValidationError(
                        self.tr('You must add at least one file to convert!'))
            if not self.get_current_tab().ok_to_continue():
                return False
            return True

        except ValidationError as e:
            QMessageBox.warning(
                    self, 'Media Converter - ' + self.tr('Error!'), str(e))
            return False

    def start_conversion(self):
        if not self.ok_to_continue():
            return

        tab = self.get_current_tab()
        ext_to = '.' + tab.extQCB.currentText()

        _list = utils.create_paths_list(
                self.fnames, ext_to, self.prefix, self.suffix,
                self.toQLE.text()
                )

        dialog = progress.Progress(_list, tab, self)
        dialog.show()

def main():
    app = QApplication([i.encode('utf-8') for i in sys.argv])
    app.setApplicationName('FF Multi Converter')

    converter = MainWindow()
    converter.show()
    app.exec_()
