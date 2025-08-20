

# WDPAPI DebugTool 运行命令

## 1. 场景相机

### 1.1 相机模式/位置/限制设置

#### 设置相机模式

```json
{
    "apiClassName": "WdpCameraControlAPI",
    "apiFuncName": "SetCameraMode",
    "args": {
        "controlMode": "FPS"
    }
}
```

### 1.2 相机与实体行为

#### 相机聚焦到坐标点

```json
{
    "apiClassName": "WdpCameraControlAPI",
    "apiFuncName": "FocusToPosition",
    "args": {
        "targetPosition": [0, 0, 0],
        "rotation": {
            "pitch": -30,
            "yaw": 0
        },
        "distance": 10,
        "flyTime": 1
    }
}
```

#### 获取当前相机的信息

得到相机经纬度坐标位置，视角朝向等信息

```json
{
    "apiClassName": "WdpCameraControlAPI",
    "apiFuncName": "GetCameraInfo",
    "args": {
    }
}
```

#### 设置相机的经纬度坐标

```json
{
    "apiClassName": "WdpCameraControlAPI",
    "apiFuncName": "SetCameraPose",
    "args": {
        "location": [103.59140494959958, 31.017364990195702, 1229.4700123759205],
        "rotation": {
            "pitch": 0,
            "yaw": 0
        },
        "flyTime": 0
    }
}
```

## 2. 实体覆盖物

### 2.1 POI点位操作

#### POI打点

```json
{
    "apiClassName": "WdpSceneAPI",
    "apiFuncName": "CreateEntities",
    "args": {
        "createEntityParams": [
            {
                "EntityType": "PoiEntity",
                "BasicInfoAtom": {
                    "entityName": "myName1",
                    "customId": "myId1",
                    "customData": "{\"data\":\"myCustomData\"}"
                },
                "TransformAtom2D": {
                    "location": [
                        121.52400833,
                        31.19254757,
                        56
                    ]
                },
                "PoiEntityAtom": {
                    "markerNormalUrl": "http://wdpapi.51aes.com/doc-static/images/static/markerNormal.png",
                    "markerActivateUrl": "http://wdpapi.51aes.com/doc-static/images/static/markerActive.png",
                    "markerSize": [100, 228],
                    "labelBgImageUrl": "http://wdpapi.51aes.com/doc-static/images/static/LabelBg.png",
                    "labelBgSize": [200, 50],
                    "labelBgOffset": [50, 200],
                    "labelContent": [" 文本内容A", "fe587aff", "24"],
                    "labelContentOffset": [10, 20]
                }
            }
        ],
        "operations": {
            "calculateCoordZ": {
                "coordZRef": "surface",
                "coordZOffset": 50
            }
        }
    }
}
```

#### 点选放置POI点

```json
{
    "apiClassName": "WdpActionManagerAPI",
    "apiFuncName": "RunAction",
    "args": {
        "actionName": "PlacePOIAction",
        "actionParams": {
            "name": "123",
            "snapMode": "Surface",
            "markerVisible": true,
            "markerNormalUrl": "http://wdpapi.51aes.com/doc-static/images/static/markerNormal.png",
            "markerActivateUrl": "http://wdpapi.51aes.com/doc-static/images/static/markerActive.png",
            "markerSize": [100, 228],
            "labelBgImageUrl": "http://wdpapi.51aes.com/doc-static/images/static/LabelBg.png",
            "labelBgSize": [200, 50],
            "labelBgOffset": [50, 200],
            "labelContent": [" 文本内容A", "fe587aff", "24"],
            "labelContentOffset": [10, 20]
        }
    }
}
```

### 2.2 路径操作

#### 创建路径Path

```json
{
    "apiClassName": "WdpSceneAPI",
    "apiFuncName": "CreateEntities",
    "args": {
        "createEntityParams": [
            {
                "EntityType": "BP_PathEntity_C",
                "BasicInfoAtom": {
                    "entityName": "myName1",
                    "customId": "myId1",
                    "customData": "{\"data\":\"myCustomData\"}"
                },
                "PathEntityAtom": {
                    "type": "arrow",
                    "width": 16,
                    "color": "ff8a2a",
                    "passColor": "0a4bff"
                },
                "PolylineAtom": {
                    "coordinates": [
                        [121.93684819200513, 30.899377036157219, 0],
                        [121.93613052572492, 30.899128660962887, 0],
                        [121.93609372902178, 30.899865532716987, 0],
                        [121.93695748517804, 30.899855298006866, 0]
                    ]
                }
            }
        ],
        "operations": {
            "calculateCoordZ": {
                "coordZRef": "surface",
                "coordZOffset": 8
            }
        }
    }
}
```

## 3. 底板图层操作

### 3.1 AES底板图层操作

#### 设置图层显隐

隐藏地形

```json
{
    "apiClassName": "AesTilesAPI",
    "apiFuncName": "SetLayersVisibility",
    "args": {
        "layers": ["terrain"],
        "bVisible": false,
        "aesTilesEid": "-9151314294491913630"
    }
}
```

隐藏建筑

```json
{
    "apiClassName": "AesTilesAPI",
    "apiFuncName": "SetLayersVisibility",
    "args": {
        "layers": ["building"],
        "bVisible": false,
        "aesTilesEid": "-9151314294491913630"
    }
}
```

隐藏路网

```json
{
    "apiClassName": "AesTilesAPI",
    "apiFuncName": "SetLayersVisibility",
    "args": {
        "layers": ["road"],
        "bVisible": false,
        "aesTilesEid": "-9151314294491913630"
    }
}
```

隐藏水域

```json
{
    "apiClassName": "AesTilesAPI",
    "apiFuncName": "SetLayersVisibility",
    "args": {
        "layers": ["water"],
        "bVisible": false,
        "aesTilesEid": "-9151314294491913630"
    }
}
```

