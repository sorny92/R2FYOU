import time
import math
from pysinewave import SineWave

# Create a sine wave, with a starting pitch of 12, and a pitch change speed of 10/second.
for i in range(1,20):
    freq = 1000*i
    print(freq)
    myPitch = (12 * math.log(freq / 261.626)) / math.log(2)
    sinewave = SineWave(pitch = myPitch, pitch_per_second = 1)


    # Turn the sine wave on.
    sinewave.play()

    # Sleep for 2 seconds, as the sinewave keeps playing.
    time.sleep(0.6)
    sinewave.stop()
