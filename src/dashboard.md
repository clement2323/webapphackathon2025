```js
import {loadDepartmentGeom, loadDepartmentLevel, loadDepartmentEvol} from "./components/loaders.js";
import {getConfig} from "./components/config.js";
import {transformData} from "./components/build-table.js";
import {getIlotCentroid} from "./utils/fonctions.js";
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

// const geom = await loadDepartmentGeom(department);
// const level = await loadDepartmentLevel(department);
// const evol = await loadDepartmentEvol(department);
const available_years = ['2018','2021']
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
const year_start = years_select["year_start"]
const year_end = years_select["year_end"]
//const data_select = transformData(evol, level, year_start, year_end);
```

```js
 //récupération du centre de l'ilot à partir de l'ilot sélectionné
const placeholder_nuts = available_nuts[0]
 ```

 ```js
//  const search = view(
//       Inputs.search(data_select, 
//       {
//         placeholder: placeholder_nuts,
//         columns:["depcom_2018","code"]
//       })
//     )
```

```js
    // const search_table = view(
    //   Inputs.table(search, {
    //     columns: ['depcom_2018', 'code', `aire_${year_end}`, `pourcentage_bati_${year_end}`, 'evol_abs', 'evol_rela'],
    //     header: {
    //       depcom_2018: 'Code Commune',
    //       code: 'Code Îlot',
    //       [`aire_${year_end}`]: `Surface ${year_end} (m²)`,
    //       [`pourcentage_bati_${year_end}`]: `Bâti ${year_end} (%)`,
    //       evol_abs: 'Écart absolu (m²)',
    //       evol_rela: 'Écart relatif (%)'
    //     },
    //     width: {
    //       depcom_2018: 120,
    //       code: 100,
    //       [`aire_${year_end}`]: 120,
    //       [`pourcentage_bati_${year_end}`]: 90,
    //       evol_abs: 120,
    //       evol_rela: 120
    //     },
    //     format: {
    //       [`aire_${year_end}`]: x => Math.round(x),
    //       [`pourcentage_bati_${year_end}`]: x => Math.round(x),
    //       evol_abs: x => Math.round(x),
    //       evol_rela: x => (Math.round(x * 10) / 10)
    //     },
    //     sort: {
    //       column: 'depcom_2018',
    //       reverse: false
    //     },
    //     rows: 10
    //   })
    // )
```

<!-- 
## Analyse des îlots

```js
const center = getIlotCentroid(
    geom,
    search[0]?.depcom_2018 || placeholder_commune,
    search[0]?.code || placeholder_ilot
  )
console.log(center)
``` -->
```js
// Initialisation de la carte Leaflet
const mapDiv = display(document.createElement("div"));
mapDiv.style = "height: 600px; width: 100%; margin: 0 auto;";
const center = [50.850346, 4.351721];
  
// Initialiser la carte avec la position centrale du département
const map = L.map(mapDiv, {
            center: center,
            zoom: 17,           
            maxZoom: 21 //(or even higher)
        });

// Ajout d'une couche de base OpenStreetMap
const OSM = getOSM();
const OSMDark  = getOSMDark();
const marker = getMarker(center);
const BORDERS = getClusters(nuts3);

const Sentinel2 = getSatelliteImages();
const selectedSentinel2 = filterObject(Sentinel2, [`Sentinel2 ${year_start}`, `Sentinel2 ${year_end}`,])

OSM['OpenStreetMap clair'].addTo(map);
BORDERS["nuts boundaries"].addTo(map);

marker.addTo(map);
```

```js
 L.control.layers({
   ...OSM,
   ...OSMDark,  
   },
{ ...selectedSentinel2}
//   { ...selectedPleiades,
//   [`Bâtiments ${year_start}`]: buildingLayerStart,
//   [`Bâtiments ${year_end}`]: buildingLayerEnd,
//   }
).addTo(map);

// // Définition des labels et couleurs
// const legendItems = [
//   {name: "Batiment", color: "rgb(206, 112, 121)"},
//   {name: "Zone imperméable", color: "rgb(166, 170, 183)"},
//   {name: "Zone perméable", color: "rgb(152, 119, 82)"},
//   {name: "Piscine", color: "rgb(98, 208, 255)"},
//   {name: "Serre", color: "rgb(185, 226, 212)"},
//   {name: "Sol nu", color: "rgb(187, 176, 150)"},
//   {name: "Surface eau", color: "rgb(51, 117, 161)"},
//   {name: "Neige", color: "rgb(233, 239, 254)"},
//   {name: "Conifère", color: "rgb(18, 100, 33)"},
//   {name: "Feuillu", color: "rgb(76, 145, 41)"},
//   {name: "Coupe", color: "rgb(228, 142, 77)"},
//   {name: "Brousaille", color: "rgb(181, 195, 53)"},
//   {name: "Pelouse", color: "rgb(140, 215, 106)"},
//   {name: "Culture", color: "rgb(222, 207, 85)"},
//   {name: "Terre labourée", color: "rgb(208, 163, 73)"},
//   {name: "Vigne", color: "rgb(176, 130, 144)"},
//   {name: "Autre", color: "rgb(34, 34, 34)"}
// ];

// // Créer les couches individuelles pour chaque classe
// const predictionLayers = {};
// legendItems.forEach((item, index) => {
//   const layerName = `${item.name}`;
//   const layer = L.tileLayer.wms(selectedPredictions[`Prédictions ${year_end}`]._url, {
//     ...selectedPredictions[`Prédictions ${year_end}`].options,
//     cql_filter: `label='${index+1}'`  // index correspond maintenant au bon label
//   });
//   predictionLayers[layerName] = layer;
// });

// // Ajouter le marqueur à la carte
// marker.addTo(map);

// // Création de la légende à gauche avec texte noir
// const legend = htl.html`
//   <div class="legend" style="
//     position: absolute;
//     bottom: 20px;
//     left: 20px;
//     background: rgba(255, 255, 255, 0.9);
//     padding: 10px;
//     border-radius: 5px;
//     box-shadow: 0 0 10px rgba(0,0,0,0.1);
//     z-index: 1000;
//     max-height: 70vh;
//     overflow-y: auto;
//     color: black;  /* Texte en noir */
//   ">
//     <h4 style="margin: 0 0 10px 0; color: black;">Légende ${year_end}</h4>
//     ${legendItems.map(item => htl.html`
//       <div style="display: flex; align-items: center; margin-bottom: 5px">
//         <div style="
//           width: 18px;
//           height: 18px;
//           background: ${item.color};
//           margin-right: 8px;
//           opacity: 0.7;
//           border-radius: 3px;
//         "></div>
//         <span style="color: black;">${item.name}</span>
//       </div>
//     `)}
//   </div>
// `;

// // Deuxième contrôle : couches de prédiction individuelles avec titre
// const predictionDetailControl = L.control.layers(null, predictionLayers, {
//   position: 'topright',
//   collapsed: true
// }).addTo(map);

// // Ajout d'un titre au contrôle
// const predictionControlDiv = predictionDetailControl.getContainer();
// const title = L.DomUtil.create('div', 'prediction-control-title');
// title.innerHTML = `<h4 style="
//   margin: 0 0 8px 0;
//   padding: 0;
//   color: black;
//   font-size: 14px;
// "> labels ${year_end}</h4>`;
// predictionControlDiv.insertBefore(title, predictionControlDiv.firstChild);

// // Ajout de la légende à la carte
// mapDiv.appendChild(legend);
// ```