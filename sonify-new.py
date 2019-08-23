import os
from sys import argv
import numpy as np
import skimage
from skimage import io
from skimage.color import rgb2gray
from skimage import measure
import matplotlib.pyplot as plt
from skimage.morphology import skeletonize
from collections import Counter
import pretty_midi

script, path = argv

# image 1007kunmondriaan.jpg
# https://www.nrc.nl/nieuws/2014/07/10/zeeuws-nazomerlicht-betoverde-mondriaan-1397427-a1152239
# https://www.geeksforgeeks.org/getting-started-scikit-image-image-processing-python/
# https://scikit-image.org/
# http://scikit-image.org/docs/stable/api/skimage.measure.html#skimage.measure.find_contours
# http://scikit-image.org/docs/dev/auto_examples/color_exposure/plot_rgb_to_gray.html
# http://scikit-image.org/docs/stable/api/skimage.morphology.html#skimage.morphology.skeletonize
# http://scikit-image.org/docs/stable/auto_examples/edges/plot_skeleton.html#sphx-glr-auto-examples-edges-plot-skeleton-py
# http://scikit-image.org/docs/stable/api/skimage.util.html#skimage.util.invert
# http://craffel.github.io/pretty-midi/#module-pretty_midi

# rows x cols = 1006 x 1280
#mondriaan = 'mondriaan.jpg'
pic = argv[1]
# rows x cols = 104, 101
#mondriaan = 'mondriaan-test.png'

# path = '/Users/reinierdevalk/Downloads/'
# path = 'C:/Users/Reinier/Desktop/sonification/sonification/'
#path = argv[1]
path = ''

file = os.path.join(path, pic)


mon_col = io.imread(file)
mon = rgb2gray(mon_col)

dims = mon.shape
print(dims)
y_pix = dims[0]
x_pix = dims[1]

# print len(mon_col[0]) # first row in first 1006 x 1280 panel
# print mon_col[0][0] # RGB values for first element in first row in RGB panels
# print len(mon[0]) # first row in only (grayscale) 1006 x 1280 panel
# print mon[0][0] # RGB value for first element in first row in gray panel

#io.imshow(mon)
#io.show()

# 72 pitches from 24 (C1) to 96 (C7)
# 64 durations from 1 (one 16th) to 64 (four whole notes)

contours = measure.find_contours(mon, 0.2)
print("len contours    = " + str(len(contours)))

# exclude really short and really long contour vectors
new_contours = []
for item in contours:
	print(len(item))
	if len(item) > 50 and len(item) < 1000:
		new_contours.append(item)

print("len new_contours    = " + str(len(new_contours)))

#new_contours = contours

test = contours[1]
#test = contours[5]

# https://stackoverflow.com/questions/1518522/find-the-most-common-element-in-a-list
def most_common(lst):
    data = Counter(lst)
    return data.most_common(1)[0][0]

notes = []
# each contour is an ndarray of shape (n, 2), consisting of n (row (pitch), column (onset)) coordinates along the contour.
for c in contours:
	# sort by column value (onset)
	sort = np.asarray(sorted(c, key=lambda x: x[1]))

	# get column 0 (pitches)
	pitches = sort[:,0]
	min_pitch = min(pitches)
	max_pitch = max(pitches)
	# get column 1 (onsets)
	durs = sort[:,1]
	min_dur = min(durs)
	max_dur = max(durs)
#	print len(sort)
#	skeleton = skeletonize(sort)
#	print skeleton


	dur = max_dur - min_dur
	delta_p = max_pitch - min_pitch
	# print 'dur = ' + str(dur)
	# print 'delta_p = ' + str(delta_p)
	# print 'min_pitch = ' + str(min_pitch)
	# print 'max_pitch = ' + str(max_pitch)
	# print 'min_dur = ' + str(min_dur)
	# print 'max_dur = ' + str(max_dur)
	# print 'delta_above = '
	pitches_rounded = [round(p) for p in pitches]
	most_common_pitch = most_common(pitches_rounded)

	# print pitches
	# print pitches_rounded
	# print most_common_pitch

	delta_p_upper = 0
	if min_pitch < most_common_pitch:
		delta_p_upper = most_common_pitch - min_pitch
	delta_p_lower = 0
	if max_pitch > most_common_pitch:
		delta_p_lower = max_pitch - most_common_pitch
	# print 'delta_p_upper = ' + str(delta_p_upper)
	# print 'delta_p_lower = ' + str(delta_p_lower)
	note = {'pitch': most_common_pitch, 'onset': min_dur, 'dur': dur, 'delta_p': delta_p, 'delta_p_upper': delta_p_upper, 'delta_p_lower': delta_p_lower}
	print(note)
	notes.append(note)

