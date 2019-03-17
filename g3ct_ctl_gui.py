import sys
import time
import threading
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from g3ct_ctl_core import G3CTCtlCore
from g3ct_ctl_settings import G3CTCtlSettings


class G3CTCtlWindow(QMainWindow):
    def __init__(self, core_arg):
        QMainWindow.__init__(self)
        self.core = core_arg
        self.statusPollThread = G3CTCtlWindow.StatusPollThread(self, self.core)
        self.autoRunThread = G3CTCtlWindow.AutoRunThread(self, self.core)

        # coreState = core.getState()

        # self.setMinimumSize(QSize(640, 480))
        self.setWindowTitle("G3CT Reactor Control")
        # self.setMinimumWidth(400)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        self.layout = QVBoxLayout()

        qt_rectangle = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        qt_rectangle.moveCenter(center_point)
        self.move(qt_rectangle.topLeft())

        self.startStopHeaderLabel = QLabel("MIXER", self)
        self.startStopHeaderLabel.setAlignment(Qt.AlignCenter)
        self.startStopButton = QPushButton('Start Mixer', self)
        self.startStopButton.clicked.connect(self.startStopClickMethod)
        self.startStopStateLabel = QLabel("idle", self)
        self.startStopStateLabel.setAlignment(Qt.AlignCenter)
        self.startStopAutoCheck = QCheckBox("Auto Run", self)
        self.startStopAutoCheck.stateChanged.connect(self.startStopAutoStateChange)
        self.startStopAutoCheck.setChecked(False)
        self.startStopPeriod = QTimeEdit(self)
        self.startStopPeriod.setTimeSpec(Qt.LocalTime)
        self.startStopPeriod.setDisplayFormat('hh:mm:ss')
        min_time = QTime.fromString('00:01:00', 'hh:mm:ss')
        max_time = QTime.fromString('23:59:59', 'hh:mm:ss')
        self.startStopPeriod.setTimeRange(min_time, max_time)
        self.startStopPeriod.setTime(min_time)
        self.startStopPeriod.setEnabled(False)
        self.startStopCountDownLabel = QLabel("", self)
        # temporary
        self.startStopAutoCheck.setEnabled(False)
        self.startStopPeriod.setEnabled(False)
        self.startStopButton.setEnabled(False)

        self.addMaterialHeaderLabel = QLabel("SUPPLY", self)
        self.addMaterialHeaderLabel.setAlignment(Qt.AlignCenter)
        self.addMaterialButton = QPushButton('Add Material', self)
        self.addMaterialButton.clicked.connect(self.addMaterialClickMethod)
        self.addMaterialStateLabel = QLabel("idle", self)
        self.addMaterialStateLabel.setAlignment(Qt.AlignCenter)
        self.addMaterialAutoCheck = QCheckBox("Auto Run", self)
        self.addMaterialAutoCheck.stateChanged.connect(self.addMaterialAutoStateChange)
        self.addMaterialAutoCheck.setChecked(False)
        self.addMaterialPeriod = QTimeEdit(self)
        self.addMaterialPeriod.setTimeSpec(Qt.LocalTime)
        self.addMaterialPeriod.setDisplayFormat('hh:mm:ss')
        min_time = QTime.fromString('00:00:15', 'hh:mm:ss')
        max_time = QTime.fromString('23:59:59', 'hh:mm:ss')
        self.addMaterialPeriod.setTimeRange(min_time, max_time)
        self.addMaterialPeriod.setTime(min_time)
        self.addMaterialPeriod.setEnabled(False)
        self.addMaterialCountDownLabel = QLabel("", self)
        self.addMaterialRepeatCheck = QCheckBox("Repeat Limit", self)
        self.addMaterialRepeatCheck.stateChanged.connect(self.addMaterialRepeatStateChange)
        self.addMaterialRepeatCheck.setChecked(False)
        self.addMaterialRepeatCount = QSpinBox(self)
        self.addMaterialRepeatCount.setMinimum(1)
        self.addMaterialRepeatCount.setMaximum(1000)
        self.addMaterialRepeatCount.setEnabled(False)
        self.addMaterialRepeatCount.valueChanged.connect(self.addMaterialRepeatCountChange)
        self.addMaterialRepeatLabel = QLabel("", self)

        self.addWaterHeaderLabel = QLabel("WATER", self)
        self.addWaterHeaderLabel.setAlignment(Qt.AlignCenter)
        self.addWaterButton = QPushButton('Add Water', self)
        self.addWaterButton.clicked.connect(self.addWaterClickMethod)
        self.addWaterStateLabel = QLabel("idle", self)
        self.addWaterStateLabel.setAlignment(Qt.AlignCenter)
        self.addWaterAutoCheck = QCheckBox("Auto Run", self)
        self.addWaterAutoCheck.stateChanged.connect(self.addWaterAutoStateChange)
        self.addWaterAutoCheck.setChecked(False)
        self.addWaterPeriod = QTimeEdit(self)
        self.addWaterPeriod.setTimeSpec(Qt.LocalTime)
        self.addWaterPeriod.setDisplayFormat('hh:mm:ss')
        min_time = QTime.fromString('00:00:20', 'hh:mm:ss')
        max_time = QTime.fromString('23:59:59', 'hh:mm:ss')
        self.addWaterPeriod.setTimeRange(min_time, max_time)
        self.addWaterPeriod.setTime(min_time)
        self.addWaterPeriod.setEnabled(False)
        self.addWaterCountDownLabel = QLabel("", self)
        self.addWaterRepeatCheck = QCheckBox("Repeat Limit", self)
        self.addWaterRepeatCheck.stateChanged.connect(self.addWaterRepeatStateChange)
        self.addWaterRepeatCheck.setChecked(False)
        self.addWaterRepeatCount = QSpinBox(self)
        self.addWaterRepeatCount.setMinimum(1)
        self.addWaterRepeatCount.setMaximum(1000)
        self.addWaterRepeatCount.setEnabled(False)
        self.addWaterRepeatCount.valueChanged.connect(self.addWaterRepeatCountChange)
        self.addWaterRepeatLabel = QLabel("", self)

        self.removeMaterialHeaderLabel = QLabel("DISCHARGE", self)
        self.removeMaterialHeaderLabel.setAlignment(Qt.AlignCenter)
        self.removeMaterialButton = QPushButton('Remove Material', self)
        self.removeMaterialButton.clicked.connect(self.removeMaterialClickMethod)
        self.removeMaterialStateLabel = QLabel("idle", self)
        self.removeMaterialStateLabel.setAlignment(Qt.AlignCenter)
        self.removeMaterialAutoCheck = QCheckBox("Auto Run", self)
        self.removeMaterialAutoCheck.stateChanged.connect(self.removeMaterialAutoStateChange)
        self.removeMaterialAutoCheck.setChecked(False)
        self.removeMaterialPeriod = QTimeEdit(self)
        self.removeMaterialPeriod.setTimeSpec(Qt.LocalTime)
        self.removeMaterialPeriod.setDisplayFormat('hh:mm:ss')
        min_time = QTime.fromString('00:01:00', 'hh:mm:ss')
        max_time = QTime.fromString('23:59:59', 'hh:mm:ss')
        self.removeMaterialPeriod.setTimeRange(min_time, max_time)
        self.removeMaterialPeriod.setTime(min_time)
        self.removeMaterialPeriod.setEnabled(False)
        # temporary
        self.removeMaterialAutoCheck.setEnabled(False)
        self.removeMaterialPeriod.setEnabled(False)
        self.removeMaterialButton.setEnabled(False)
        self.removeMaterialCountDownLabel = QLabel("", self)

        self.dischargeValveControlHeaderLabel = QLabel("DISCHARGE VALVE", self)
        self.dischargeValveControlHeaderLabel.setAlignment(Qt.AlignCenter)
        self.dischargeValveControlButton = QPushButton('Open', self)
        self.dischargeValveControlButton.clicked.connect(self.dischargeValveControlClickMethod)
        self.dischargeValveControlStateLabel = QLabel("idle", self)
        self.dischargeValveControlStateLabel.setAlignment(Qt.AlignCenter)
        self.dischargeValveControlCountDownLabel = QLabel("", self)

        self.manualButtonBox = QHBoxLayout()

        self.startStopBox = QVBoxLayout()
        self.startStopBox.addWidget(self.startStopHeaderLabel)
        self.startStopBox.addWidget(self.startStopButton)
        self.startStopBox.addWidget(self.startStopStateLabel)
        self.startStopBox.addWidget(self.startStopAutoCheck)
        self.startStopBox.addWidget(self.startStopPeriod)
        self.startStopBox.addWidget(self.startStopCountDownLabel)
        self.startStopBox.addStretch(1)
        self.manualButtonBox.addLayout(self.startStopBox)
        self.manualButtonBox.addStretch(1)

        self.addMaterialBox = QVBoxLayout()
        self.addMaterialBox.addWidget(self.addMaterialHeaderLabel)
        self.addMaterialBox.addWidget(self.addMaterialButton)
        self.addMaterialBox.addWidget(self.addMaterialStateLabel)
        self.addMaterialBox.addWidget(self.addMaterialAutoCheck)
        self.addMaterialBox.addWidget(self.addMaterialPeriod)
        self.addMaterialBox.addWidget(self.addMaterialCountDownLabel)
        self.addMaterialBox.addWidget(self.addMaterialRepeatCheck)
        self.addMaterialBox.addWidget(self.addMaterialRepeatCount)
        self.addMaterialBox.addWidget(self.addMaterialRepeatLabel)
        self.manualButtonBox.addLayout(self.addMaterialBox)
        self.manualButtonBox.addStretch(1)

        self.addWaterBox = QVBoxLayout()
        self.addWaterBox.addWidget(self.addWaterHeaderLabel)
        self.addWaterBox.addWidget(self.addWaterButton)
        self.addWaterBox.addWidget(self.addWaterStateLabel)
        self.addWaterBox.addWidget(self.addWaterAutoCheck)
        self.addWaterBox.addWidget(self.addWaterPeriod)
        self.addWaterBox.addWidget(self.addWaterCountDownLabel)
        self.addWaterBox.addWidget(self.addWaterRepeatCheck)
        self.addWaterBox.addWidget(self.addWaterRepeatCount)
        self.addWaterBox.addWidget(self.addWaterRepeatLabel)
        self.manualButtonBox.addLayout(self.addWaterBox)
        self.manualButtonBox.addStretch(1)

        self.removeMaterialBox = QVBoxLayout()
        self.removeMaterialBox.addWidget(self.removeMaterialHeaderLabel)
        self.removeMaterialBox.addWidget(self.removeMaterialButton)
        self.removeMaterialBox.addWidget(self.removeMaterialStateLabel)
        self.removeMaterialBox.addWidget(self.removeMaterialAutoCheck)
        self.removeMaterialBox.addWidget(self.removeMaterialPeriod)
        self.removeMaterialBox.addWidget(self.removeMaterialCountDownLabel)
        self.removeMaterialBox.addStretch(1)
        self.manualButtonBox.addLayout(self.removeMaterialBox)

        self.dischargeValveControlBox = QVBoxLayout()
        self.dischargeValveControlBox.addWidget(self.dischargeValveControlHeaderLabel)
        self.dischargeValveControlBox.addWidget(self.dischargeValveControlButton)
        self.dischargeValveControlBox.addWidget(self.dischargeValveControlStateLabel)
        self.dischargeValveControlBox.addWidget(self.dischargeValveControlCountDownLabel)
        self.dischargeValveControlBox.addStretch(1)
        self.manualButtonBox.addLayout(self.dischargeValveControlBox)

        self.layout.addLayout(self.manualButtonBox)

        self.exitButton = QPushButton('Quit', self)
        self.exitButton.clicked.connect(self.exitClickMethod)

        self.emergencyStopButton = QPushButton('Emergency Stop', self)
        self.emergencyStopButton.clicked.connect(self.emergencyStopClickMethod)
        self.emergencyStopButton.setStyleSheet("background-color: red")

        self.commonButtonBox = QHBoxLayout()
        self.commonButtonBox.addWidget(self.emergencyStopButton)
        self.commonButtonBox.addWidget(self.exitButton)
        self.layout.addLayout(self.commonButtonBox)

        central_widget.setLayout(self.layout)

        self.statusPollThread.start()
        self.autoRunThread.start()

    def setAddMaterialStateLabel(self, text):
        self.addMaterialStateLabel.setText(text)

    #        if text == 'idle':
    #            self.addMaterialStateLabel.setStyleSheet('color: none')
    #        elif text == 'error':
    #            self.addMaterialStateLabel.setStyleSheet('color: red')
    #        else:
    #            self.addMaterialStateLabel.setStyleSheet('color: green')

    def setAddWaterStateLabel(self, text):
        self.addWaterStateLabel.setText(text)

    #        if text == 'idle':
    #            self.addWaterStateLabel.setStyleSheet('color: none')
    #        elif text == 'error':
    #            self.addWaterStateLabel.setStyleSheet('color: red')
    #        else:
    #            self.addWaterStateLabel.setStyleSheet('color: green')

    def setRemoveMaterialStateLabel(self, text):
        self.removeMaterialStateLabel.setText(text)

    def setDischargeValveControlStateLabel(self, text):
        self.dischargeValveControlStateLabel.setText(text)

    def enableDischargeValveControlButton(self):
        self.dischargeValveControlButton.setEnabled(True)

    def setStartStopStateLabel(self, text):
        self.startStopStateLabel.setText(text)

    class StatusPollThread(threading.Thread):
        def __init__(self, gui, core_arg):
            threading.Thread.__init__(self)
            self.gui = gui
            self.core = core_arg
            self.stopFlag = False

        def setStopFlag(self):
            self.stopFlag = True

        def run(self):
            while not self.stopFlag:
                add_water_state = self.core.getAddWaterState()
                self.gui.setAddWaterStateLabel(add_water_state)
                add_material_state = self.core.getAddMaterialState()
                self.gui.setAddMaterialStateLabel(add_material_state)
                remove_material_state = self.core.getRemoveMaterialState()
                self.gui.setRemoveMaterialStateLabel(remove_material_state)
                discharge_valve_state = self.core.getDischargeValveControlState()
                self.gui.setDischargeValveControlStateLabel(discharge_valve_state)
                if discharge_valve_state == "opened" or discharge_valve_state == "closed":
                    self.gui.enableDischargeValveControlButton()
                mixer_state = core.getActualMixerState()
                self.gui.setStartStopStateLabel(mixer_state)
                time.sleep(1)

    def setAddMaterialCountDownLabel(self, text):
        self.addMaterialCountDownLabel.setText(text)

    def setAddMaterialRepeatLabel(self, text):
        self.addMaterialRepeatLabel.setText(text)

    def cancelAddMaterialAutoRun(self):
        self.addMaterialAutoCheck.setChecked(False)
        self.addMaterialRepeatCheck.setChecked(False)

    def setAddWaterCountDownLabel(self, text):
        self.addWaterCountDownLabel.setText(text)

    def setAddWaterRepeatLabel(self, text):
        self.addWaterRepeatLabel.setText(text)

    def cancelAddWaterAutoRun(self):
        self.addWaterAutoCheck.setChecked(False)
        self.addWaterRepeatCheck.setChecked(False)

    def setRemoveMaterialCountDownLabel(self, text):
        self.removeMaterialCountDownLabel.setText(text)

    def setStartStopCountDownLabel(self, text):
        self.startStopCountDownLabel.setText(text)

    class AutoRunThread(threading.Thread):
        def __init__(self, gui, core_arg):
            threading.Thread.__init__(self)
            self.gui = gui
            self.core = core_arg
            self.stopFlag = False

            self.mixerAutoRun = False
            self.mixerPeriod = 0
            self.mixerTriggerTime = QDateTime()
            self.addMaterialAutoRun = False
            self.addMaterialPeriod = 0
            self.addMaterialTriggerTime = QDateTime()
            self.addMaterialRepeatLimit = False
            self.addMaterialRepeatCount = 0
            self.addMaterialRepeatIter = 0
            self.addWaterAutoRun = False
            self.addWaterPeriod = 0
            self.addWaterTriggerTime = QDateTime()
            self.addWaterRepeatLimit = False
            self.addWaterRepeatCount = 0
            self.addWaterRepeatIter = 0
            self.removeMaterialAutoRun = False
            self.removeMaterialPeriod = 0
            self.removeMaterialTriggerTime = QDateTime()

        def setStopFlag(self):
            self.stopFlag = True

        def setMixerAutoRun(self, state, period):
            self.mixerAutoRun = state
            self.mixerPeriod = period
            if self.mixerAutoRun:
                self.mixerTriggerTime = QDateTime.currentDateTime().addSecs(period)

        def setAddMaterialAutoRun(self, state, period):
            self.addMaterialAutoRun = state
            self.addMaterialPeriod = period
            if self.addMaterialAutoRun:
                self.addMaterialTriggerTime = QDateTime.currentDateTime().addSecs(period)

        def setAddMaterialRepeatCount(self, state, count):
            self.addMaterialRepeatLimit = state
            self.addMaterialRepeatCount = count
            self.addMaterialRepeatIter = 0

        def setAddWaterAutoRun(self, state, period):
            self.addWaterAutoRun = state
            self.addWaterPeriod = period
            if self.addWaterAutoRun:
                self.addWaterTriggerTime = QDateTime.currentDateTime().addSecs(period)

        def setAddWaterRepeatCount(self, state, count):
            self.addWaterRepeatLimit = state
            self.addWaterRepeatCount = count
            self.addWaterRepeatIter = 0

        def setRemoveMaterialAutoRun(self, state, period):
            self.removeMaterialAutoRun = state
            self.removeMaterialPeriod = period
            if self.removeMaterialAutoRun:
                self.removeMaterialTriggerTime = QDateTime.currentDateTime().addSecs(period)

        def run(self):
            while not self.stopFlag:

                if not self.mixerAutoRun:
                    self.gui.setStartStopCountDownLabel("")
                else:
                    if self.mixerTriggerTime.__gt__(QDateTime.currentDateTime()):
                        rem = QDateTime.currentDateTime().secsTo(self.mixerTriggerTime)
                        self.gui.setStartStopCountDownLabel(str(rem) + ' seconds')
                    else:
                        self.mixerTriggerTime = QDateTime.currentDateTime().addSecs(self.mixerPeriod)
                        self.gui.setStartStopCountDownLabel('triggering')
                        # emulate button press
                        self.gui.startStopClickMethod()

                if not self.addMaterialAutoRun:
                    self.gui.setAddMaterialCountDownLabel("")
                else:
                    if self.addMaterialTriggerTime.__gt__(QDateTime.currentDateTime()):
                        rem = QDateTime.currentDateTime().secsTo(self.addMaterialTriggerTime)
                        self.gui.setAddMaterialCountDownLabel(str(rem) + ' seconds')
                    else:
                        repeat_limit_reached = False
                        if self.addMaterialRepeatLimit:
                            if self.addMaterialRepeatIter >= self.addMaterialRepeatCount:
                                self.gui.setAddMaterialRepeatLabel("done")
                                self.gui.cancelAddMaterialAutoRun()
                                repeat_limit_reached = True
                            else:
                                self.addMaterialRepeatIter = self.addMaterialRepeatIter + 1
                                self.gui.setAddMaterialRepeatLabel("repetition " + str(self.addMaterialRepeatIter))
                        if not repeat_limit_reached:
                            self.addMaterialTriggerTime = QDateTime.currentDateTime().addSecs(self.addMaterialPeriod)
                            self.gui.setAddMaterialCountDownLabel('triggering')
                            # emulate button press
                            self.gui.addMaterialClickMethod()

                if not self.addWaterAutoRun:
                    self.gui.setAddWaterCountDownLabel("")
                else:
                    if self.addWaterTriggerTime.__gt__(QDateTime.currentDateTime()):
                        rem = QDateTime.currentDateTime().secsTo(self.addWaterTriggerTime)
                        self.gui.setAddWaterCountDownLabel(str(rem) + ' seconds')
                    else:
                        repeat_limit_reached = False
                        if self.addWaterRepeatLimit:
                            if self.addWaterRepeatIter >= self.addWaterRepeatCount:
                                self.gui.setAddWaterRepeatLabel("done")
                                self.gui.cancelAddWaterAutoRun()
                                repeat_limit_reached = True
                            else:
                                self.addWaterRepeatIter = self.addWaterRepeatIter + 1
                                self.gui.setAddWaterRepeatLabel("repetition " + str(self.addWaterRepeatIter))
                        if not repeat_limit_reached:
                            self.addWaterTriggerTime = QDateTime.currentDateTime().addSecs(self.addWaterPeriod)
                            self.gui.setAddWaterCountDownLabel('triggering')
                            # emulate button press
                            self.gui.addWaterClickMethod()

                if not self.removeMaterialAutoRun:
                    self.gui.setRemoveMaterialCountDownLabel("")
                else:
                    if self.removeMaterialTriggerTime.__gt__(QDateTime.currentDateTime()):
                        rem = QDateTime.currentDateTime().secsTo(self.removeMaterialTriggerTime)
                        self.gui.setRemoveMaterialCountDownLabel(str(rem) + ' seconds')
                    else:
                        self.removeMaterialTriggerTime = QDateTime.currentDateTime().addSecs(self.removeMaterialPeriod)
                        self.gui.setRemoveMaterialCountDownLabel('triggering')
                        # emulate button press
                        self.gui.removeMaterialClickMethod()

                time.sleep(1)

    def exitClickMethod(self):
        print('Clicked exit button.')
        self.statusPollThread.setStopFlag()
        self.autoRunThread.setStopFlag()
        QtCore.QCoreApplication.instance().exit(0)

    def emergencyStopClickMethod(self):
        print('Clicked emergency stop button.')
        self.core.emergencyStop()
        QtCore.QCoreApplication.instance().exit(0)

    def startStopClickMethod(self):
        print('Clicked startStop button.')
        self.core.startStopMixer()
        if self.core.getCommandedMixerState() == "stop":
            self.startStopButton.setText("Start Mixer")
        else:
            self.startStopButton.setText("Stop Mixer")

    def addMaterialClickMethod(self):
        print('Clicked addMaterial button.')
        self.core.addMaterial()

    def addWaterClickMethod(self):
        print('Clicked addWater button.')
        self.core.addWater()

    def removeMaterialClickMethod(self):
        print('Clicked removeMaterial button.')
        self.core.removeMaterial()

    def dischargeValveControlClickMethod(self):
        print('Clicked dischargeValveControl button.')
        self.core.dischargeValveControl()
        if self.core.getCommandedDischargeValveControlState() == "open":
            self.dischargeValveControlButton.setText("Close")
        else:
            self.dischargeValveControlButton.setText("Open")
        # disable the button until operation is complete
        self.dischargeValveControlButton.setEnabled(False)

    def startStopAutoStateChange(self, state):
        print ('startStopAuto state is ' + str(state))
        if state == QtCore.Qt.Checked:
            self.startStopPeriod.setEnabled(True)
            self.startStopButton.setEnabled(False)
            h = self.startStopPeriod.time().hour()
            m = self.startStopPeriod.time().minute()
            s = self.startStopPeriod.time().second()
            period = (((h * 60) + m) * 60) + s
            self.autoRunThread.setMixerAutoRun(True, period)
        else:
            self.startStopPeriod.setEnabled(False)
            self.startStopButton.setEnabled(True)
            self.autoRunThread.setMixerAutoRun(False, 0)

    def addMaterialAutoStateChange(self, state):
        print ('addMaterialAuto state is ' + str(state))
        if state == QtCore.Qt.Checked:
            self.addMaterialPeriod.setEnabled(True)
            self.addMaterialButton.setEnabled(False)
            print self.addMaterialPeriod.time()
            h = self.addMaterialPeriod.time().hour()
            m = self.addMaterialPeriod.time().minute()
            s = self.addMaterialPeriod.time().second()
            print h, m, s
            period = (((h * 60) + m) * 60) + s
            self.autoRunThread.setAddMaterialAutoRun(True, period)
        else:
            self.addMaterialPeriod.setEnabled(False)
            self.addMaterialButton.setEnabled(True)
            self.autoRunThread.setAddMaterialAutoRun(False, 0)

    def addMaterialRepeatStateChange(self, state):
        print ('addMaterialRepeat state is ' + str(state))
        if state == QtCore.Qt.Checked:
            self.addMaterialRepeatCount.setEnabled(True)
            count = self.addMaterialRepeatCount.value()
            self.autoRunThread.setAddMaterialRepeatCount(True, count)
            self.addMaterialRepeatLabel.setText("")
        else:
            self.addMaterialRepeatCount.setEnabled(False)
            self.autoRunThread.setAddMaterialRepeatCount(False, 0)

    def addMaterialRepeatCountChange(self):
        if self.addMaterialRepeatCheck.isChecked():
            count = self.addMaterialRepeatCount.value()
            self.autoRunThread.setAddMaterialRepeatCount(True, count)

    def addWaterAutoStateChange(self, state):
        print ('addWaterAuto state is ' + str(state))
        if state == QtCore.Qt.Checked:
            self.addWaterPeriod.setEnabled(True)
            self.addWaterButton.setEnabled(False)
            h = self.addWaterPeriod.time().hour()
            m = self.addWaterPeriod.time().minute()
            s = self.addWaterPeriod.time().second()
            period = (((h * 60) + m) * 60) + s
            self.autoRunThread.setAddWaterAutoRun(True, period)
        else:
            self.addWaterPeriod.setEnabled(False)
            self.addWaterButton.setEnabled(True)
            self.autoRunThread.setAddWaterAutoRun(False, 0)

    def addWaterRepeatStateChange(self, state):
        print ('addWaterRepeat state is ' + str(state))
        if state == QtCore.Qt.Checked:
            self.addWaterRepeatCount.setEnabled(True)
            count = self.addWaterRepeatCount.value()
            self.autoRunThread.setAddWaterRepeatCount(True, count)
            self.addWaterRepeatLabel.setText("")
        else:
            self.addWaterRepeatCount.setEnabled(False)
            self.autoRunThread.setAddWaterRepeatCount(False, 0)

    def addWaterRepeatCountChange(self):
        if self.addWaterRepeatCheck.isChecked():
            count = self.addWaterRepeatCount.value()
            self.autoRunThread.setAddWaterRepeatCount(True, count)

    def removeMaterialAutoStateChange(self, state):
        print ('removeMaterialAuto state is ' + str(state))
        if state == QtCore.Qt.Checked:
            self.removeMaterialPeriod.setEnabled(True)
            self.removeMaterialButton.setEnabled(False)
            h = self.removeMaterialPeriod.time().hour()
            m = self.removeMaterialPeriod.time().minute()
            s = self.removeMaterialPeriod.time().second()
            period = (((h * 60) + m) * 60) + s
            self.autoRunThread.setRemoveMaterialAutoRun(True, period)
        else:
            self.removeMaterialPeriod.setEnabled(False)
            self.removeMaterialButton.setEnabled(True)
            self.autoRunThread.setRemoveMaterialAutoRun(False, 0)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    settings = G3CTCtlSettings("g3ct_ctl_settings.json")
    core = G3CTCtlCore(settings)
    mainWin = G3CTCtlWindow(core)
    mainWin.show()
    sys.exit(app.exec_())
 #Test Commit