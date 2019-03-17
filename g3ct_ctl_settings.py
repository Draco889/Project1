import json


class G3CTCtlSettings:
    def __init__(self, filename):
        with open(filename, "r") as read_file:
            self.data = json.load(read_file)

    def getComPort(self):
        return self.data["comPort"]

    def getLogFilename(self):
        return self.data["logFilename"]

    def getWaterDoserController(self):
        return self.data["waterDoser"]["controller"]

    def getWaterDoserMotorNumber(self):
        return self.data["waterDoser"]["motor"]["number"]

    def getWaterDoserMotorOpenDirection(self):
        return self.data["waterDoser"]["motor"]["openDirection"]

    def getWaterDoserMotorOpenDuration(self):
        return self.data["waterDoser"]["motor"]["openDuration"]

    def getWaterDoserMotorCloseDirection(self):
        return self.data["waterDoser"]["motor"]["closeDirection"]

    def getWaterDoserMotorCloseDuration(self):
        return self.data["waterDoser"]["motor"]["closeDuration"]

    def getMaterialDoserController(self):
        return self.data["materialDoser"]["controller"]

    def getMaterialDoserTopMotorNumber(self):
        return self.data["materialDoser"]["topMotor"]["number"]

    def getMaterialDoserTopMotorOpenDirection(self):
        return self.data["materialDoser"]["topMotor"]["openDirection"]

    def getMaterialDoserTopMotorOpenDuration(self):
        return self.data["materialDoser"]["topMotor"]["openDuration"]

    def getMaterialDoserTopMotorCloseDirection(self):
        return self.data["materialDoser"]["topMotor"]["closeDirection"]

    def getMaterialDoserTopMotorCloseDuration(self):
        return self.data["materialDoser"]["topMotor"]["closeDuration"]

    def getMaterialDoserBottomMotorNumber(self):
        return self.data["materialDoser"]["bottomMotor"]["number"]

    def getMaterialDoserBottomMotorOpenDirection(self):
        return self.data["materialDoser"]["bottomMotor"]["openDirection"]

    def getMaterialDoserBottomMotorOpenDuration(self):
        return self.data["materialDoser"]["bottomMotor"]["openDuration"]

    def getMaterialDoserBottomMotorCloseDirection(self):
        return self.data["materialDoser"]["bottomMotor"]["closeDirection"]

    def getMaterialDoserBottomMotorCloseDuration(self):
        return self.data["materialDoser"]["bottomMotor"]["closeDuration"]

    def getMaterialBunkerController(self):
        return self.data["materialBunker"]["controller"]

    def getMaterialBunkerMotorNumber(self):
        return self.data["materialBunker"]["motor"]["number"]

    def getMaterialBunkerMotorDirection(self):
        return self.data["materialBunker"]["motor"]["direction"]

    def getMaterialBunkerMotorDuration(self):
        return self.data["materialBunker"]["motor"]["duration"]

    def getDischargeValveController(self):
        return self.data["dischargeValve"]["controller"]

    def getDischargeValvelMotorNumber(self):
        return self.data["dischargeValve"]["motor"]["number"]

    def getDischargeValveMotorOpenDirection(self):
        return self.data["dischargeValve"]["motor"]["openDirection"]

    def getDischargeValveMotorOpenDuration(self):
        return self.data["dischargeValve"]["motor"]["openDuration"]

    def getDischargeValveMotorCloseDirection(self):
        return self.data["dischargeValve"]["motor"]["closeDirection"]

    def getDischargeValveMotorCloseDuration(self):
        return self.data["dischargeValve"]["motor"]["closeDuration"]

    def getMixerController(self):
        return self.data["mixer"]["controller"]

    def getMixerForwardSwitch(self):
        return self.data["mixer"]["forwardSwitch"]["number"]

    def getMixerReverseSwitch(self):
        return self.data["mixer"]["reverseSwitch"]["number"]

    def getMixerDeadTime(self):
        return self.data["mixer"]["deadTime"]

    def getMixerMaterialRemovalTime(self):
        return self.data["mixer"]["materialRemovalTime"]
