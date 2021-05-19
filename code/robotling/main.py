# ----------------------------------------------------------------------------
# main.py
# Main program; is automatically executed after reboot.
#
# For decription, see `hexbug.py`
#
# The MIT License (MIT)
# Copyright (c) 2019 Thomas Euler
# 2018-12-22, reorganised into a module with the class `Hexbug` and a simpler
#             main program file (`main.py`). All hardware-related settings
#             moved to separate file (`hexbug_config-py`)
# 2018-12-28, adapted to using the new `spin_ms()` function to keep the
#             robotling board updated; does not require a Timer anymore.
#             For details, see `robotling.py`.
# 2019-04-07, added new "behaviour" (take a nap)
# 2019-07-13, added new "behaviour" (find light)
#             `hexbug_config.py` reorganised and cleaned up
# 2019-07-24, added "memory" to turn direction (experimental)
# 2019-08-19, in case of an uncaught exception, it tries to send a last
#             MQTT message containing the traceback to the broker
# 2021-04-29, Some refactoring; configuration parameters now clearly marked
#             as such (`cfg.xxx`)
#
# ----------------------------------------------------------------------------
from hexbug import *

# ----------------------------------------------------------------------------
def main():
  # Setup the robot's spin function
  r.spin_ms(period_ms=cfg.TM_PERIOD, callback=r.housekeeper)

  # Angle the IR sensor towards floor in front
  r.ServoRangingSensor.angle = cfg.SCAN_DIST_SERVO
  r.spin_ms(100)

  # Loop ...
  print("Entering loop ...")
  try:
    try:
      lastTurnDir = 0
      round = 0

      while True:
        try:
          r.onLoopStart()

          if r.onHold:
            # Some problem was detected (e.g. robot tilted etc.), skip all
            # the following code
            lastTurnDir = 0
            continue
          r._t.spin()


        finally:
          # Make sure the robotling board get updated at least once per loop
          r.spin_ms()
          round += 1

    except KeyboardInterrupt:
      print("Loop stopped.")

  finally:
    # Make sure that robot is powered down
    r.ServoRangingSensor.off()
    r.powerDown()
    r.printReport()

# ----------------------------------------------------------------------------
# Create instance of HexBug, derived from the Robotling class
r = HexBug(cfg.MORE_DEVICES)

# Call main
if __name__ == "__main__":
  try:
    main()
  except Exception as e:
    # Create an in-memory file-like string object (`sIO`) to accept the
    # exception's traceback (`sys.print_exception` requires a file-like
    # object). This traceback string is then converted into a dictionary
    # to be sent as an MQTT message (if telemetry is activate)
    if cfg.SEND_TELEMETRY and r._t._isReady:
      import sys, uio
      sIO = uio.StringIO()
      sys.print_exception(e, sIO)
      r._t.publishDict(KEY_RAW, {KEY_DEBUG: str(sIO.getvalue())})
    # Re-raise the exception such that it becomes also visible in the REPL
    raise e

# ----------------------------------------------------------------------------
