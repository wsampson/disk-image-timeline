import os
import subprocess
import sys

root = '.'

dirList=[]
flsList=[]
missedNumber = 0

timeline = open('timeline-final.csv', 'a')

# get top level directories in root
for directory in os.listdir(root):
    if os.path.isdir(os.path.join(root, directory)):
        dirList.append(directory)

# produce fls output file for each image
for d in dirList:
    
    # get a listing of files in each directory
    files = [f for f in os.listdir(d) if os.path.isfile(os.path.join(d,f))]
    for item in files:
        
        # run fls on ewf image and output txt file
        #if item.lower().endswith(('.e01')):
        #    try:
        #        fstype = subprocess.check_output(['fsstat', '-t', d + '/' + item])     
        #        out = subprocess.check_output(['fls', '-m', '.', '-i', 'ewf', d + '/' + item])
        #        flsList.append((d, fstype))
        #        f = open(d + '.txt', 'w')
        #        f.write(out)
        #        f.close()
        #    except:
        #        e = sys.exc_info()[0]
        #        print item + ' disk image could not be read and was skipped.'

        # run fls on raw image and output txt file
        if item.lower().endswith(('.img', '.dd')):
            try: 
                fstype = subprocess.check_output(['fsstat', '-t', d + '/' + item])
                out = subprocess.check_output(['fls', '-m', '.', '-i', 'raw', d + '/' + item])
                flsList.append((d, fstype))
                f = open(d + '.txt', 'w')
                f.write(out)
                f.close()
            except subprocess.CalledProcessError as e:
                if e.returncode != 0:               
                        try:
                                makeDir = subprocess.call(['mkdir', '/home/bcadmin/Desktop/tmp/' + d]) 
                                makeFsDir = subprocess.call(['mkdir', '/home/bcadmin/Desktop/fs/' + d])                                
                                hfs_extract = subprocess.check_output(['./unhfs-x.sh', '-v', '-resforks', 'APPLEDOUBLE', '-o', '/home/bcadmin/Desktop/tmp/' + d, d + '/' + item])
                                makeFsReadOnly = subprocess.call(['bindfs', '-n', '-r', '/home/bcadmin/Desktop/tmp/' + d, '/home/bcadmin/Desktop/fs/' + d])
                                #makeFilesReadOnly = subprocess.call(['sudo', 'chmod', '-R', '0444', '/home/bcadmin/Desktop/tmp/' + d])
                                #makeDirReadOnly = subprocess.call(['sudo', 'chmod', '-R', '0544', '/home/bcadmin/Desktop/tmp/' + d])

                                out = subprocess.check_output(['mac-robber', '/home/bcadmin/Desktop/fs/' + d])
                                unmount = subprocess.call(['fusermount', '-u', '/home/bcadmin/Desktop/fs/' + d])
                                fstype = 'hfs\n'
                        except subprocess.CalledProcessError as e:
                                if e.returncode != 0:
                                        missedNumber += 1
                                        fstype = 'skipped\n'
                                        out = 'skipped'
                        flsList.append((d, fstype))
                        f = open(d + '.txt', 'w')
                        f.write(out)
                        f.close() 

print missedNumber
print len(dirList)

# put all txt files in spreadsheet
for d, fstype in flsList:

    out = subprocess.check_output(['mactime', '-b', d + '.txt', '-d', '-y'])
    
    # remove first line (a header row) from the out string
    sansfirstline = '\n'.join(out.split('\n')[1:])
    
    lines = sansfirstline.splitlines()
    for line in lines:
        line = line + ',' + d + ',' + fstype
        timeline.write(line)
