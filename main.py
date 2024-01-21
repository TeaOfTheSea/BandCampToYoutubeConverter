import os
from pydub import AudioSegment

def main():
    #Get current working directory and files therin
    cwd = os.getcwd()
    files = os.listdir()

    #Populate array of covers and music
    covers = []
    music = []
    lastArtist = ""#Bandcamp releases can have multiple artists so while we are looping through the music we check if there are more than one here
    allSameName = True
    for file in files:
        stream = os.popen("file \'"+cwd+"/"+file+"\'")
        fileinfo = stream.read()
        if "image" in fileinfo:
            covers.append(file)
        elif "audio" in fileinfo:
            if lastArtist == "":
                lastArtist = file[:file.find("-")-1]
            elif lastArtist != file[:file.find("-")-1]:
                allSameName = False
            music.append(file)
        else:
            print("WARNING: \'" + file + "\' is a weird file!")

    #check for any extra dashes in the file name before using the dashes as a delimeter
    dashindex = 2
    if music[0].count("-") > 2:
        print("Extra dashes were found in filenames, which dash should be used to find the track number?")
        dashindex = int(input(""))

    #Sort music list before we make the video or tracklist for hopefully obvious reasons
    music = quicksort(music, dashindex)

    with open(cwd+"/tracklist.txt", 'w') as tracklist:
        for track in music:
            tracklist.write("file \'"+cwd+"/"+track+"\'\n")
            
    #Combine all of the audio files
    stream = os.popen("ffmpeg -f concat -safe 0 -i tracklist.txt -c copy concat.wav")
    log = stream.read()
    print(log)

    #Select a cover image
    cover = ""
    if len(covers)>1:
        print("More than one cover image was found.\n Which of the following would you like to bake into the video?")
        for i in range(len(covers)):
            print("["+str(i)+"]"+"\t"+covers[i])
        selection  = int(input(""))
        cover = covers[selection]
    else:
        cover = covers[0]

    #Apply a cover image
    stream = os.popen("ffmpeg -framerate 1 -loop 1 -i \'" + cwd + "/" + cover + "\' -i \'" + cwd + "/concat.wav\' -shortest output.avi")
    log = stream.read()
    print(log)

    #Create the timestamps
    print("\nTimestamps")
    totalTime= 0
    for track in music:
        title = ""
        if allSameName == False:
            title = track[:track.find("-")-1]+" - "
        index = 0
        for i in range(0,2): #Find the second index of "-"
            index = track.find("-", index+1) + 5
        title = title + track[index:-4]
        print(formatDuration(totalTime)+"\t"+title)
        totalTime += getWavLength(cwd+"/"+track)

    #Remove everything but the final video
    os.remove(cwd+"/concat.wav")
    os.remove(cwd+"/tracklist.txt")

def quicksort(arr, dashindex):
    if len(arr) <= 1:
        return arr
    else:
        pivot = arr[0]
        pivotValue = getTrackNumber(arr[0], dashindex)
        less = [x for x in arr[1:] if getTrackNumber(x, dashindex) <= pivotValue]
        greater = [x for x in arr[1:] if getTrackNumber(x, dashindex) > pivotValue]
        return quicksort(less, dashindex) + [pivot] + quicksort(greater, dashindex)

def getTrackNumber(file, dashindex):
    index = 0
    for i in range(0, dashindex): #Find the second index of "-"
        index = file.find("-", index+1)
    return int(file[index+2:index+4]) #Using the index of the second index of the dash, we know where the track number is.

def getWavLength(file_path):
    return len(AudioSegment.from_file(file_path)) / 1000.0  # Duration in seconds

def formatDuration(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)

    if hours > 0:
        return f"{int(hours)}:{str(int(minutes)).zfill(2)}:{str(int(seconds)).zfill(2)}"
    else:
        return f"{str(int(minutes)).zfill(2)}:{str(int(seconds)).zfill(2)}"

if __name__ == "__main__":
    main()
