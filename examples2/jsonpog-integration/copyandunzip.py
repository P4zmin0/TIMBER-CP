import os,sys

rundir = os.getcwd()

pogs = ['BTV','EGM','JME','LUM','MUO']

eras = ['2022_Summer22','2022_Summer22EE','2023_Summer23','2023_Summer23BPix']

for pog in pogs:
    for era in eras:
        if not os.path.exists('POG/'+pog+'/'+era):
            os.system('mkdir POG/'+pog+'/'+era)
        os.system('cp /cvmfs/cms.cern.ch/rsync/cms-nanoAOD/jsonpog-integration/POG/'+pog+'/'+era+'/* POG/'+pog+'/'+era+'/')

        zips = [f for f in os.listdir('POG/'+pog+'/'+era)]
        print('Found these files: '+str(zips))
        
        os.chdir('POG/'+pog+'/'+era)
        for zip in zips:
            print('Unzipping POG/'+pog+'/'+era+'/'+zip)
            os.system('gunzip '+zip)
        os.chdir(rundir)
            
