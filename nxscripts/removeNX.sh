#! /bin/bash

## script to remove NX

archiveDir=~/.NXarchive
downloadDir=~/.packages ;
if [ ! -d "$archiveDir" ]; then 
    mkdir $archiveDir ;
fi
if [ -d "$archiveDir/NX" ]; then 
    sudo rm -rf $archiveDir/NX ;
fi
sudo mv -f /usr/NX $archiveDir 
sudo userdel nx