### 3.2 工程底板单体操作

#### 设置人工摆放单体对象的显隐、描边、高亮

对象显隐效果

```json
{
    "apiClassName": "AesTilesNodeAPI",
    "apiFuncName": "SetNodesVisibility",
    "args": {
        "nodes": ["74064", "74065"],
        "bVisible": false,
        "aesTilesEid": "-1905392284"
    }
}
```

对象亮边效果

```json
{
    "apiClassName": "AesTilesNodeAPI",
    "apiFuncName": "SetNodesOutline",
    "args": {
        "nodeIds": ["74064", "74065"],
        "bOutline": true,
        "styleName": "Default",
        "aesTilesEid": "-1905392284"
    }
}
```

对象高亮效果

```json
{
    "apiClassName": "AesTilesNodeAPI",
    "apiFuncName": "SetNodesHighlight",
    "args": {
        "nodeIds": ["150"],
        "bHighlight": true,
        "styleName": "Default",
        "aesTilesEid": "-1905392284"
    }
}
```

## 4. 功能组件

### 4.1 环境设置

#### 场景光照

获取时间

```json
{
    "apiClassName": "WdpEnvironmentAPI",
    "apiFuncName": "GetSkylightTime",
    "args": {
    }
}
```

设置时间

```json
{
    "apiClassName": "WdpEnvironmentAPI",
    "apiFuncName": "SetSkylightTime",
    "args": {
        "skylightTime": "12:30",
        "durationSeconds": 1.2000000476837158,
        "bRealtime": false
    }
}
```

#### 场景天气

获取天气

```json
{
    "apiClassName": "WdpEnvironmentAPI",
    "apiFuncName": "GetSceneWeather",
    "args": {
    }
}
```

设置天气

```json
{
    "apiClassName": "WdpEnvironmentAPI",
    "apiFuncName": "SetSceneWeather",
    "args": {
        "sceneWeather": "Sunny",
        "durationSeconds": 1.2000000476837158,
        "bRealtime": false
    }
}
```

#### 场景风格化

设置场景风格样式

```json
{
    "apiClassName": "SetSceneStyleAPI",
    "apiFuncName": "SetSceneStyle",
    "args": {
        "style": "comic"
    }
}
```

### 4.2 工具类API

#### CAD坐标转经纬度坐标

创建CAD地理参考

```json
{
    "apiClassName": "WdpCoordinateAPI",
    "apiFuncName": "CreateCADGeoRef",
    "args": {
        "cadPoints": [[0, 0, 0]],
        "worldPoints": [[0, 0, 0]]
    }
}
```

本地坐标转全局坐标（需要先运行上面的CreateCADGeoRef获取geoRefEid）

```json
{
    "apiClassName": "WdpCoordinateAPI",
    "apiFuncName": "LocalToGlobalGeoRef",
    "args": {
        "geoRefEid": "0",
        "from": [[0, 0, 0]]
    }
}
```

#### 笛卡尔坐标转GIS坐标

```json
{
    "apiClassName": "WdpCoordinateAPI",
    "apiFuncName": "CartesianToGIS",
    "args": {
        "from": [[-291554.248540, -338994.727828, 30570.326238]]
    }
}
```

#### 取点工具

开启取点工具

```json
{
    "apiClassName": "WdpPickPointAPI",
    "apiFuncName": "StartPickPoint",
    "args": {
        "coordinateShow": true,
        "iconShow": true,
        "coordZRef": "Altitude"
    }
}
```

获取坐标点

```json
{
    "apiClassName": "WdpPickPointAPI",
    "apiFuncName": "GetPickedPoints",
    "args": {
        "coordZRef": "Altitude"
    }
}
```

关闭取点工具

```json
{
    "apiClassName": "WdpPickPointAPI",
    "apiFuncName": "EndPickPoint",
    "args": {
    }
}
```

## 5. 3DTiles操作

### 5.1 加载操作

加载3DTiles

```json
{
    "apiClassName": "GeoLayerAPI",
    "apiFuncName": "CreateGeoLayerEntity",
    "args": {
        "geoLayerUrl": "http://14.103.8.151:30051/gis/MYSK_3DT022506/tileset.json",
        "geoLayerType": "3DTiles",
        "geoLayerParams": {
            "serviceLayerName": "",
            "featureType": "Polygon",
            "needGCJOffset": false,
            "batchFeatureNum": 4000
        },
        "geoFeatureStyle": {
            "filterColor": "ffffffff",
            "styleDesc": "",
            "bBasedOnTerrain": false,
            "polygonStyle": {
                "filledColor": "ffffffff",
                "bOutline": false,
                "outlineColor": "ffffffff",
                "outlineWidth": 1,
                "bExtrude": false,
                "extrudeHeight": 100,
                "extrudeHeightField": "Elevation"
            },
            "lineStyle": {
                "lineColor": "ffffffff",
                "lineWidth": 1,
                "lineShape": "Plane"
            },
            "pointStyle": {
                "pointColor": "ffffffff",
                "pointSize": 5,
                "pointShape": "Circle"
            }
        },
        "geoLayerSymbol": {
            "symbolField": "",
            "symbolScheme": "",
            "geoFeatureSymbolArray": []
        },
        "geoLayerOperation": {
            "tile_MaximumScreenSpaceError": 8
        }
    }
}
```

### 5.2 变换操作

旋转3DTiles

```json
{
    "apiClassName": "GeoLayerAPI",
    "apiFuncName": "SetGeoLayerRotation",
    "args": {
        "eid": "-9151314275211419539",
        "geoLayerIndex": 0,
        "GeoLayerRotation": [1, 0, 0]
    }
}
```