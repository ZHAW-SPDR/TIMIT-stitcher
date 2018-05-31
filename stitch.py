import os
import shutil
import subprocess
from pydub import AudioSegment


class Stitchable(object):
        def __init__(self, filename, audio, length):
            self.filename = filename
            self.audio = audio
            self.length = length


audiolist = []
data = []
IN = './in/'
OUT = './out/'
OUTNAME = 'TIMIT_DUMMY-01'
silence_3s = AudioSegment.silent(duration=3000)
#clean up
shutil.rmtree(OUT)
#run
os.mkdir(OUT)
os.mkdir(OUT+''+OUTNAME)
print('Let\'s start stitching our own dataset together!')
for path, dirs, files in os.walk(IN):
    for filename in files:
        if filename.endswith('WAV'):
            f = os.path.join(path, filename)
            audiolist.append(f)

data.append(Stitchable('SILENCE', silence_3s, len(silence_3s))) 
for item in audiolist:
    audio = AudioSegment.from_file(item, format='wav')
    length = len(audio)
    name = (item.rsplit('/')[2]).rsplit('.')[0]
    data.append(Stitchable(name, audio, length))
    data.append(Stitchable('SILENCE', silence_3s, len(silence_3s)))

outfile = AudioSegment.empty()
duration = 0

with open(OUT+''+OUTNAME+'/'+OUTNAME+'.txt', 'w') as tf:
    for elem in data:
        start = duration

        outfile += elem.audio
        duration += elem.length

        end = duration

        speaker = elem.filename.split('_')[0]
        tf.write("%.3f %.3f %s\n"  % (start, end, speaker))

exporthandle = OUTNAME+'_01.wav'
outfile.export(OUT+''+exporthandle, format="wav")

with open(OUT+''+OUTNAME+'.uem', 'w') as tf:
    tf.write("%s %d %.3f %.3f\n" % (OUTNAME, 1, 0, len(outfile)))

sphexporthandle = exporthandle.replace('wav', 'sph')
bashCommand = ['sox', '-t', 'wav', OUT+''+exporthandle, '-r', '16000', '-t', 'sph', OUT+''+OUTNAME+'/'+sphexporthandle]
process = subprocess.Popen(bashCommand, stdout=subprocess.PIPE)
output, error = process.communicate()

if error is not None:
    raise Exception("An error occured during conversion (%s): %s" % (output, error))

with open(OUT+''+OUTNAME+'.audioList.txt', 'w') as tf:
    fullpath = './audio/eval09/english/confmtg/' + OUTNAME + '/' + sphexporthandle
    tf.write("%s %s\n" % (OUTNAME, fullpath))

os.remove(OUT+''+exporthandle)
print('Done stitching. Check the %s folder for your dataset %s!' % (OUT, OUTNAME))