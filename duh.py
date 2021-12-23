import sys
import wave

filestr = sys.argv[1] # fixme catch exception, "with"
wavfile = wave.open(filestr, 'r')

print("params", wavfile.getparams())
five = wavfile.readframes(5)
fivemore = wavfile.readframes(5)
print(five)
print(five.hex())
print(fivemore.hex())
print(type(five))
print ("seconds", wavfile.getnframes() / wavfile.getframerate())
