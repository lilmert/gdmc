# gdmc
Memorial's COMP 4303 Final Project &amp; submission to the 2021 GDMC Competition

# To Do Assignment 5

## Assess the build area

### Evaluate the chunks

16 by 16 grid of information

* Water
  * Determines how much water is on the surface of the chunk
* Flatness
  * Determines how flat or unflat a the chunk surface is
* Surface Objects
  * Determines how many objects are on the surface of the chunk
    * Flowers
    * Trees
    * Other?

### Identify the best cross-section of the build area

Evaluate the chunk grid in the given build area and determine the strip
of chunks that is best suited for a village.

The best strip will contain
  * Some water, but not overwhelming amount
  * As flat as possible
  * Limited surface obstruction

### Start building surface area objects in a "logically historic" manner

1. Beging with "Town Center"
2. Surrounding housing
3. Farm land
4. Market area
5. ????

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
git clone https://github.com/nilsgawlik/gdmc_http_client_python .
```

# Running

1. Open your authenticated Minecraft installation with the `forge` version loaded
2. Select from the mods panel the `GDMC HTTP Interface`
3. Start up a new minecraft world
4. Once in the world, set your build area to the current location of your player via `/setbuildarea` (???)
5. In a terminal, run .......?
6. Watch the terrain generate

# Contributors

<<<<<<< HEAD
< To be completed >

=======
* [Marty Whelan](https://github.com/lilmert)
* [Jesse Hanlon](https://github.com/jessehanlon)
>>>>>>> 2c831077d1a9e66ff8cb0b264cf6995c2349822a
