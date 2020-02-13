# trqk-cover-song-detection

cover-song-detection code - Matlab (librosa) and python (django)


CoSoDe Code install on Linux/AWS

Shell commands

sudo apt-get install octave
sudo apt-get install liboctave-dev
sudo apt-get install mpg123
sudo apt-get install mp3info
sudo apt-get install python3
sudo apt-get install python3-pip
#sudo apt-get install lynx


Run the pkg mgr within octave

echo "pkg install -forge control" | octave
echo "pkg install -forge signal" | octave


For python3, install django

pip3 install Django


Test octave matcher with

cd csd_web_app/Chrm_DTW
octave RunSongPair.m csd_web_app/songs/static/MP3/ub40+Labour_of_Love+06-Red_Red_Wine.mp3 csd_web_app/songs/static/MP3/neil_diamond+Hot_August_Night_Disc_1+10-Red_Red_Wine.mp3


Start django server with

cd csd_web_app
./lrun

