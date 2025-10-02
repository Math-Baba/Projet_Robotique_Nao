# -*- coding: utf-8 -*-
import pygame
import sys
from time import sleep
from naoqi import ALProxy

# ---------- CONFIGURATION NAO ----------
NAO_IP = "11.0.0.147"
PORT = 9559

motion = ALProxy("ALMotion", NAO_IP, PORT)
posture = ALProxy("ALRobotPosture", NAO_IP, PORT)
animation_player = ALProxy("ALAnimationPlayer", NAO_IP, PORT)

posture.goToPosture("StandInit", 0.5)

# ---------- INITIALISATION MANETTE ----------
pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("Aucune manette détectée !")
    exit()

joystick = pygame.joystick.Joystick(0)
joystick.init()
print("Manette détectée :", joystick.get_name())

# ---------- BOUCLE PRINCIPALE ----------
try:
    while True:
        pygame.event.pump()  # met à jour l'état de la manette

        # Lecture axes du joystick gauche
        axe_x = joystick.get_axis(0)  # gauche/droite
        axe_y = joystick.get_axis(1)  # avant/arrière

        # Déplacements proportionnels au joystick
        if abs(axe_x) > 0.1 or abs(axe_y) > 0.1:
            motion.moveTo(-axe_y*0.2, 0, -axe_x*0.5)

        # Lecture boutons
        btn_triangle = joystick.get_button(3)  # Triangle
        btn_square   = joystick.get_button(0)  # Carré
        btn_cross    = joystick.get_button(1)  # X
        btn_circle   = joystick.get_button(2)  # Rond

        # Animations avec les boutons triangle, carré, rond et X
        if btn_triangle:
            animation_player.run("animations/Stand/Gestures/Hey_1")
        elif btn_square:
            animation_player.run("animations/Stand/Gestures/Hey_1")
        elif btn_cross:
            animation_player.run("animations/Stand/Gestures/Hey_1")
        elif btn_circle:
            animation_player.run("animations/Stand/Gestures/Hey_1")

        sleep(0.1)

except KeyboardInterrupt:
    print("Arrêt du contrôle manette")
    motion.stopMove()
    pygame.quit()
    sys.exit()
