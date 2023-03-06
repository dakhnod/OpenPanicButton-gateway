# OpenPanicButton-gateway
ESP32 mesh gateway for the OpenPanicButton.

## Goal

This project aims to build an Open Source, wide range, mesh-based panic button.

Primarily this project is aimed at people who are at risk of falling without being able to get up 
or people in general who may be in need of a open-infrastructure panic button.

## Prerequisites

The code needs to be run on an ESP32 micropython board.
It is only tested on the base ESP32 wemos32 board.
As to how to install the MicroPython firmware refer to [this](https://micropython.org/download/esp32/) source.

## Installtion

To run the code, just run `ampy put main.py` to copy the code onto the board.
Then, just the [configuration](configuration) is needed.

## Configuration

### Key
Each network needs a key to differentiate it from other networks. This key consists of four bytes and is entered into the config.py. This key also needs to be present in the button's advertisement packet.

### Name
The name is broadcasted along with the button packet data, to that each nodes shows up in your BLE scanner.

### ID
The id is only needed for chain testing mode.

## Protocol

The protocol is fairly simple. The button, when pressed, needs to broadcast a packet with specific manufacturer specific data:

index start | index end | function
|-| - | ------------------------------
0 | 3 | key, as described in config.json
4 | 4 | target id (only relevant for test chain mode)
5 | 5 | mode

When a node receives a packet with a key matching it's own key, is retransmits that packet for 120 seconds, before going to sleep for 600 seconds.

## Modes

### Test chain mode (mode value 0xFF)

This is the only mode that has logic seperated from the hook. When the mode byte has the value 0, the node ignores packets whose id does not match it's own id.
When the node encounters a fitting packet, it retransmits that packet, but with the target id incremented by 1.
In result, if a single node in the chain is not working, the signal cannot traverse the whole chain.
The hook is called for this mode aswell. It is up to the hook to ignore this mode.

### Alarm mode (mode value 0x00)

This mode is just a proposal, it comes down to the hook how to handle it. My suggestion is to handle this mode like a regular alarm.

### Short alarm mode (mode value 0x01)

This mode is also hook-implementation-specific. I suggest to handle this mode like a short alarm, maybe for testing purposes.

### Silent alarm mode (mode value 0x02)

This mode is also hook-implementation-specific. My suggestion is to use this mode for testing purposes without ringing an audible alarm.

## Hook

### init

The hook consists of a file called `hook.py` along with the main.py.
Upon startup, the hooks `init` method is called without any arguments. Use this to enable GPIO etc.

### hook

When a matching key is encountered, the hooks `hook`-method is called with the [manufacturer specific data of the packet](protocol), aka the key, the id and the mode.
The implementation then decides how to handle the target id and mode.