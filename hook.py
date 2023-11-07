import machine
import time 

relais = None

def init():
    # here you can setup GPIO's or similar
    global relais
    relais = machine.Pin(22)
    relais.init(relais.OUT)
    pass

def hook(data):
    target_id = data[4]
    mode = data[5]

    # This function gets called when the advertised key matched this nodes key
    # we are completely free to decide how we act upon different ids and modes
    # the following is just an example implementation

    def pulses(count, duration):
        for i in range(count):
            relais.on()
            time.sleep(duration)
            relais.off()
            time.sleep(duration)

    if mode == 0x02:
        # silent mode, no need to ring any alarm
        return
    if mode in [0xFF, 0x01]:
        # chain mode or silent mode
        # so maybe give out a short alarm
        pulses(2, 0.2)
        return

    for i in range(3):
        pulses(3, 0.3)
        pulses(3, 1)
        pulses(3, 0.3)

        time.sleep(5)

    # regular alarm mode
    # use GPIO to ring a regular alarm or something

