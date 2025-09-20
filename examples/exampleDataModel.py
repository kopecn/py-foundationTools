from dataModelHelpers.commonTypes.GeoCoordinate import GeoCoordinate
from pathlib import Path


if __name__ == "__main__":
    aCoordfile = Path.home().joinpath("acoord.json")

    # Create and save a coord
    geoCoord = GeoCoordinate(3.1, 2.3)
    geoCoord.saveToFile(aCoordfile)

    # load and validate the coord
    reloadedCoord = GeoCoordinate.loadFromFile(aCoordfile)
    print(reloadedCoord)

    if aCoordfile.exists() and aCoordfile.is_file():
        aCoordfile.unlink()
