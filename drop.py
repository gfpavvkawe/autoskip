def adrop(w1, w2, seg_list, r): # files must be closed by caller
    ac = w1.getnchannels()
    ar = w1.getframerate()
    numvframes = 0
    ivframe = 0 # Current input video frame position
    vframe = 0 # Current output video frame position
    aframe = 0 # Current output audio frame position
    nframes = 0 # Number of audio frames to copy

    for seg in seg_list:
        numvframes += seg[1] - seg[0]
    # Total count of audio frames. It must be calculated first because output stream might be unseekable.
    numaframes = int(numvframes * ar / (r[0] / r[1]))
    w2.setparams((ac, 2, ar, numaframes, 'NONE', 'not compressed'))

    for seg in seg_list:
        nframes = int((vframe + seg[1] - seg[0]) * ar / (r[0] / r[1]) - aframe)
        w1.setpos(int(seg[0] * ar / (r[0] / r[1])))
#        w1.readframes(int(seg[0] * ar / (r[0] / r[1]) - w1.tell()))
        w2.writeframesraw(w1.readframes(nframes))
        vframe += seg[1] - seg[0]
        aframe += nframes

def _read_y4m_frame(f, framesize):
    return f.readline() + f.read(framesize)

def vdrop(f1, f2, framesize, seg_list): # files must be closed by caller
    vframe = 0
    for seg in seg_list:
        for _ in range(seg[0] - vframe):
            _read_y4m_frame(f1, framesize)
            vframe += 1
        for _ in range(seg[1] - seg[0]):
            f2.write(_read_y4m_frame(f1, framesize))
            vframe += 1
