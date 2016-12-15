from src.LocalDbManager import LocalDbManager

ldm = LocalDbManager('/TCT/QCT MSM8953/B-MERCURY')
ldm.sync()
#ldm.test()



#(code, out, err) = Im.execute('im issues %s' % params)
#(code, out, err) = Im.execute('im viewissue --showRichContent %d' % 3412329)
#print ('code: %d' % code)
#print ('out: %s' % out)
#print ('err: %s' % err)

#with open('out.txt', 'w') as f:
#    f.write(out)

