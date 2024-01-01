# -*- coding: utf-8 -*-
import string
import cStringIO
try:
    from PIL import Image
    Image.init()
except:
    pass

DEFAULT_QUALITY = 96


def IsImage(afname, amaxsizex=12000, amaxsizey=12000, aignoreext=0):
    if not aignoreext:
        aext1, aext2 = afname[-4:].lower(), afname[-5:].lower()
        if not aext1 in ['.jpg', '.gif', '.png', '.bmp'] and not aext2 in ['.jpeg', ]:
            return 0
    try:
        aimage = Image.open(afname)
        if aimage.size[0] > 0 and aimage.size[1] > 0 and aimage.size[0] < amaxsizex and aimage.size[1] < amaxsizey:
            _x = aimage.getpixel((aimage.size[0] - 1, aimage.size[1] - 1))
        else:
            return 0
    except:
        return 0
    return 1


def ResizeImageByConstraint(afnamein, afnameout, max_width, max_height, amaxsizekb=-1, acrop=0, alog=None):
    if alog:
        alog.Log('ResizeImageByConstraint ' + afnamein + ' ' + afnameout + ' ' + str(max_width) + ' ' + str(max_height) + ' ' + str(amaxsizekb) + ' ' + str(acrop))
    amaxsizekb = 1024 * amaxsizekb
    try:
        img = Image.open(afnamein).convert('RGB')
        if max_width > 0 and max_height == 0:
            src_width, src_height = img.size
            if alog:
                alog.Log('  #1 ' + str(src_width) + ' ' + str(src_height))
            drop_ratio = float(src_width) / float(max_width)
            img = img.resize((int(max_width), int(float(src_height / drop_ratio))), Image.ANTIALIAS)
        elif max_width == 0 and max_height > 0:
            src_width, src_height = img.size
            if alog:
                alog.Log('  #2 ' + str(src_width) + ' ' + str(src_height))
            drop_ratio = float(src_height) / float(max_height)
            img = img.resize((int(float(src_width / drop_ratio)), int(max_height)), Image.ANTIALIAS)
        elif max_width > 0 and max_height > 0 and not acrop:
            if alog:
                alog.Log('  #3 ')
            img.thumbnail((max_width, max_height), Image.ANTIALIAS)
        else:
            src_width, src_height = img.size
            if alog:
                alog.Log('  #4 ' + str(src_width) + ' ' + str(src_height))
            src_ratio = float(src_width) / float(src_height)
            dst_width, dst_height = max_width, max_height
            if dst_height != 0:
                dst_ratio = float(dst_width) / float(dst_height)
            else:
                dst_ratio = src_ratio
            if dst_ratio < src_ratio:
                crop_height = src_height
                crop_width = crop_height * dst_ratio
                x_offset = float(src_width - crop_width) / 2
                y_offset = 0
            else:
                crop_width = src_width
                crop_height = crop_width / dst_ratio
                x_offset = 0
                y_offset = float(src_height - crop_height) / 3
            if acrop:
                img = img.crop((int(x_offset), int(y_offset), int(x_offset) + int(crop_width), int(y_offset) + int(crop_height)))
            if dst_width > 0 and dst_height > 0:
                img = img.resize((int(dst_width), int(dst_height)), Image.ANTIALIAS)
        w = 1
        if alog:
            alog.Log('  OK')
    except:
        w = 0
        raise
    if w:
        aquality = DEFAULT_QUALITY
        adata = ''
        while aquality > 0:
            ff = cStringIO.StringIO()
            img.save(ff, 'JPEG', quality=aquality)
            adata = ff.getvalue()
            ff.close()
            if len(adata) <= amaxsizekb or amaxsizekb <= 0:
                break
            aquality = aquality - 10
    else:
        fin = open(afnamein, 'rb')
        adata = fin.read()
        fin.close()
    fout = open(afnameout, 'wb')
    fout.write(adata)
    fout.close()
    if alog:
        alog.Log('  Save OK')
