# Operational geospatial data sources

The live case-study workflows query the following sources. Google Earth Engine collections were accessed on **4 August 2026** using project ID `virtual-cycling-502617-j8` (project number `880607990959`). Users reproducing the workflow should supply a Google Earth Engine project to which they are authorized.

| Source | Identifier | Experimental use |
|---|---|---|
| Sentinel-2 SR Harmonized | `COPERNICUS/S2_SR_HARMONIZED` | NDVI and optical surface reflectance |
| SRTM DEM 30 m | `USGS/SRTMGL1_003` | Elevation and slope |
| JRC Global Surface Water | `JRC/GSW1_4/GlobalSurfaceWater` | Surface-water and flood-prone mapping |
| GHSL Population | `JRC/GHSL/P2023A/GHS_POP` | Population and density analysis |
| ESA WorldCover 2021 | `ESA/WorldCover/v200/2021` | Land-cover composition |
| MODIS NDVI | `MODIS/061/MOD13A2` | Vegetation time series |
| FAO GAUL Level 2 | `FAO/GAUL/2015/level2` | Administrative boundaries |
| Hansen Global Forest Change | `UMD/hansen/global_forest_change_2023_v1_1` | Forest cover and loss |
| CHIRPS Daily | `UCSB-CHG/CHIRPS/DAILY` | Precipitation |
| NASA EONET | Official EONET public API | Natural-disaster events; this is not a GEE collection |

## Fixed study areas

- Hanoi AOI: approximately `105.7–106.0°E`, `20.9–21.25°N`.
- Northern Vietnam AOI: `102.5–107.0°E`, `21–23°N`.

The repository contains code and benchmark specifications. Source imagery and other third-party geospatial data remain hosted by their respective providers and are subject to their licenses and terms.
