# -*- coding: utf-8 -*-
def say_with_animation(tts_service, animation_service, text, animation_name):
    tts_task = tts_service.say(text, _async=True)
    anim_task = animation_service.run(animation_name, _async=True)
    tts_task.wait()
    anim_task.wait()
