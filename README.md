#Purpose

* This program turns your Raspberry Pi into a doorbell. It can replace a traditional hardware doorbell, and it integrates with [openHAB](http://www.openhab.org/) and has a number of customization features.

#Features

1. Integration with [openHAB](http://www.openhab.org/) via its [simple HTTP API](https://code.google.com/p/openhab-samples/wiki/Tricks#Use_URL_to_manipulate_items).  Know if your doorbell's been rung and take actions accordingly.

1. Silent mode. It's beneficial for babies or people who act like babies all day when the doorbell interrupts their sleep.

1. Selectable indoor/outdoor sound location (based on stereo channel). Even if it's silent inside, you can make it play outside so that someone doesn't think your doorbell's broken and resort to knocking.

1. Configurable sound. You can go with a traditional sound or pick novelty sounds for holidays, specific guests, UPS delivery, etc.

1. Button timings match a real mechanical doorbell. The software reacts in real time, but there's a (configurable) delay that precedes the playback of the lower-pitch bell.

1. On-the-fly re-load of configuration changes. This makes the configurable sound feature more powerful.


#HOWTO

##What You Need

* Raspberry Pi. (Rev B tested, but any revision should work.)

* A momentary switch.

* A resistor. (The resistance depends on how you wire up your switch.)

* A free GPIO pin.

* Two WAV files.

* At least 7% available CPU on your Pi.

* Basic Linux skills (file copying and editing).

##For all Doorbell Types

1. Wire up a pushbutton on a GPIO pin of your choosing.
    1. There are many different ways to do this. _See online HOWTOs for doing this properly.
    
    1. The code does not enable built-in pulldown or pullup resistors, so you will need to provide your own resistor._

1. Copy the project files and folders to a directory of your choosing on your Raspberry Pi.

1. Edit ```doorbell_config.ini```.

    1. Set ```input_pin``` to the 1-indexed board-centric pin _number_ that you used above, as shown [here](http://www.raspberrypi.org/learning/reaction-game/gpio.png).
    
    1. If your button takes your input pin LOW when pressed, set ```reverse_logic``` to ```True```. Otherwise, set it to ```False```.
    
    1. Set the paths of the WAV files you want to use (or leave them alone to use the default included sounds).

        1. ```ding_soundfile``` will be played on button _press_.
    
        1. ```dong_soundfile``` will be played on button _release_.
    
    1. Set ```noise_location``` to reflect where you want your doorbell sounds to play.

1. In the directory where you copied the project files and directories, run this command:
    ```
    sudo python ./doorbell.py
    ```
1. Press and release the button as you would a normal doorbell.

##For [openHAB](http://www.openhab.org/) Integration

* In [openHAB](http://www.openhab.org/), add a "virtual" doorbell in your ```.items``` file for the doorbell, like so:
```
Switch Button_Front_Doorbell		"Doorbell"		(Outdoor)
```

* Set up any rules you'd like to run when it's pressed and released. Example ```.rules``` entry:
```
rule "Virtual Front Doorbell"
when
	Item Button_Front_Doorbell received command
then
    if(receivedCommand==ON) {
      logInfo("Virtual Front Doorbell", "DING...")
    } else if(receivedCommand==OFF) {
      logInfo("Virtual Front Doorbell", "...DONG")
    }
end
```

* In ```doorbell_config.ini```, edit ```openhab_doorbell_base_URL``` to point to the URL for your virtual doorbell. For example:
```
openhab_doorbell_base_URL:http://bbb1:8080/CMD?Button_Front_Doorbell
```

##Additional Options

* See the comments in ```doorbell_config.ini``` to learn about the other ways you can configure your doorbell.

##For a Traditional Two-Tone Doorbell

1. As above, but create or find two bell tones in WAV format. The 'DING' tone should be 3 half-tones in pitch higher than the 'DONG' tone.

##For a Novelty Doorbell

1. As above, using any two WAV files you like.

###Example Novelty Ideas

* DING: **"somebody's"** DONG: **"at the door"**

    * A larger value for ```dong_delay``` in ```doorbell_config.ini``` is likely necessary, to avoid "at the door" stepping over "somebody's."

* DING: **(a dog barking)** DONG: **(another dog barking)**

* DING: **(spooky Halloween ambient sounds)** DONG: **(random spooky Halloween accent sound)**

    * For the accent sound, write a script that periodically edits ```doorbell_config.ini``` to point ```dong_soundfile``` at a different WAV file.

##Third-Party Extension Ideas

1. Alter ```doorbell_config.ini``` to point to different sounds when different external conditions occur, such as calendar events (keywords, holidays, etc.), times of day.

###Example Third-Party Extension Ideas

* DING: **"Happy"** DONG: **"Easter"**

    * Use a calendar to pick different WAV files and ```dong_delay``` values for ```doorbell_config.ini```.

* DING: **"Hi, [friend's name]."** DONG: **"I'll be right there."**

    * Use [openCV](http://opencv.org/) to do face or license plate recognition, then change ```ding_soundfile``` in ```doorbell_config.ini``` appropriately. Change it all back when done.

* DING: **"Hi. We're asleep right now, so please leave a message after the beep. _BEEP_"** DONG: **(silence)**

####[Boodler](http://boodler.org/)

* [Boodler](http://boodler.org/) is a Python soundscape generator. You could either generate "canned" instances of dynamically-generated soundscapes and switch between them using methods outlined above, or you could extend the software architecture to invoke [Boodler](http://boodler.org/) instead of playing WAV files.

#Questions?

* I'm happy to field any questions in the comments on my corresponding [blog post](http://bob.igo.name/?p=222).
