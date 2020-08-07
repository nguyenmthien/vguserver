# vguserver
A VGU-funded project to monitor its main server room remotely.

## Overall descriptions
The system is responsible for monitoring ambient data of the server room in several sampling points and other critical server room status, such as power condition.
Remote monitoring, including changing the isolated air conditioner in the room can be done via an mobile phone application. 
This system uses the Raspberry Pi as the main processor, and several ESP8266 microcontroller boards for data gathering. 
Communication with the Android application is powered by the Blynk IoT platform.


## Installation
You can download this project directly via the GitHub web link, or clone using git:

```bash
git clone https://github.com/nguyenmthien/vguserver/
```

For setting up the Python environment, the Kivy environment, the UART connection to the Raspberry Pi UPS and the Blynk server, please see the README file in /pi.

### Requirements
 - [Python 3](https://python.org/)
 - [Kivy](https://kivy.org/)

      ```bash
      python -m pip install --user kivy
      ```

## Usage

```bash
python main.py
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.


## Special thanks to
 - The Python community, especially the [Python Documentation](https://docs.python.org/)
 - The [Kivy](https://kivy.org/) community
 - The [Blynk](https://blynk.io/) community, especially the [Blynk Python Library community](https://github.com/blynkkk/lib-python)


## License
[MIT](https://choosealicense.com/licenses/mit/)
