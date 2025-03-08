```js
import {loadDepartmentGeom, loadDepartmentLevel, loadDepartmentEvol} from "./components/loaders.js";
import {getConfig} from "./components/config.js";
import {transformData} from "./components/build-table.js";
import {getCentroid} from "./utils/fonctions.js";
import {getOSM, getOSMDark, getMarker, getSatelliteImages, getPredictions, getClusters, getEvolutions} from "./components/map-layers.js";
import {filterObject} from "./components/utils.js";
```

```js
// Crée un élément h1 avec le nom du département
const titre = html`<h1>Buildings </h1>`;
display(titre);
```


```js
const nuts3 = FileAttachment("./data/nuts3.json").json()
const statNuts3 = FileAttachment('./data/statNuts3.parquet').parquet()
const available_years = ['2018','2021','2024']
const available_nuts = ['BE100','BE251','FRK26','FRJ27']
```


```js
const years_select = view(Inputs.form({
  year_start : Inputs.select(available_years, {value: available_years[0], label: "start"}),
  year_end : Inputs.select(available_years, {value: available_years[1], label: "end"})
},
 {
    template: (formParts) => htl.html`
     <div>
       <div style="
         width: 400px;
         display: flex;
         gap: 10px;
       ">
         ${Object.values(formParts)}
       </div>
     </div>`
  }
))
```
```js
const placeholder_nuts = "BE100"
const search = view(
     Inputs.search(statNuts3, 
     {
       placeholder: placeholder_nuts,
       columns:["NUTS3"]
     })
   )
```
```js
const search_table = view(
    Inputs.table(search, {
        columns: ["NUTS3", "artificial+", "artificial-", "artificial_net", "NDVI+", "NDVI-", "NDVI_net"]
    })
);
```
```js
const center = getCentroid(
    nuts3,
    search[0]?.NUTS3||placeholder_nuts ,
  )
```

```js
const year_start = years_select["year_start"]
const year_end = years_select["year_end"]
```

```js
// Initialisation de la carte Leaflet
const mapDiv = display(document.createElement("div"));
mapDiv.style = "height: 600px; width: 100%; margin: 0 auto;";

// Initialiser la carte avec la position centrale du département
const map = L.map(mapDiv, {
            center: center,
            zoom: 10,           
            maxZoom: 21 //(or even higher)
        });

// Adding the WMS layer
const CLCplus2018 = L.tileLayer.wms("https://copernicus.discomap.eea.europa.eu/arcgis/services/CLC_plus/CLMS_CLCplus_RASTER_2018_010m_eu/ImageServer/WMSServer?", {
    layers: "CLMS_CLCplus_RASTER_2018_010m_eu",
    format: "image/png",
    transparent: true,
    version: "1.3.0",
    opacity: 0.5, 
    attribution: "© Copernicus CLC+ 2018 - European Environment Agency"
});

const CLCplus2021 = L.tileLayer.wms("https://copernicus.discomap.eea.europa.eu/arcgis/services/CLC_plus/CLMS_CLCplus_RASTER_2021_010m_eu/ImageServer/WMSServer?", {
    layers: "CLMS_CLCplus_RASTER_2021_010m_eu",
    format: "image/png",
    transparent: true,
    version: "1.3.0",
    opacity: 0.5, 
    attribution: "© Copernicus CLC+ 2021 - European Environment Agency"
});
// Add WMS layer to map

// Ajout d'une couche de base OpenStreetMap
const OSM = getOSM();
const OSMDark  = getOSMDark();
const marker = getMarker(center);
const BORDERS = getClusters(nuts3);

const Sentinel2 = getSatelliteImages();
const selectedSentinel2 = filterObject(Sentinel2, [`Sentinel2 ${year_start}`, `Sentinel2 ${year_end}`,])


OSM['OpenStreetMap clair'].addTo(map);
BORDERS["nuts boundaries"].addTo(map);


const urlGeoServer = "https://geoserver-hachathon2025.lab.sspcloud.fr/geoserver/hachathon2025/wms";
const workSpace = "hachathon2025";

const differences = L.tileLayer.wms(urlGeoServer, {
    layers: `${workSpace}:change_polygons_CLC`,
    format: 'image/png',
    transparent: true,
    version: '1.1.0',
    opacity: 1,
    maxZoom: 21,
    styles : "style_multiclass",
   // CQL_FILTER: "INCLUDE",
  //  cql_filter: `class='3'`  
});

marker.addTo(map);
```

```js
 L.control.layers({
   ...OSM,
   ...OSMDark,  
   },
{ ...selectedSentinel2,
  differences,
 [`CLC+ ${year_start}`]: CLCplus2018,
  [`CLC+ ${year_end}`]: CLCplus2021,
}
).addTo(map);

```