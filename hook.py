def init():
    # here you can setup GPIO's or similar
    pass

def hook(data):
    target_id = data[4]
    mode = data[5]

    # This function gets called when the advertised key matched this nodes key
    # we are completely free to decide how we act upon different ids and modes
    # the following is just an example implementation

    if mode == 0x02:
        # silent mode, no need to ring any alarm
        return
    if mode in [0xFF, 0x01]:
        # chain mode or silent mode
        # so maybe give out a short alarm
        return

    # regular alarm mode
    # use GPIO to ring a regular alarm or something

