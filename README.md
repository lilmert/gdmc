# gdmc
Minecraft Generative Design Project

![Screenshot](screenshot.png)

# Installation

## Dependency

* [Download the Forge Mod Loader](https://files.minecraftforge.net/)
* Install the forge mod loader via the jar
* Open Minecraft with the installed Forge Mod
* Navigate to the Mods panel and click "Open Mods Folder"
* Download the jar file from [here](https://github.com/nilsgawlik/gdmc_http_interface/releases/tag/v0.3.1) and place it in the mod folder
* Restart Minecraft and launch the Forge Installation again. The mod should now appear in the mod list under "Mods".
* When you open a world the HTTP Server will be started automatically, and you should now be able to send HTTP requests to it

## Setup

```bash
git clone https://github.com/lilmert/gdmc
cd gdmc
pip3 install -r requirements.txt
```

After running the above commands and installing the required dependencies,
you'll have everything you need to run the project. From here, the following
are your options...

1. Open Minecraft with the forge mod launcher
2. Launch a single player creative world

# Running

1. Open your authenticated Minecraft installation with the `forge` version loaded
2. Select from the mods panel the `GDMC HTTP Interface`
3. Start up a new minecraft world
4. Once in the world, set your build area to the current location of your player via `/setbuildarea` (???)
5. In a terminal, run........

For running the generation you have 2 options

* Pass command line args to the program representing the x and z values of the
  origin along with the size of the settling area.
  * eg: `python3 main.py 193 181 128`
    * x = 193
    * z = 181
    * size = 128x128
* Accept the default parameters which are x=0, z=0, size=128x128

Running the project options

* `python3 main.py 13 15 128`
* `python3 main.py` (will use 0, 0, 128)

6. Watch the terrain generate

# Contributors

* [Marty Whelan](https://github.com/lilmert)
* [Jesse Hanlon](https://github.com/jessehanlon)
