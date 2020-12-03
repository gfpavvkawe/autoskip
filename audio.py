import struct, wave


def measure_sample(sample, numch, endianess=0): # 0 = little endian, 1 = big endian
    sum = 0
    num_frame = len(sample) // 2 // numch
    sample = struct.unpack(('<' if endianess == 0 else '>') + str(len(sample)//2) + 'h', sample)
    for i in range(num_frame):
        sum_frame = 0
        for ch in range(numch):
            sum_frame += sample[numch * i + ch]
        sum += abs(sum_frame / numch)
    return sum/num_frame


def gen_seg(wav, r, threshold):
    ar = wav.getframerate()
    ac = wav.getnchannels()
    aframe = 0
    vframe = 1
    seg_list = [[None,None]]

    while True:
        nframes = int((vframe + 1) / (r[0]/r[1]) * ar) - aframe
        sample = wav.readframes(nframes)
        if (not sample):
            if (seg_list[-1][-1] == None): #segment unfinished
                seg_list[-1][-1] = vframe
            break
        vol = measure_sample(sample, ac, 0)
        if (seg_list[-1][-1] != None and vol >= threshold):
            seg_list.append([int(vframe), None])
        elif (seg_list[-1][-1] == None and vol < threshold):
            seg_list[-1][-1] = int(vframe)

        aframe += nframes
        vframe += 1
    return seg_list[1:]


def add_margin(seg_list, r, msec):
    m = int(r[0] / r[1] * msec / 1000)
    if (not m):
        return seg_list
    for i in range(len(seg_list)): # add margin except first and last segment.
        if (i != 0):
            seg_list[i][0] -= m
        if (i != len(seg_list) - 1):
            seg_list[i][1] += m
#    for i in range(len(seg_list)): # merge overlapping segments.
    for i in range(len(seg_list)-2, -1, -1):
        if ((i < len(seg_list) - 1) and (seg_list[i][1] >= seg_list[i+1][0])):
            seg_list[i][1] = seg_list[i+1][1]
            seg_list.pop(i+1)
    return seg_list
