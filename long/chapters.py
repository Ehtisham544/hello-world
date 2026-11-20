import render_long as R
print('0:00 Intro')
for si,s in enumerate(R.SLIDES):
    if s['kind'] in ('chapter','outro'):
        t=int(R.SLIDE_START[si]); print(f"{t//60}:{t%60:02d} "+(s['title'] if s['kind']=='chapter' else 'Summary'))
