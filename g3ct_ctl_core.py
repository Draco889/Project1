import threading
import collections
import time
import datetime
import subprocess
from g3ct_ctl_settings import G3CTCtlSettings


class G3CTCtlCore:

    def __init__(self, settings):
        self.state = "initializing"
        self.settings = settings
        self.interfaceLock = threading.Lock()
        self.mixerLock = threading.Lock()
        self.dischargeValveControlLock = threading.Lock()
        self.addWaterState = ""
        self.setAddWaterState("idle")
        self.waterThread = None
        self.addMaterialState = ""
        self.setAddMaterialState("idle")
        self.materialThread = None
        self.removeMaterialState = ""
        self.setRemoveMaterialState("idle")
        self.removeMaterialThread = None
        self.commandedDischargeValveControlState = "close"
        self.actualDischargeValveControlState = "closed"
        self.dischargeValveThread = None
        self.commandedMixerState = "stop"
        self.actualMixerState = "stopped"
        self.logfile = open(self.settings.getLogFilename(), "a")

    def getState(self):
        return self.state

    def sendCommand(self, cmd):
        print cmd
        return "ack"
        self.interfaceLock.acquire(True)
        print(cmd)
        args = cmd.split(" ")
        try:
            ret_str = subprocess.check_output(args)
        except subprocess.CalledProcessError:
            ret_str = "FAILURE"
        self.interfaceLock.release()
        return ret_str.rstrip('\n')

    ##########################################################################

    class WaterDoserThread(threading.Thread):
        def __init__(self, core, cmd_dict, duration_dict):
            threading.Thread.__init__(self)
            self.core = core
            self.cmdDict = cmd_dict
            self.durationDict = duration_dict

        def run(self):
            self.core.logfile.write(str(datetime.datetime.now()) + " adding water\n")
            self.core.setAddWaterState("opening")
            cmd_ret = self.core.sendCommand(self.cmdDict["openCmd"])
            if cmd_ret != "ack":
                print cmd_ret
                self.core.setAddWaterState("error")
                return
            time.sleep(self.durationDict["open"])
            self.core.sendCommand(self.cmdDict["stopCmd"])
            if cmd_ret != "ack":
                print cmd_ret
                self.core.setAddWaterState("error")
                return
            self.core.setAddWaterState("closing")
            self.core.sendCommand(self.cmdDict["closeCmd"])
            if cmd_ret != "ack":
                print cmd_ret
                self.core.setAddWaterState("error")
                return
            time.sleep(self.durationDict["close"])
            self.core.sendCommand(self.cmdDict["stopCmd"])
            if cmd_ret != "ack":
                print cmd_ret
                self.core.setAddWaterState("error")
                return
            self.core.setAddWaterState("idle")
            self.core.logfile.write(str(datetime.datetime.now()) + " added water\n")

    def setAddWaterState(self, state):
        self.addWaterState = state

    def getAddWaterState(self):
        return self.addWaterState

    def addWater(self):
        com_port = self.settings.getComPort()
        controller = self.settings.getWaterDoserController()
        motor = self.settings.getWaterDoserMotorNumber()
        open_direction = self.settings.getWaterDoserMotorOpenDirection()
        open_duration = self.settings.getWaterDoserMotorOpenDuration()
        close_direction = self.settings.getWaterDoserMotorCloseDirection()
        close_duration = self.settings.getWaterDoserMotorCloseDuration()
        print controller, motor, open_direction, open_duration, close_direction, close_duration
        cmd_dict = collections.OrderedDict()
        duration_dict = collections.OrderedDict()

        cmd_dict["openCmd"] = "ctrl-comm " + str(com_port) + " set ctl " + str(controller) + " motor " + str(
            motor) + " dir " + str(open_direction) + " speed 255"
        cmd_dict["closeCmd"] = "ctrl-comm " + str(com_port) + " set ctl " + str(controller) + " motor " + str(
            motor) + " dir " + str(close_direction) + " speed 255"
        cmd_dict["stopCmd"] = "ctrl-comm " + str(com_port) + " set ctl " + str(controller) + " motor " + str(
            motor) + " off"

        duration_dict["open"] = open_duration
        duration_dict["close"] = close_duration

        self.waterThread = G3CTCtlCore.WaterDoserThread(self, cmd_dict, duration_dict)
        self.waterThread.start()

    ##########################################################################

    def setAddMaterialState(self, state):
        self.addMaterialState = state

    def getAddMaterialState(self):
        return self.addMaterialState

    class MaterialDoserThread(threading.Thread):
        def __init__(self, core, cmd_dict, duration_dict):
            threading.Thread.__init__(self)
            self.core = core
            self.cmdDict = cmd_dict
            self.durationDict = duration_dict

        def run(self):

            self.core.logfile.write(str(datetime.datetime.now()) + " adding material\n")
            self.core.setAddMaterialState("opening top")
            cmd_ret = self.core.sendCommand(self.cmdDict["openCmdTop"])
            if cmd_ret != "ack":
                print cmd_ret
                self.core.setAddMaterialState("error")
                return

            time.sleep(self.durationDict["openTop"])

            self.core.setAddMaterialState("opening bottom")
            cmd_ret = self.core.sendCommand(self.cmdDict["openCmdBottom"])
            if cmd_ret != "ack":
                print cmd_ret
                self.core.setAddMaterialState("error")
                return

            # time.sleep(self.durationDict["openBottom"])

            self.core.setAddMaterialState("closing top")
            cmd_ret = self.core.sendCommand(self.cmdDict["closeCmdTop"])
            if cmd_ret != "ack":
                print cmd_ret
                self.core.setAddMaterialState("error")
                return

            time.sleep(self.durationDict["closeTop"])

            self.core.setAddMaterialState("closing bottom")
            cmd_ret = self.core.sendCommand(self.cmdDict["closeCmdBottom"])
            if cmd_ret != "ack":
                print cmd_ret
                self.core.setAddMaterialState("error")
                return

            time.sleep(self.durationDict["closeBottom"])

            # fail-safe to stop in case of linear motors
            cmd_ret = self.core.sendCommand(self.cmdDict["stopCmdTop"])
            if cmd_ret != "ack":
                print cmd_ret
                self.core.setAddMaterialState("error")
                return
            cmd_ret = self.core.sendCommand(self.cmdDict["stopCmdBottom"])
            if cmd_ret != "ack":
                print cmd_ret
                self.core.setAddMaterialState("error")
                return

            self.core.setAddMaterialState("idle")
            self.core.logfile.write(str(datetime.datetime.now()) + " added material\n")

    def addMaterial(self):
        com_port = self.settings.getComPort()
        controller = self.settings.getMaterialDoserController()
        motor = self.settings.getMaterialDoserTopMotorNumber()
        open_direction = self.settings.getMaterialDoserTopMotorOpenDirection()
        open_duration = self.settings.getMaterialDoserTopMotorOpenDuration()
        close_direction = self.settings.getMaterialDoserTopMotorCloseDirection()
        close_duration = self.settings.getMaterialDoserTopMotorCloseDuration()
        print controller, motor, open_direction, open_duration, close_direction, close_duration
        cmd_dict = collections.OrderedDict()
        duration_dict = collections.OrderedDict()

        cmd_dict["openCmdTop"] = "ctrl-comm " + str(com_port) + " set ctl " + str(controller) + " motor " + str(
            motor) + " dir " + str(open_direction) + " speed 255"
        cmd_dict["closeCmdTop"] = "ctrl-comm " + str(com_port) + " set ctl " + str(controller) + " motor " + str(
            motor) + " off"
        cmd_dict["stopCmdTop"] = "ctrl-comm " + str(com_port) + " set ctl " + str(controller) + " motor " + str(
            motor) + " off"

        duration_dict["openTop"] = open_duration
        duration_dict["closeTop"] = close_duration

        controller = self.settings.getMaterialBunkerController()
        motor = self.settings.getMaterialBunkerMotorNumber()
        direction = self.settings.getMaterialBunkerMotorDirection()
        duration = self.settings.getMaterialBunkerMotorDuration()

        cmd_dict["spinCmdBunker"] = "ctrl-comm " + str(com_port) + " set ctl " + str(controller) + " motor " + str(
            motor) + " dir " + str(direction) + " speed 255"
        cmd_dict["stopCmdBunker"] = "ctrl-comm " + str(com_port) + " set ctl " + str(controller) + " motor " + str(
            motor) + " off"
        duration_dict["spinBunker"] = duration

        controller = self.settings.getMaterialDoserController()
        motor = self.settings.getMaterialDoserBottomMotorNumber()
        open_direction = self.settings.getMaterialDoserBottomMotorOpenDirection()
        open_duration = self.settings.getMaterialDoserBottomMotorOpenDuration()
        close_direction = self.settings.getMaterialDoserBottomMotorCloseDirection()
        close_duration = self.settings.getMaterialDoserBottomMotorCloseDuration()
        print controller, motor, open_direction, open_duration, close_direction, close_duration

        cmd_dict["openCmdBottom"] = "ctrl-comm " + str(com_port) + " set ctl " + str(controller) + " motor " + str(
            motor) + " dir " + str(open_direction) + " speed 255"
        cmd_dict["closeCmdBottom"] = "ctrl-comm " + str(com_port) + " set ctl " + str(controller) + " motor " + str(
            motor) + " off"
        cmd_dict["stopCmdBottom"] = "ctrl-comm " + str(com_port) + " set ctl " + str(controller) + " motor " + str(
            motor) + " off"

        duration_dict["openBottom"] = open_duration
        duration_dict["closeBottom"] = close_duration

        self.materialThread = G3CTCtlCore.MaterialDoserThread(self, cmd_dict, duration_dict)
        self.materialThread.start()

    ##########################################################################

    class RemoveMaterialThread(threading.Thread):
        def __init__(self, core, cmd_dict, duration_dict):
            threading.Thread.__init__(self)
            self.core = core
            self.cmdDict = cmd_dict
            self.durationDict = duration_dict

        def run(self):
            self.core.setRemoveMaterialState("stopping mixer")
            cmd_ret = self.core.sendCommand(self.cmdDict["stopCmd1"])
            if cmd_ret != "ack":
                print cmd_ret
                self.core.setRemoveMaterialState("error")
                return
            cmd_ret = self.core.sendCommand(self.cmdDict["stopCmd2"])
            if cmd_ret != "ack":
                print cmd_ret
                self.core.setRemoveMaterialState("error")
                return
            time.sleep(self.durationDict["deadTime"])

            self.core.setRemoveMaterialState("removing material")
            self.core.sendCommand(self.cmdDict["reverseCmd"])
            if cmd_ret != "ack":
                print cmd_ret
                self.core.setRemoveMaterialState("error")
                return
            time.sleep(self.durationDict["removalTime"])

            self.core.setRemoveMaterialState("stopping mixer")
            self.core.sendCommand(self.cmdDict["stopCmd1"])
            if cmd_ret != "ack":
                print cmd_ret
                self.core.setRemoveMaterialState("error")
                return
            self.core.sendCommand(self.cmdDict["stopCmd2"])
            if cmd_ret != "ack":
                print cmd_ret
                self.core.setRemoveMaterialState("error")
                return
            time.sleep(self.durationDict["deadTime"])

            self.core.sendCommand(self.cmdDict["restoreCmd"])
            if cmd_ret != "ack":
                print cmd_ret
                self.core.setRemoveMaterialState("error")
                return
            self.core.setRemoveMaterialState("idle")
            if self.core.commandedMixerState == "stop":
                self.core.actualMixerState = "stopped"
            else:
                self.core.actualMixerState = "running"

    def setRemoveMaterialState(self, state):
        self.removeMaterialState = state

    def getRemoveMaterialState(self):
        return self.removeMaterialState

    def removeMaterial(self):
        com_port = self.settings.getComPort()
        controller = self.settings.getMixerController()
        forward_switch = self.settings.getMixerForwardSwitch()
        reverse_switch = self.settings.getMixerReverseSwitch()
        dead_time = self.settings.getMixerDeadTime()
        removal_time = self.settings.getMixerMaterialRemovalTime()

        cmd_dict = collections.OrderedDict()
        duration_dict = collections.OrderedDict()

        cmd_dict["stopCmd1"] = "ctrl-comm " + str(com_port) + " set ctl " + str(controller) + " motor " + str(
            forward_switch) + " dir 1 speed 0"
        cmd_dict["stopCmd2"] = "ctrl-comm " + str(com_port) + " set ctl " + str(controller) + " motor " + str(
            reverse_switch) + " dir 1 speed 0"
        cmd_dict["reverseCmd"] = "ctrl-comm " + str(com_port) + " set ctl " + str(controller) + " motor " + str(
            reverse_switch) + " dir 1 speed 255"
        cmd_dict["restoreCmd"] = "ctrl-comm " + str(com_port) + " set ctl " + str(controller) + " motor " + str(
            forward_switch) + " dir 1 speed 0"
        if self.commandedMixerState == "run":
            cmd_dict["restoreCmd"] = "ctrl-comm " + str(com_port) + " set ctl " + str(controller) + " motor " + str(
                forward_switch) + " on"

        duration_dict["deadTime"] = dead_time
        duration_dict["removalTime"] = removal_time

        self.removeMaterialThread = G3CTCtlCore.RemoveMaterialThread(self, cmd_dict, duration_dict)
        self.mixerLock.acquire(True)
        self.setRemoveMaterialState("initializing")
        self.setActualMixerState("waiting")
        self.mixerLock.release()
        self.removeMaterialThread.start()

    ##########################################################################

    def setActualMixerState(self, state):
        self.actualMixerState = state

    def getActualMixerState(self):
        return self.actualMixerState

    def getCommandedMixerState(self):
        return self.commandedMixerState

    def doStartMixer(self):
        com_port = self.settings.getComPort()
        controller = self.settings.getMixerController()
        forward_switch = self.settings.getMixerForwardSwitch()
        reverse_switch = self.settings.getMixerReverseSwitch()
        dead_time = self.settings.getMixerDeadTime()
        cmd = "ctrl-comm " + str(com_port) + " set ctl " + str(controller) + " motor " + str(
            reverse_switch) + " dir 1 speed 0"
        cmd_ret = self.sendCommand(cmd)
        if cmd_ret != "ack":
            print cmd_ret
            self.actualMixerState = "error"
            return
        time.sleep(dead_time)
        cmd = "ctrl-comm " + str(com_port) + " set ctl " + str(controller) + " motor " + str(
            forward_switch) + " dir 1 speed 255"
        cmd_ret = self.sendCommand(cmd)
        if cmd_ret != "ack":
            print cmd_ret
            self.actualMixerState = "error"
            return
        self.actualMixerState = "running"

    def doStopMixer(self):
        com_port = self.settings.getComPort()
        controller = self.settings.getMixerController()
        forward_switch = self.settings.getMixerForwardSwitch()
        reverse_switch = self.settings.getMixerReverseSwitch()
        cmd = "ctrl-comm " + str(com_port) + " set ctl " + str(controller) + " motor " + str(
            reverse_switch) + " dir 1 speed 0"
        cmd_ret = self.sendCommand(cmd)
        if cmd_ret != "ack":
            print cmd_ret
            self.actualMixerState = "error"
            return
        cmd = "ctrl-comm " + str(com_port) + " set ctl " + str(controller) + " motor " + str(
            forward_switch) + " dir 1 speed 0"
        cmd_ret = self.sendCommand(cmd)
        if cmd_ret != "ack":
            print cmd_ret
            self.actualMixerState = "error"
            return
        self.actualMixerState = "stopped"

    def startStopMixer(self):
        self.mixerLock.acquire(True)
        if self.commandedMixerState == "stop":
            self.commandedMixerState = "run"
            # attempt to start mixer
            if self.removeMaterialState != "idle":
                self.actualMixerState = "waiting"
            else:
                self.doStartMixer()
        else:
            self.commandedMixerState = "stop"
            # attempt to stop mixer
            if self.removeMaterialState != "idle":
                self.actualMixerState = "waiting"
            else:
                self.doStopMixer()
        self.mixerLock.release()

    ##########################################################################

    class DischargeValveThread(threading.Thread):
        def __init__(self, core, cmd_dict, duration_dict, direction):
            threading.Thread.__init__(self)
            self.core = core
            self.cmdDict = cmd_dict
            self.durationDict = duration_dict
            self.direction = direction

        def run(self):
            self.core.dischargeValveControlLock.acquire(True)
            if self.direction == "open":
                self.core.logfile.write(str(datetime.datetime.now()) + " opening discharge valve\n")
                self.core.setDischargeValveControlState("opening")
                cmd_ret = self.core.sendCommand(self.cmdDict["openCmd"])
                if cmd_ret != "ack":
                    print cmd_ret
                    self.core.setDischargeValveControlState("error")
                    self.core.dischargeValveControlLock.release()
                    return
                time.sleep(self.durationDict["open"])
                self.core.sendCommand(self.cmdDict["stopCmd"])
                if cmd_ret != "ack":
                    print cmd_ret
                    self.core.setDischargeValveControlState("error")
                    self.core.dischargeValveControlLock.release()
                    return
                self.core.setDischargeValveControlState("opened")
                self.core.logfile.write(str(datetime.datetime.now()) + " opened discharge valve\n")
            else:
                self.core.logfile.write(str(datetime.datetime.now()) + " closing discharge valve\n")
                self.core.setDischargeValveControlState("closing")
                cmd_ret = self.core.sendCommand(self.cmdDict["closeCmd"])
                if cmd_ret != "ack":
                    print cmd_ret
                    self.core.setDischargeValveControlState("error")
                    self.core.dischargeValveControlLock.release()
                    return
                time.sleep(self.durationDict["close"])
                cmd_ret = self.core.sendCommand(self.cmdDict["stopCmd"])
                if cmd_ret != "ack":
                    print cmd_ret
                    self.core.setDischargeValveControlState("error")
                    self.core.dischargeValveControlLock.release()
                    return
                self.core.setDischargeValveControlState("closed")
                self.core.logfile.write(str(datetime.datetime.now()) + " closed discharge valve\n")

            self.core.dischargeValveControlLock.release()

    def setDischargeValveControlState(self, state):
        self.actualDischargeValveControlState = state

    def getCommandedDischargeValveControlState(self):
        return self.commandedDischargeValveControlState

    def getDischargeValveControlState(self):
        return self.actualDischargeValveControlState

    def doDischargeValveControl(self, direction):
        com_port = self.settings.getComPort()
        controller = self.settings.getDischargeValveController()
        motor = self.settings.getDischargeValvelMotorNumber()
        open_direction = self.settings.getDischargeValveMotorOpenDirection()
        open_duration = self.settings.getDischargeValveMotorOpenDuration()
        close_direction = self.settings.getDischargeValveMotorCloseDirection()
        close_duration = self.settings.getDischargeValveMotorCloseDuration()
        print controller, motor, open_direction, open_duration, close_direction, close_duration
        cmd_dict = collections.OrderedDict()
        duration_dict = collections.OrderedDict()

        cmd_dict["openCmd"] = "ctrl-comm " + str(com_port) + " set ctl " + str(controller) + " motor " + str(
            motor) + " dir " + str(open_direction) + " speed 255"
        cmd_dict["closeCmd"] = "ctrl-comm " + str(com_port) + " set ctl " + str(controller) + " motor " + str(
            motor) + " dir " + str(close_direction) + " speed 255"
        cmd_dict["stopCmd"] = "ctrl-comm " + str(com_port) + " set ctl " + str(controller) + " motor " + str(
            motor) + " off"

        duration_dict["open"] = open_duration
        duration_dict["close"] = close_duration

        self.dischargeValveThread = G3CTCtlCore.DischargeValveThread(self, cmd_dict, duration_dict, direction)
        self.dischargeValveThread.start()

    def dischargeValveControl(self):
        self.dischargeValveControlLock.acquire(True)
        if self.commandedDischargeValveControlState == "open":
            self.commandedDischargeValveControlState = "close"
            self.doDischargeValveControl("close")
        else:
            self.commandedDischargeValveControlState = "open"
            self.doDischargeValveControl("open")
        self.dischargeValveControlLock.release()

    ##########################################################################

    def emergencyStop(self):
        # return
        ret_str = ""
        self.interfaceLock.acquire(True)
        com_port = self.settings.getComPort()
        controller = self.settings.getWaterDoserController()
        for i in xrange(0, 7):
            cmd = "ctrl-comm " + str(com_port) + " set ctl " + str(controller) + " switch " + str(i) + " off"
            print cmd
            args = cmd.split(" ")
            try:
                ret_str = subprocess.check_output(args)
            except subprocess.CalledProcessError:
                ret_str = "FAILURE"
        controller = self.settings.getMaterialDoserController()
        for i in xrange(0, 7):
            cmd = "ctrl-comm " + str(com_port) + " set ctl " + str(controller) + " switch " + str(i) + " off"
            args = cmd.split(" ")
            print cmd
            try:
                ret_str = subprocess.check_output(args)
            except subprocess.CalledProcessError:
                ret_str = "FAILURE"
        controller = self.settings.getMaterialBunkerController()
        for i in xrange(0, 7):
            cmd = "ctrl-comm " + str(com_port) + " set ctl " + str(controller) + " switch " + str(i) + " off"
            args = cmd.split(" ")
            print cmd
            try:
                ret_str = subprocess.check_output(args)
            except subprocess.CalledProcessError:
                ret_str = "FAILURE"
        controller = self.settings.getMixerController()
        for i in xrange(0, 7):
            cmd = "ctrl-comm " + str(com_port) + " set ctl " + str(controller) + " switch " + str(i) + " off"
            args = cmd.split(" ")
            print cmd
            try:
                ret_str = subprocess.check_output(args)
            except subprocess.CalledProcessError:
                ret_str = "FAILURE"

        if ret_str == "FAILURE":
            print "Failed to effect emergency stop"
