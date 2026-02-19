# -*- coding: utf-8 -*-
import time

def pickup_bottle(motion, posture):
    """
    Ramasser une bouteille en restant debout.
    Bras rapprochés au maximum, coudes pliés, avant-bras tournés,
    doigts ouverts puis fermés pour tenir la bouteille.
    """
    try:
        speed = 0.3

        # 1️⃣ Bras vers le bas légèrement écartés
        motion.angleInterpolationWithSpeed(
            ["LShoulderPitch","RShoulderPitch"],
            [1.0, 1.0],
            speed
        )
        motion.angleInterpolationWithSpeed(
            ["LShoulderRoll","RShoulderRoll"],
            [0.1, -0.1],  # bras très rapprochés
            speed
        )

        # 2️⃣ Plier les coudes pour caliner la bouteille
        motion.angleInterpolationWithSpeed(
            ["LElbowRoll","RElbowRoll"],
            [-0.8, 0.8],
            speed
        )
        motion.angleInterpolationWithSpeed(
            ["LElbowYaw","RElbowYaw"],
            [-1.0, 1.0],
            speed
        )

        time.sleep(0.5)

        # 3️⃣ Ouvrir les mains
        motion.openHand("LHand")
        motion.openHand("RHand")
        time.sleep(0.3)

        # 4️⃣ Fermer les mains pour saisir la bouteille
        motion.closeHand("LHand")
        motion.closeHand("RHand")
        time.sleep(0.3)

        # 5️⃣ Lever légèrement les bras pour soulever la bouteille
        motion.angleInterpolationWithSpeed(
            ["LShoulderPitch","RShoulderPitch"],
            [0.2, 0.2],
            speed
        )
        motion.angleInterpolationWithSpeed(
            ["LShoulderRoll","RShoulderRoll"],
            [0.0, 0.0],
            speed
        )

        print("Bouteille calinée et tenue ! Position maintenue indéfiniment.")

    except Exception as e:
        print("Erreur pickup_bottle: {}".format(e))
