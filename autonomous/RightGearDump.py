from robotpy_ext.autonomous import StatefulAutonomous, timed_state, state
import wpilib

class DriveForward(StatefulAutonomous):

    MODE_NAME = 'Right Gear Dump'

    """
        TODO:
            - Have it floor it to the other side
            - Adjust angle and distance
    """
    def initialize(self):

        self.drive_speed = -0.5

    @timed_state(duration=0.5, next_state='drive_forward', first=True)
    def drive_wait(self):

        self.drive.mecanumMove(0,0,0,0)
        self.drive.setAutoForwardSetpoint(92)
        self.drive.updateSetpoint("teleop")
        self.drive.setPIDenable(True)

    @timed_state(duration=1.75, next_state='startPID')
    def drive_forward(self):

        if self.drive.isAutoForwardOnTarget():
            self.drive.mecanumMove(0,0,0,0)
            self.drive.disableAutoForward()
            self.next_state("startPID")
        else:
            self.drive.mecanumMove(0,0,0,0)

    @state()
    def startPID(self):
        self.drive.updateSetpoint("auto", 60)
        self.drive.setPIDenable(False)
        self.drive.mecanumMove(0,0,0,0)
        self.next_state('stopPID')

    @timed_state(duration=1.5, next_state="stop")
    def stopPID(self):
        if self.drive.enableAutoTurn():
            self.drive.setPIDenable(True)
            self.drive.updateSetpoint("teleop")
            self.next_state('goForward')

        self.drive.mecanumMove(0,0,0,0)

    @timed_state(duration=.3, next_state='findPeg')
    def goForward(self):
        self.drive.mecanumMove(0,0,0,0)

    @timed_state(duration=3, next_state="stop")
    def findPeg(self):
        self.drive.engageVisionX(True, self.alignGear.getAlignNumber())

        if self.drive.visionOnTarget():
            self.drive.disableVision()
            self.next_state('goToPeg')
        self.drive.mecanumMove(0,0,0,0)
    @timed_state(duration=2, next_state="openUp")
    def goToPeg(self):
        if self.ultrasonic.getRangeInches()<9:
            self.next_state("openUp")
        else:
            self.drive.disableVision()
            self.drive.disableAutoForward() #This is likly the problem for not moving forward
            self.drive.disableAutoTurn()
            self.drive.mecanumMove(0,-1,0,.27)
        print (self.ultrasonic.getRangeInches())
    @timed_state(duration=.75, next_state='goBackInit')
    def openUp(self):
        self.gearPiston.set(True)

    @state()
    def goBackInit(self):
        self.drive.resetEncoder()
        self.drive.setAutoForwardSetpoint(100) #Guessing
        self.drive.updateSetpoint("teleop") #Maybe? Could use Teleop instead
        self.next_state("goBack")

    @timed_state(duration=3, next_state="stop")
    def goBack(self):
        if self.drive.isAutoForwardOnTarget():
            self.drive.mecanumMove(0,0,0,0)
            self.drive.disableAutoForward()
            self.next_state("strafeOver")
        else:
            self.drive.mecanumMove(0,0,0,0)

    @timed_state(duration=.75, next_state="dropFuel")
    def strafeOver(self):
        self.drive.mecanumMove(1,0,0,.3)

    @timed_state(duration=1, next_state="stop")
    def dropFuel(self):
        self.servo.set(1)

    @state()
    def stop(self):
        self.drive.mecanumMove(0,0,0,0)
