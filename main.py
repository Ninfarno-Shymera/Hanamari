import sys
from PyQt6.QtWidgets import QApplication
from hanamari.body.sprite import Sprite
from hanamari.body.inbox import Inbox
from hanamari.body.animation import Animator
from hanamari.body.screen import Screen
from hanamari.body.movement import Movement, Physic
from hanamari.brain.driver import Driver

MODEL_RUTE = "resources/models/espeon_mint"
ICON_RUTE = "resources/icons/inbox.png"
SIZE = 128
POSITION = "center"

app = QApplication(sys.argv)
app.setQuitOnLastWindowClosed(False) #Impide que se cierre la app al cerrar la ventana principal

# Sprites
sprite = Sprite()

# Screen
screen = Screen()

# Animations
animator = Animator(MODEL_RUTE)
scale = SIZE / animator.model["size"]
animator.configure(scale=scale, ratio=sprite.devicePixelRatioF())

physics = Physic(animator.model.get("physics", {}), SIZE)
movement = Movement(screen, scale, physics)
driver = Driver(MODEL_RUTE)

animator.changedFrame.connect(sprite.showFotogram)
animator.changedVelocity.connect(movement.establishVel)
animator.endlessFrame.connect(driver.endingAnimation)

# Movement
movement.changedPosition.connect(sprite.place)
movement.changedDirection.connect(animator.lookAt)
movement.lostAnimation.connect(driver.force)

# Sprite code ending
sprite.startDragged.connect(movement.toGrab)
sprite.moveDragged.connect(movement.toDrag)
sprite.endDragged.connect(movement.toLetGo)

# Driver
driver.changeAnimation.connect(animator.play)
driver.look.connect(movement.lookAt)

movement.place(screen.xInitial(POSITION))
sprite.show()
driver.start()

# Inbox
inbox = Inbox(ICON_RUTE)
def alternate():
    if sprite.isVisible():
        sprite.hide()
        animator.stop()
        movement.stop()
        driver.stop()
    else:
        sprite.show()
        animator.resume()
        driver.start()
        movement.resume()
        
inbox.switchOrder.connect(alternate)
inbox.exitOrder.connect(app.quit)

sys.exit(app.exec())