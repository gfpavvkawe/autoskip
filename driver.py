import sys, io, os, tempfile
import wave, ffmpeg
import audio, drop

def autoskip(src, dst, threshold, margin):
    vid_in = ffmpeg.input(src)
    out, _ = (vid_in.output('-', format='wav').overwrite_output()
    .run(quiet=True))
    audio_data = io.BytesIO(out)
    process1 = (vid_in.output('-', format='yuv4mpegpipe', pix_fmt='yuv420p')
            .run_async(pipe_stdout=True))
    header = process1.stdout.readline()

    rate = [30000,1001] # Assume 30fps drop frame if fps not found in header.
    for s in header.decode().strip('\n').split(' ')[1:]:
        if (s[0] == 'W'):
            width = int(s[1:])
        if (s[0] == 'H'):
            height = int(s[1:])
        if (s[0] == 'F'):
            rate[0] = int(s[1:].split(':')[0])
            rate[1] = int(s[1:].split(':')[1])

    print('generating segment...', file=sys.stderr)
    w1 = wave.open(audio_data, 'rb')
    seg_list = audio.gen_seg(w1, rate, threshold)
    audio.add_margin(seg_list, rate, margin)
    w1.rewind()

    print('writing audio to temporary file...', file=sys.stderr)
    audiotmp = tempfile.NamedTemporaryFile(delete=False)
    w2 = wave.open(audiotmp, 'wb')
    drop.adrop(w1, w2, seg_list, rate)
    w2.close()
    audiotmp.flush()
    w1.close()
    audio_data.close()

    out_video = ffmpeg.input('-', format='yuv4mpegpipe')
    out_audio = ffmpeg.input(audiotmp.name, format='wav')
    process2 = (ffmpeg.output(out_video, out_audio, dst)
            .overwrite_output()
            .run_async(pipe_stdin=True))
    process2.stdin.write(header)

    print('processing video...', file=sys.stderr)
    framesize = int(width * height * 3 / 2)
    drop.vdrop(process1.stdout, process2.stdin, framesize, seg_list)

    process1.stdout.read()
    process1.stdout.close()
    process2.stdin.close()
    process1.wait()
    process2.wait()

    os.unlink(audiotmp.name)

if (__name__ == '__main__'):
    src = input('src:')
    dst = input('dst:')
    threshold = int(input('threshold:'))
    margin = int(input('margin:'))
    autoskip(src, dst, threshold, margin)