min_pitch = 1000
max_pitch = 0
min_dur = 1000
max_dur = 0
min_delta_p = 1000
max_delta_p = 0
min_onset = 1000
max_onset = 0
all_pitches = []
for item in notes:
	if not item['pitch'] in all_pitches:
		all_pitches.append(item['pitch'])
	if item['pitch'] < min_pitch:
		min_pitch = item['pitch']
	if item['pitch'] > max_pitch:
		max_pitch = item['pitch']
	if item['dur'] < min_dur:
		min_dur = item['dur']
	if item['dur'] > max_dur:
		max_dur = item['dur']
	if item['delta_p'] > max_delta_p:
		max_delta_p = item['delta_p']
	if item['delta_p'] < min_delta_p:
		min_delta_p = item['delta_p']
	if item['onset'] > max_onset:
		max_onset = item['onset']
	if item['onset'] < min_onset:
		min_onset = item['onset']

print('- - - - - - - - - - - - -')
print('max_pitch ' + str(max_pitch))
print('min_dur ' + str(min_dur))
print('max_dur ' + str(max_dur))
print('max_delta_p ' + str(max_delta_p))
print('min_delta_p ' + str(min_delta_p))
print('max_onset ' + str(max_onset))
print('min_onset ' + str(min_onset))
print('==============')
print(len(all_pitches))

print(len(notes))

for item in notes:
	# fit range of pitches (y_pix) into 72 (6 octaves) --> y_pix / factor = 72 --> y_pix = 72*f --> f = y_pix/72
	item['pitch'] = round(item['pitch'] / (y_pix/60.0))
	# lowest pitch is not 0 but 24
	item['pitch'] += 12
	print('+ + + + + + + + + +')
	print('pitch = ' + str(item['pitch']))

	# fit range of onsets/durations (x_pix); take four pixels as one 16th (1280 pixels = 20 bars)
	print('onset = ' + str(item['onset']))
	print('dur = ' + str(item['dur']))
	item['dur'] = round(item['dur'] /4.0)
	item['onset'] = round(item['onset'] /4.0)
	print('onset = ' + str(item['onset']))
	print('dur = ' + str(item['dur']))

	# fit range of velocities (max_delta_p) into 127 (MIDI velocity range))
#	item['delta_p'] = round(item['delta_p']) #/2.0)
	item['delta_p'] = round(item['delta_p'] / (max_delta_p/127.0))
	if item['delta_p'] < 50:
		item['delta_p'] = 50
	print('delta_p = ' + str(item['delta_p']))


# http://craffel.github.io/pretty-midi/
# Create a PrettyMIDI object
mon_son = pretty_midi.PrettyMIDI()
# Create an Instrument instance for a cello instrument
cello_program = pretty_midi.instrument_name_to_program('Cello')
cello = pretty_midi.Instrument(program=cello_program)
# Iterate over note names, which will be converted to note number later

print('- + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + -')

for item in notes:
#for note_name in ['C5', 'E5', 'G5']:
    # Retrieve the MIDI note number for this note name
#    note_number = pretty_midi.note_name_to_number(note_name)
    # Create a Note instance, starting at 0s and ending at .5s


#    note = pretty_midi.Note(velocity=int(item['delta_p']), pitch=int(item['pitch']), start=int((item['onset'])/10), end=int((item['onset']+item['dur'])/10))

    # 60 bpm = 60 Q/m = 1 Q/s = 4 16th/s
	onset_in_sec = item['onset'] / 4.0
	dur_in_sec = item['dur'] / 4.0
	offset_in_sec = onset_in_sec + dur_in_sec

	print('=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=')
	print('pitch    = ' + str(item['pitch']))
	print('velocity = ' + str(item['delta_p']))
	print('onset    = ' + str(onset_in_sec))
	print('dur      = ' + str(dur_in_sec))
	print('offset   = ' + str(offset_in_sec))

	note = pretty_midi.Note(velocity=int(item['delta_p']), pitch=int(item['pitch']), start=int(onset_in_sec), end=int(offset_in_sec))


#    note = pretty_midi.Note(
#        velocity=100, pitch=note_number, start=0, end=.5)

    # Add it to our cello instrument
	cello.notes.append(note)

# Add the cello instrument to the PrettyMIDI object
mon_son.instruments.append(cello)

# Write out the MIDI data
#mon_son.write(path + 'mondriaan-test-sonified.mid')
mon_son.write(path + pic[:pic.index('.')] + '-sonified.mid')


fig, ax = plt.subplots()
ax.imshow(mon, interpolation='nearest', cmap=plt.cm.gray)

for n, contour in enumerate(contours):
    ax.plot(contour[:, 1], contour[:, 0], linewidth=2)

ax.axis('image')
ax.set_xticks([])
ax.set_yticks([])
plt.show()