COMP 4304 Assignment 5
Marty Whelan 201257227
Jesse Hanlon 201738838


Description of what we got working:

For this assignment, our goal was to select the best section of the build area to build our settlement, and start to place the foundations for our buildings. We set the size of the settlement to be 128x128 (able to be modified later if necessary), and sliced the build area into sections of this size. Each section was given a rating based on flatness, quantity of water, and terrain type. We also began to determine the placement of large and small houses by seperating the desired settlement area into sections and rated them to determine which would best hold the building depending on flatness and water presence, choosing to select one placement from a list of optimal placements, making sure no overlaps occur. We then placed the foundation of these buildings.

The lapis blocks are the housing plots, the mushrooms indicate the outline of the area chosen to settle.
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
3. Launch a new world in creative mode
4. Once in the world, teleport to 0, 128, 0
5. In a terminal, run the script "housing.py"
6. Watch generation

# Contributors

