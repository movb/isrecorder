# iStream HLS output recorder and replayer.

This project aims to help debug and reproduce errors of iStream video streaming server.

  - You can save whole output of 1 HLS channel
  - Replay output

### Version
1.0.0

### Installation

You need Git and python installed:

```sh
$ pip install requests
$ pip install sqlalchemy
$ git clone http://gitlab.netris.ru/m.plekhanov/isrecorder.git
```

### Recoding HLS
```sh
$ python ./isrecorder.py -h                             
usage: isrecorder.py [-h] [-o OUTPUT] [-s SESSION] url   

Istream HLS Session Recorder.                            

positional arguments:                                    
  url                               hls input stream                 

optional arguments:                                      
  -h, --help                        show this help message and exit  
  -o OUTPUT, --output OUTPUT        output folder name               
  -s SESSION, --session SESSION     output session name              
```

For example, if you want to capture url 'https://istreamkz.netris.ru:443/bbc_world.m3u8', you can run:
```sh
$ python ./isrecorder https://istreamkz.netris.ru:443/bbc_world.m3u8
```
By default, it creates folder _sessions_ in current directory and subfolder _session1_ inside.

Press _Ctrl+C_ to stop recording.

### Replaying channel

Now, you can replay whole recorderd HLS output, just as it did istream.
```sh
$ python ./isreplayer.py session1
```
By default, it starts http server on 9090 port, and you can access channel by _http://you_ip:9090/stream.m3u8_.

All options of isreplayer:
```sh
$ python ./isreplayer.py -h                                       
usage: isreplayer.py [-h] [-f FOLDER] [-p PORT] [-o OFFSET] session
 
Istream HLS Session Replayer.                                      

positional arguments:                                              
  session                           recorded session name                      

optional arguments:                                                
  -h, --help                        show this help message and exit            
  -f FOLDER, --folder FOLDER        session folder                             
  -p PORT, --port PORT              listening port (default 9090)              
  -o OFFSET, --offset OFFSET        start offset in seconds                    
```

### Example of HLS output analysis

You can observe saved data in session folder. It contains session.db - a sqlite database with playlists and keys, and chunks directory, where all chunks saved.

There is example python script to find big dellay in chunk updates:
```sh
$  python adjacent_find.py -h                                                  
usage: adjacent_find.py [-h] [-f FOLDER] [-t TIME] [-p PLAYLIST] session       

Istream HLS Session Replayer.                                                  

positional arguments:                                                          
  session                               recorded session name                                  

optional arguments:                                                            
  -h, --help                            show this help message and exit                        
  -f FOLDER, --folder FOLDER            session folder                                         
  -t TIME, --time TIME                  max time delta between consecutive rows (seconds)      
  -p PLAYLIST, --playlist PLAYLIST      playlist name                                          
```

#### Exmaple of using:
```sh
$  python adjacent_find.py -f /mnt/storage/test -t 12 -p test_36_37.m3u8 session1
                                                                                            
                                                                                            
Find time difference 0:00:13.929747                                                         
1268 - 2015-03-05 18:17:35.165488                                                           
#EXTM3U                                                                                     
#EXT-X-VERSION:3                                                                            
#EXT-X-TARGETDURATION:8                                                                     
#EXT-X-MEDIA-SEQUENCE:1468                                                                  
#EXTINF:6.76,                                                                               
http://plekhanov.netris.ru:8554/test/npt=10275.9200-10282.6800_pid=36,37.ts                 
#EXTINF:7.20,                                                                               
http://plekhanov.netris.ru:8554/test/npt=10282.6800-10289.8800_pid=36,37.ts                 
#EXTINF:6.76,                                                                               
http://plekhanov.netris.ru:8554/test/npt=10289.8800-10296.6400_pid=36,37.ts                 
#EXTINF:7.28,                                                                               
http://plekhanov.netris.ru:8554/test/npt=10296.6400-10303.9200_pid=36,37.ts                 
#EXTINF:7.08,                                                                               
http://plekhanov.netris.ru:8554/test/npt=10303.9200-10311.0000_pid=36,37.ts                 
#EXTINF:6.56,                                                                               
http://plekhanov.netris.ru:8554/test/npt=10311.0000-10317.5600_pid=36,37.ts                 
#EXTINF:7.16,                                                                               
http://plekhanov.netris.ru:8554/test/npt=10317.5600-10324.7200_pid=36,37.ts                 
                                                                                            
-------------------------------------------------------------------                         
1274 - 2015-03-05 18:17:49.095235                                                           
#EXTM3U                                                                                     
#EXT-X-VERSION:3                                                                            
#EXT-X-TARGETDURATION:8                                                                     
#EXT-X-MEDIA-SEQUENCE:1470                                                                  
#EXTINF:6.76,                                                                               
http://plekhanov.netris.ru:8554/test/npt=10289.8800-10296.6400_pid=36,37.ts                 
#EXTINF:7.28,                                                                               
http://plekhanov.netris.ru:8554/test/npt=10296.6400-10303.9200_pid=36,37.ts                 
#EXTINF:7.08,                                                                               
http://plekhanov.netris.ru:8554/test/npt=10303.9200-10311.0000_pid=36,37.ts                 
#EXTINF:6.56,                                                                               
http://plekhanov.netris.ru:8554/test/npt=10311.0000-10317.5600_pid=36,37.ts                 
#EXTINF:7.16,                                                                               
http://plekhanov.netris.ru:8554/test/npt=10317.5600-10324.7200_pid=36,37.ts                 
#EXTINF:7.08,                                                                               

```