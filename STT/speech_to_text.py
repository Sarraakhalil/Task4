import json
from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import pyaudio
import wave
from ibm_watson import TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from playsound import playsound
import os
chunk = 1024  # Record in chunks of 1024 samples
sample_format = pyaudio.paInt16  # 16 bits per sample
channels = 2
fs = 44100  # Record at 44100 samples per second
seconds = 5

filename = "output.wav"
num = 0
while True:
    p = pyaudio.PyAudio()  # Create an interface to PortAudio

    print('Recording')

    stream = p.open(format=sample_format,channels=channels,rate=fs,frames_per_buffer=chunk,input=True)

    frames = []  # Initialize array to store frames
    res = ""
    auth = IAMAuthenticator("CFmU96qbA78RAT8M_34hATG1ox6iwV9KSWnlbEMSHCKh")
    service = SpeechToTextV1(authenticator=auth)
    service.set_service_url("https://api.eu-gb.speech-to-text.watson.cloud.ibm.com/instances/e5f160d8-a481-4ad9-955a-2fec0e5caf8c")

    # Store data in chunks for 3 seconds
    for i in range(0, int(fs / chunk * seconds)):
        data = stream.read(chunk)
        frames.append(data)
        #tmp = str(service.recognize(b''.join(frames),content_type='audio/l16;rate=44100')).replace("inline; filename=\"result.json\"", "")
        #print(json.loads(tmp).get("result").get("results"))

    # Stop and close the stream 
    stream.stop_stream()
    stream.close()
    # Terminate the PortAudio interface
    p.terminate()

    print('Finished recording')

    # Save the recorded data as a WAV file
    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()
    with open(filename,'rb') as audio_file:
            tmp = str(service.recognize(audio_file,content_type='audio/wav')).replace("inline; filename=\"result.json\"", "")
            res = json.loads(tmp).get("result").get("results")[0].get('alternatives')[0].get("transcript")
            res = res[0:len(res)-1]
            print("You said:"+res)
            with open("res.txt",'a') as r:
                r.write(res + "\n")
    dic_req = {
        0:"how are you",
        1:"i want to evaluate this place",
        2:"good",
        3:"bad",
        4:"hello"
           }
    dic_reply = {
        0:"Iam fine thanks",
        1:"please say good or bad",
        2:"good evaluation thanks",
        3:"bad evaluation",
        4:"hello"
           }
    rep = ""
    flag = False
    for k,v in dic_req.items():
        if res.lower() == v:
            rep = dic_reply[k]
            flag = True
            

    if flag == False:
        rep = "Good bye"
    auth = IAMAuthenticator("mlLo5NqFdPuEd-3oh_M84fUAzj5hxbL5T_d08x7wBwp5")
    service = TextToSpeechV1(authenticator=auth)
    service.set_service_url("https://api.eu-gb.text-to-speech.watson.cloud.ibm.com/instances/aceb0741-1bfb-46de-95a2-17fd2012369d")
    if rep != "Good bye":
        with open("reply"+str(num)+".mp3",'wb') as audio_file:
                res = service.synthesize(rep,accept="audio/mp3",voice="en-US_AllisonV3Voice").get_result()
                audio_file.write(res.content)
        playsound('reply'+str(num)+'.mp3')     
    os.remove("output.wav")
    num= num+1
    if rep == "Good bye":
        break

