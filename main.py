import bluetooth
import machine
import time
import json

try:
    import hook
    hook.init()
except ImportError:
    print('Hook module not found')

config = {}
try:
    with open('config.json', 'r') as config:
        config = json.load(config)
except OSError:
    print('config file not found')

print("starting")

COMPANY = b'\xff\xff'
KEY = bytes(config.get('key'))
ID = config.get('id', 0)
NAME = config.get('name', 'Node unnamed')
ADV_PERIOD = config.get('period_adv', 120)
ADV_PAUSE = config.get('period_pause', 600)

MODE_TEST_CHAIN = 0xFF
MODE_ALERT = 0x00
MODE_ALERT_SHORT = 0x01
MODE_TEST_SILENT = 0x02

REBOOT_PERIOD = 2 * 60 * 1000

WATCHDOG_TIMEOUT = REBOOT_PERIOD + ((ADV_PERIOD + ADV_PAUSE) * 1000)

# safety reboot, should never trigger
wdt = machine.WDT(timeout=WATCHDOG_TIMEOUT)
wdt.feed()

led = machine.Pin(2)
led.init(led.OUT)
led.off()

ble = bluetooth.BLE()

ble.active(True)

adv_timer = machine.Timer(0)
blink_timer = machine.Timer(1)
reboot_timer = machine.Timer(2)

led_on = False

blink = True

def reboot_timeout(timer):
    machine.reset()

reboot_timer.init(period=REBOOT_PERIOD, mode=reboot_timer.ONE_SHOT, callback=reboot_timeout)

def adv_data_decode(data):
    index = 0
    while index < len(data):
        length = data[index]
        pdu_type = data[index + 1]
        payload = data[index + 2 : index + 1 + length]
        index += length + 1
        yield((pdu_type, bytes(payload)))

def key_found(data):
    global blink

    data = bytearray(data)

    mode = data[5]
    if mode == MODE_TEST_CHAIN:
        print('test chain mode')
        id = data[4]
        if id != ID:
            print('id mismatch')
            return # not for us
        data[4] += 1
        global ADV_PERIOD, ADV_PAUSE
        ADV_PERIOD = 30
        ADV_PAUSE = 10

    led.on()
    reboot_timer.deinit() # going to reboot anyway

    blink = False

    ble.gap_scan(None)
    payload = bytearray()
    payload.append(len(NAME) + 1)
    payload.append(0x09)
    payload.extend(NAME.encode())

    payload.append(len(data) + 3)
    payload.append(0xff) # manufacturer specific data
    payload.extend(b'\xff\xff') # no company id

    payload.extend(data)

    ble.gap_advertise(100, payload)

    def pause_timeout(timer):
        print("pause timeout, rebooting")
        led.off()
        machine.reset()

    def led_timeout(timer):
        global led_on
        if led_on:
            led.off()
        else:
            led.on()
        led_on = not led_on

    def adv_timeout(timer):
        print("stopping advertisement")
        ble.gap_advertise(None)
        adv_timer.init(mode=adv_timer.ONE_SHOT, period=ADV_PAUSE*1000, callback=pause_timeout)
        blink_timer.init(period=100, callback=led_timeout)

    adv_timer.init(mode=adv_timer.ONE_SHOT, period=ADV_PERIOD*1000, callback=adv_timeout)

    try:
        hook.hook(data)
    except NameError:
        print('Hook not found')


def handle_irq(type, args):
    if type == 5:
        addr_type, addr, adv_type, rssi, adv_data = args
        if adv_data is None:
            return
        # print(f"scan result addr_type: {addr_type}, addr: {bytes(addr)}, adv_type: {adv_type}, rssi: {rssi}, adv_data: {bytes(adv_data)}")
        packets = list(adv_data_decode(adv_data))
        packets = dict(packets)
        try:
            data = packets[0xff]
        except KeyError:
            return
        company = data[0:2]
        if company != COMPANY:
            return
        data = data[2:]
        key = data[:4]
        if key != KEY:
            return
        print("found")
        key_found(data)

ble.irq(handle_irq)
ble.gap_scan(0, 1280000, 1000000, False)

while True:
    led.on()
    time.sleep(0.1)
    if not blink:
        break
    led.off()
    time.sleep(5)

time.sleep(999999) # wait for reboot
